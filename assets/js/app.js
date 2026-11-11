/* Arc d'Iris — panneau d'accessibilité, défilement, lecture à voix haute, navigation aux flèches */
(function () {
  'use strict';

  var CLE = 'arc-iris-prefs';
  var racine = document.documentElement;

  // ---------- Préférences ----------
  // Chaque réglage correspond à un attribut data-* sur <html>.
  var DEFAUTS = { couleurs: 'arc', contraste: 'non', taille: '1', police: 'normal', espace: 'normal', mouvement: 'normal', cote: 'droite', zones: 'normal', fleches: 'non' };

  function lire() {
    try { return JSON.parse(localStorage.getItem(CLE) || '{}'); } catch (e) { return {}; }
  }
  function ecrire(p) {
    try { localStorage.setItem(CLE, JSON.stringify(p)); } catch (e) { /* ignoré */ }
  }
  function valeurActuelle(cle) {
    var v = racine.getAttribute('data-' + cle);
    if (v) return v;
    if (cle === 'contraste') return 'non';
    return DEFAUTS[cle];
  }
  function appliquer(cle, valeur) {
    var p = lire();
    if (valeur === DEFAUTS[cle]) { delete p[cle]; racine.removeAttribute('data-' + cle); }
    else { p[cle] = valeur; racine.setAttribute('data-' + cle, valeur); }
    // Si on choisit « non » pour le contraste, on mémorise le refus (sinon prefers-contrast le réactive).
    if (cle === 'contraste' && valeur === 'non') { p.contraste = 'non'; racine.setAttribute('data-contraste', 'non'); }
    ecrire(p);
  }

  // ---------- Panneau ----------
  var bouton = document.getElementById('acc-bouton');
  var panneau = document.getElementById('acc-panneau');
  if (!bouton || !panneau) return;

  var fermer = panneau.querySelector('.acc-fermer');

  function synchroniser() {
    panneau.querySelectorAll('input[data-pref]').forEach(function (el) {
      var cle = el.getAttribute('data-pref');
      var actuelle = valeurActuelle(cle);
      if (el.type === 'radio') el.checked = (el.value === actuelle);
      else el.checked = (actuelle === el.getAttribute('data-oui'));
    });
  }

  function ouvrir() {
    panneau.hidden = false;
    bouton.setAttribute('aria-expanded', 'true');
    synchroniser();
    var titre = panneau.querySelector('h2');
    if (titre) { titre.setAttribute('tabindex', '-1'); titre.focus(); }
  }
  function fermerPanneau(rendreFocus) {
    panneau.hidden = true;
    bouton.setAttribute('aria-expanded', 'false');
    if (rendreFocus) bouton.focus();
  }

  bouton.addEventListener('click', function () { if (panneau.hidden) ouvrir(); else fermerPanneau(false); });
  fermer.addEventListener('click', function () { fermerPanneau(true); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panneau.hidden) { fermerPanneau(true); }
  });
  document.addEventListener('click', function (e) {
    if (!panneau.hidden && !panneau.contains(e.target) && !bouton.contains(e.target)) fermerPanneau(false);
  });

  panneau.addEventListener('change', function (e) {
    var el = e.target;
    if (!el.matches('input[data-pref]')) return;
    var cle = el.getAttribute('data-pref');
    if (el.type === 'radio') appliquer(cle, el.value);
    else appliquer(cle, el.checked ? el.getAttribute('data-oui') : DEFAUTS[cle]);
  });

  panneau.querySelector('.acc-reset').addEventListener('click', function () {
    arreterLecture();
    try { localStorage.removeItem(CLE); } catch (e) { /* ignoré */ }
    ['couleurs', 'contraste', 'taille', 'police', 'espace', 'mouvement', 'cote', 'zones', 'fleches'].forEach(function (k) { racine.removeAttribute('data-' + k); });
    if (window.matchMedia && window.matchMedia('(prefers-contrast: more)').matches) racine.setAttribute('data-contraste', 'eleve');
    synchroniser();
  });

  // ---------- Se range quand on descend, revient quand on remonte ----------
  var dernierY = window.scrollY;
  var ticking = false;
  function surDefilement() {
    var y = window.scrollY;
    var maxY = document.documentElement.scrollHeight - window.innerHeight;
    var delta = y - dernierY;
    if (Math.abs(delta) > 8) {
      if (delta > 0 && y > 120) racine.classList.add('est-defilement-bas');
      else racine.classList.remove('est-defilement-bas');
      dernierY = y;
    }
    if (y < 120 || y > maxY - 40) racine.classList.remove('est-defilement-bas');
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(surDefilement); }
  }, { passive: true });
  document.addEventListener('focusin', function () { racine.classList.remove('est-defilement-bas'); });

  // ---------- Lecture à voix haute (voix du navigateur, rien à héberger) ----------
  var etat = panneau.querySelector('.acc-etat');
  var blocLecture = panneau.querySelector('[data-lecture]');
  var vitesseEl = panneau.querySelector('.acc-vitesse-val');
  var morceaux = [], indexLecture = 0, enLecture = false, vitesse = 1;
  var synth = ('speechSynthesis' in window) ? window.speechSynthesis : null;

  function majEtat(t) { if (etat) etat.textContent = t; }
  if (!synth && blocLecture) {
    blocLecture.innerHTML = '<p class="acc-aide">La lecture à voix haute n’est pas disponible sur ce navigateur.</p>';
  }

  function voixFrancaise() {
    var voix = synth.getVoices().filter(function (v) { return v.lang && v.lang.toLowerCase().indexOf('fr') === 0; });
    if (!voix.length) return null;
    return voix.filter(function (v) { return /natural|google|enhanced|premium/i.test(v.name); })[0] || voix[0];
  }
  function decouper(texte) {
    var phrases = texte.replace(/\s+/g, ' ').match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) || [texte];
    return phrases.map(function (p) { return p.trim(); }).filter(Boolean);
  }
  function lireMorceau() {
    if (!enLecture) return;
    if (indexLecture >= morceaux.length) { arreterLecture(); return; }
    var u = new SpeechSynthesisUtterance(morceaux[indexLecture]);
    u.lang = 'fr-FR'; u.rate = vitesse;
    var v = voixFrancaise(); if (v) u.voice = v;
    u.onend = function () { if (enLecture) { indexLecture++; lireMorceau(); } };
    u.onerror = function () { /* annulation volontaire : on ne fait rien */ };
    synth.speak(u);
  }
  function demarrerLecture() {
    if (!synth) return;
    var principal = document.getElementById('contenu');
    morceaux = decouper(principal ? principal.innerText : document.body.innerText);
    indexLecture = 0; enLecture = true;
    synth.cancel();
    majEtat('Lecture en cours.');
    lireMorceau();
  }
  function arreterLecture() {
    enLecture = false;
    if (synth) synth.cancel();
    majEtat('');
  }
  function reglerVitesse(delta) {
    vitesse = Math.min(2, Math.max(0.6, Math.round((vitesse + delta) * 10) / 10));
    if (vitesseEl) vitesseEl.textContent = vitesse.toFixed(1).replace('.', ',') + '×';
    if (enLecture) { synth.cancel(); lireMorceau(); }
  }
  panneau.addEventListener('click', function (e) {
    var act = e.target.getAttribute && e.target.getAttribute('data-lire');
    if (!act) return;
    if (act === 'start') demarrerLecture();
    else if (act === 'pause') {
      if (!synth) return;
      if (synth.paused) { synth.resume(); majEtat('Lecture en cours.'); }
      else { synth.pause(); majEtat('Lecture en pause.'); }
    }
    else if (act === 'stop') arreterLecture();
    else if (act === 'moins') reglerVitesse(-0.1);
    else if (act === 'plus') reglerVitesse(0.1);
  });
  window.addEventListener('pagehide', function () { if (synth) synth.cancel(); });

  // ---------- Navigation aux flèches (option, ordinateur) ----------
  var SELECTEUR = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function focusables() {
    return Array.prototype.filter.call(document.querySelectorAll(SELECTEUR), function (el) {
      if (panneau.contains(el) && panneau.hidden) return false;
      var r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
    });
  }
  function geree(el) {
    if (!el) return false;
    if (panneau.contains(el)) return true; // les flèches gardent leur rôle natif dans le panneau
    var t = el.tagName;
    if (t === 'TEXTAREA' || t === 'SELECT' || el.isContentEditable) return true;
    if (t === 'INPUT') return ['button', 'submit', 'reset', 'checkbox'].indexOf((el.type || '').toLowerCase()) === -1;
    return false;
  }
  function score(a, b, dir) {
    var dx = (b.left + b.width / 2) - (a.left + a.width / 2);
    var dy = (b.top + b.height / 2) - (a.top + a.height / 2);
    if (dir === 'right' && dx <= 2) return null;
    if (dir === 'left' && dx >= -2) return null;
    if (dir === 'down' && dy <= 2) return null;
    if (dir === 'up' && dy >= -2) return null;
    var horiz = (dir === 'left' || dir === 'right');
    return (horiz ? Math.abs(dx) : Math.abs(dy)) + (horiz ? Math.abs(dy) : Math.abs(dx)) * 2.5;
  }
  document.addEventListener('keydown', function (e) {
    if (racine.getAttribute('data-fleches') !== 'oui') return;
    var dirs = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right' };
    var dir = dirs[e.key];
    if (!dir || e.altKey || e.ctrlKey || e.metaKey || geree(document.activeElement)) return;
    var liste = focusables();
    if (!liste.length) return;
    var actif = document.activeElement;
    var r0 = (actif && liste.indexOf(actif) !== -1) ? actif.getBoundingClientRect() : { left: window.innerWidth / 2, top: 0, width: 0, height: 0 };
    var meilleur = null, mScore = Infinity;
    liste.forEach(function (el) {
      if (el === actif) return;
      var s = score(r0, el.getBoundingClientRect(), dir);
      if (s !== null && s < mScore) { mScore = s; meilleur = el; }
    });
    if (meilleur) {
      e.preventDefault();
      meilleur.focus({ preventScroll: true });
      meilleur.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
  });
})();
