/* Appliqué avant l'affichage de la page (script dans <head>, sans defer)
   pour éviter tout « flash » de la version par défaut. */
(function () {
  try {
    var p = JSON.parse(localStorage.getItem('arc-iris-prefs') || '{}');
    var h = document.documentElement;
    ['couleurs', 'contraste', 'taille', 'police', 'espace', 'mouvement', 'cote', 'zones', 'fleches'].forEach(function (k) {
      if (p[k]) h.setAttribute('data-' + k, p[k]);
    });
    if (!p.contraste && window.matchMedia && window.matchMedia('(prefers-contrast: more)').matches) {
      h.setAttribute('data-contraste', 'eleve');
    }
  } catch (e) { /* stockage indisponible : le site reste utilisable */ }
})();
