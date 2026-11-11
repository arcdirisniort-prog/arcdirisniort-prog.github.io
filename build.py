#!/usr/bin/env python3
"""Génère les pages HTML du site Arc d'Iris à partir des contenus ci-dessous.

Usage :  python3 build.py
Les pages produites (index.html, qui-sommes-nous.html, ...) sont celles qui sont publiées.
En-tête, barre d'onglets, panneau d'accessibilité et pied de page sont écrits une seule fois ici.
"""
import re
from pathlib import Path

RACINE = Path(__file__).parent

# ---------------------------------------------------------------- pages
PAGES = [
    # clé, fichier, libellé long, libellé court, icône
    ("accueil", "index.html", "Accueil", "Accueil", "home"),
    ("qui", "qui-sommes-nous.html", "Qui sommes-nous", "Nous", "users"),
    ("activites", "activites.html", "Activités", "Activités", "calendar"),
    ("allies", "allies.html", "Alliés", "Alliés", "heart"),
    ("contact", "contact.html", "Contact", "Contact", "mail"),
]

ICONES = {
    "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
}

NOM_SITE = "Arc d’Iris"

# ---------------------------------------------------------------- briques communes
def marque_svg():
    arcs = ""
    for i, r in enumerate([20.5, 17.5, 14.5, 11.5, 8.5, 5.5], start=1):
        arcs += f'<path class="b{i}" d="M{22 - r} 22 A{r} {r} 0 0 1 {22 + r} 22"/>'
    return f'<svg viewBox="0 0 44 22" aria-hidden="true" focusable="false">{arcs}</svg>'


def hero_svg():
    rayons = [562, 526, 490, 454, 418, 382]
    bandes, motifs = "", ""
    for i, r in enumerate(rayons, start=1):
        d = f"M{600 - r} 600 A{r} {r} 0 0 1 {600 + r} 600"
        bandes += f'<path class="bande b{i}" pathLength="1" style="--i:{i - 1}" d="{d}"/>'
        motifs += f'<path class="motif m{i}" stroke="url(#pm{i})" d="{d}"/>'
    defs = """<defs>
      <pattern id="pm1" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="12" stroke="#000" stroke-opacity=".5" stroke-width="3"/></pattern>
      <pattern id="pm2" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="2.6" fill="#000" fill-opacity=".5"/></pattern>
      <pattern id="pm3" width="12" height="12" patternUnits="userSpaceOnUse"><line x1="0" y1="6" x2="12" y2="6" stroke="#000" stroke-opacity=".45" stroke-width="3"/></pattern>
      <pattern id="pm4" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 7H14M7 0V14" stroke="#000" stroke-opacity=".5" stroke-width="2.4"/></pattern>
      <pattern id="pm5" width="12" height="12" patternUnits="userSpaceOnUse"><line x1="6" y1="0" x2="6" y2="12" stroke="#000" stroke-opacity=".5" stroke-width="3"/></pattern>
      <pattern id="pm6" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="12" stroke="#000" stroke-opacity=".5" stroke-width="3"/></pattern>
    </defs>"""
    return (f'<svg viewBox="0 0 1200 600" aria-hidden="true" focusable="false">{defs}{bandes}{motifs}</svg>')


def drapeau_classique():
    bandes = "".join(f'<rect y="{i * 10}" width="90" height="10" class="f{i + 1}"/>' for i in range(6))
    return (f'<svg viewBox="0 0 90 60" role="img" aria-label="Drapeau arc-en-ciel : six bandes horizontales, '
            f'du rouge en haut au violet en bas">{bandes}</svg>')


def drapeau_progress():
    bandes = "".join(f'<rect y="{i * 10}" width="90" height="10" class="f{i + 1}"/>' for i in range(6))
    # Du plus grand au plus petit : le blanc est à la pointe, le noir côté hampe.
    couches = [(20, "fb"), (16.5, "fr"), (13, "fc"), (9.5, "fm"), (6, "fn")]
    chevron = "".join(f'<polygon class="{c}" points="0,0 {w},0 {w + 20},30 {w},60 0,60"/>' for w, c in couches)
    return (f'<svg viewBox="0 0 90 60" role="img" aria-label="Drapeau Progress : les six bandes arc-en-ciel, '
            f'avec un chevron pointant vers la droite en noir, marron, bleu clair, rose et blanc">{bandes}{chevron}</svg>')


def coin_arc():
    arcs = ""
    for r in (50, 92, 134):
        arcs += f'<path d="M{200 - r} 0 A{r} {r} 0 0 0 200 {r}"/>'
    return f'<svg class="coin-arc" viewBox="0 0 200 200" aria-hidden="true" focusable="false">{arcs}</svg>'


def entete(cle):
    liens = ""
    for k, fichier, long_, _court, _ic in PAGES:
        if k == cle:
            liens += f'<a href="{fichier}" aria-current="page">{long_}<span class="arc-actif" aria-hidden="true"></span></a>'
        else:
            liens += f'<a href="{fichier}">{long_}</a>'
    return f"""<header class="entete">
  <div class="wrap entete-interieur">
    <a class="marque" href="index.html" aria-label="{NOM_SITE}, accueil">{marque_svg()}<span>{NOM_SITE}</span></a>
    <nav class="nav" aria-label="Navigation principale">{liens}</nav>
  </div>
</header>"""


def onglets(cle):
    liens = ""
    for k, fichier, long_, court, ic in PAGES:
        svg = f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONES[ic]}</svg>'
        if k == cle:
            liens += f'<a href="{fichier}" aria-current="page" aria-label="{long_}"><span class="arc-actif" aria-hidden="true"></span>{svg}<span>{court}</span></a>'
        else:
            liens += f'<a href="{fichier}" aria-label="{long_}">{svg}<span>{court}</span></a>'
    return f'<nav class="onglets" aria-label="Navigation principale (mobile)">{liens}</nav>'


def choix(nom, options, legende, aide=""):
    """Groupe de boutons radio présentés comme des boutons."""
    items = "".join(
        f'<label><input type="radio" name="p-{nom}" data-pref="{nom}" value="{val}"><span>{lib}</span></label>'
        for val, lib in options
    )
    aide_html = f'<p class="acc-aide">{aide}</p>' if aide else ""
    return f'<fieldset><legend>{legende}</legend><div class="acc-choix">{items}</div>{aide_html}</fieldset>'


def interrupteur(nom, oui, libelle):
    return (f'<label class="acc-interrupteur"><input type="checkbox" data-pref="{nom}" data-oui="{oui}">'
            f'<span>{libelle}</span></label>')


def panneau_acc():
    icone = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10"/>'
             '<circle cx="12" cy="7.6" r="1.3"/><path d="M7 10.4l5 1 5-1M12 11.4v4M9.6 19.5l2.4-4.1 2.4 4.1"/></svg>')
    return f"""<button type="button" id="acc-bouton" class="acc-bouton" aria-expanded="false" aria-controls="acc-panneau" aria-label="Réglages d’accessibilité">{icone}</button>
<div id="acc-panneau" class="acc-panneau" role="dialog" aria-labelledby="acc-titre" hidden>
  <div class="acc-entete"><h2 id="acc-titre">Accessibilité</h2><button type="button" class="acc-fermer" aria-label="Fermer les réglages">×</button></div>
  {choix("couleurs", [("arc", "Arc-en-ciel"), ("daltonien", "Daltonisme"), ("mono", "Sans couleur")], "Couleurs",
         "« Daltonisme » utilise une palette lisible par tous les types de daltonisme et ajoute des motifs sur les bandes.")}
  {interrupteur("contraste", "eleve", "Contraste élevé")}
  {choix("taille", [("1", "A"), ("2", "A+"), ("3", "A++")], "Taille du texte")}
  {interrupteur("police", "lisible", "Police très lisible")}
  {interrupteur("espace", "aere", "Texte plus aéré")}
  {interrupteur("mouvement", "reduit", "Réduire les animations")}
  {choix("cote", [("gauche", "À gauche"), ("droite", "À droite")], "Côté du pouce",
         "Place ce bouton du côté de votre main.")}
  {interrupteur("zones", "grandes", "Grandes zones à toucher")}
  {interrupteur("fleches", "oui", "Naviguer avec les flèches du clavier")}
  <fieldset data-lecture><legend>Écouter cette page</legend>
    <div class="acc-lecture">
      <button type="button" data-lire="start">Écouter</button>
      <button type="button" data-lire="pause">Pause</button>
      <button type="button" data-lire="stop">Arrêter</button>
    </div>
    <div class="acc-lecture" style="margin-top:.5rem">
      <span class="acc-vitesse">Vitesse
        <button type="button" data-lire="moins" aria-label="Ralentir la lecture">−</button>
        <span class="acc-vitesse-val" aria-live="polite">1,0×</span>
        <button type="button" data-lire="plus" aria-label="Accélérer la lecture">+</button>
      </span>
    </div>
    <p class="acc-etat" role="status"></p>
  </fieldset>
  <button type="button" class="acc-reset">Rétablir les réglages d’origine</button>
</div>"""


def pied():
    return f"""<footer class="pied">
  <div class="pied-arc" aria-hidden="true"></div>
  <div class="wrap pied-interieur">
    <div>
      <p><strong>{NOM_SITE}</strong></p>
      <p>Association loi 1901 pour les personnes LGBTQIA+ et leurs alliés.</p>
      <p>Siège : Maison des Associations, Niort.</p>
      <p>Les réglages d’accessibilité sont dans le bouton rond en bas de l’écran.</p>
    </div>
    <div class="pied-liens">
      <a href="contact.html">Contact</a>
      <a href="mentions-legales.html">Mentions légales</a>
    </div>
  </div>
</footer>"""


def suite(vers, libelle):
    return f"""<div class="suite"><div class="wrap">
  <p>Continuer vers</p>
  <a href="{vers}">{libelle}</a>
</div></div>"""


def page(cle, fichier, titre, description, contenu, noindex=False):
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#ffffff">
<meta name="color-scheme" content="light">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">{robots}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/bricolage-grotesque-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/figtree-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<script src="assets/js/prefs.js"></script>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body data-page="{cle}">
<a class="lien-evitement" href="#contenu">Aller au contenu</a>
{entete(cle)}
<main id="contenu">
{contenu}
</main>
{pied()}
{onglets(cle)}
{panneau_acc()}
<script src="assets/js/app.js" defer></script>
</body>
</html>
"""
    return typographie(html)


def typographie(html):
    """Espaces insécables à la française, hors balises."""
    def corriger(texte):
        texte = re.sub(r" ([:;?!»])", "&nbsp;\\1", texte)
        texte = re.sub(r"(«) ", "\\1&nbsp;", texte)
        return texte
    morceaux = re.split(r"(<[^>]+>)", html)
    sortie, ignorer = [], False
    for m in morceaux:
        if m.startswith("<"):
            if re.match(r"<(script|style)\b", m, re.I): ignorer = True
            if re.match(r"</(script|style)\b", m, re.I): ignorer = False
            sortie.append(m)
        else:
            sortie.append(m if ignorer else corriger(m))
    return "".join(sortie)


def todo(texte):
    return f'<span class="a-completer">[{texte}]</span>'


# ---------------------------------------------------------------- contenus
def accueil():
    actions = [
        ("Se retrouver", "Des rencontres et des événements pour échanger, jouer et faire connaissance dans un cadre bienveillant."),
        ("Faire connaître les cultures LGBTQIA+", "Mettre en avant leur histoire, leurs créations et leurs luttes."),
        ("Écouter et orienter", "Un espace d’accueil et d’écoute, et l’orientation vers les structures adaptées quand l’association ne peut pas aider elle-même."),
        ("Sensibiliser", "Informer sur les discriminations liées à l’orientation sexuelle, à l’identité et à l’expression de genre."),
        ("Coopérer", "Travailler avec les établissements d’enseignement et les autres associations."),
    ]
    items = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in actions)
    return f"""<section class="heros">
  <div class="wrap">
    <div class="heros-arc">
      {hero_svg()}
      <h1 class="heros-titre">Arc d’Iris</h1>
    </div>
    <div class="heros-texte">
      <p class="lead">Une association pour les personnes LGBTQIA+ et leurs alliés, à Niort.</p>
      <div class="actions">
        <a class="bouton" href="qui-sommes-nous.html">Découvrir l’association</a>
        <a class="bouton discret" href="contact.html">Nous écrire</a>
      </div>
    </div>
  </div>
</section>

<section class="bloc">
  <div class="wrap deux-col">
    <div>
      <h2>Ce que fait Arc d’Iris</h2>
      <p class="texte">Arc d’Iris représente, soutient et défend les personnes LGBTQIA+ et leurs alliés. Chacune et chacun doit pouvoir être visible, écouté et respecté, quelle que soit son orientation sexuelle, son identité ou son expression de genre.</p>
      <p class="texte"><a href="activites.html">Voir toutes les activités</a></p>
    </div>
    <ul class="liste-arc" style="margin-top:0">{items}</ul>
  </div>
</section>

<section class="bloc teinte">
  <div class="wrap">
    <h2>Les alliés sont les bienvenus</h2>
    <p class="lead">Il n’est pas nécessaire d’être LGBTQIA+ pour participer. Écouter, apprendre et soutenir, c’est déjà une façon d’agir avec nous.</p>
    <p style="margin-top:1.25rem"><a class="bouton" href="allies.html">Ce que les alliés peuvent faire</a></p>
  </div>
</section>

<section class="bloc">
  <div class="wrap">
    <h2>Deux drapeaux</h2>
    <p class="texte">Nous utilisons deux drapeaux, parce qu’ils racontent deux moments d’une même histoire.</p>
    <div class="drapeaux">
      <figure class="drapeau" style="margin:0">
        {drapeau_classique()}
        <figcaption><h3>Le drapeau arc-en-ciel</h3>Créé à San Francisco en 1978 par Gilbert Baker, c’est le symbole le plus connu de la communauté LGBTQIA+. Il célèbre sa diversité.</figcaption>
      </figure>
      <figure class="drapeau" style="margin:0">
        {drapeau_progress()}
        <figcaption><h3>Le drapeau Progress</h3>Conçu par Daniel Quasar en 2018, il ajoute un chevron : noir et marron pour les personnes LGBTQIA+ racisées, bleu clair, rose et blanc pour les personnes trans. Il rappelle que la lutte pour l’inclusion n’est pas terminée.</figcaption>
      </figure>
    </div>
  </div>
</section>
{suite("qui-sommes-nous.html", "Qui sommes-nous")}"""


def qui():
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Qui sommes-nous</h1>
    <p class="lead">Arc d’Iris est une association loi 1901 fondée en 2026 à Niort par quatre étudiantes et étudiants.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap texte">
    <h2>Notre histoire</h2>
    <p>Le projet est né à la rentrée 2026 sous la forme d’un club étudiant, avec une idée simple : donner une place visible aux personnes LGBTQIA+ et à leurs alliés. Il est devenu une association déclarée en préfecture, dont le siège est à la Maison des Associations de Niort.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap texte">
    <h2>Notre objet</h2>
    <p>L’association a pour but de représenter, soutenir et défendre les personnes LGBTQIA+ et leurs alliés. Elle veut promouvoir leur inclusion et leur visibilité, et lutter contre les discriminations liées à l’orientation sexuelle, à l’identité ou à l’expression de genre.</p>
    <p><a href="activites.html">Voir les activités</a></p>
  </div>
</section>

<section class="bloc">
  <div class="wrap texte">
    <h2>Comment elle fonctionne</h2>
    <p>Arc d’Iris est dirigée collectivement par un collège de quatre co-présidents. Chaque année, deux d’entre eux quittent le collège et deux nouveaux sont élus : ceux qui restent forment les arrivants, et la direction ne repose jamais sur une seule personne.</p>
    <p>Chaque pôle de travail est suivi par un membre du collège, choisi d’un commun accord. Pour participer ou adhérer, <a href="contact.html">écrivez-nous</a>.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap texte">
    <h2>Pourquoi ce nom</h2>
    <p>Dans la mythologie grecque, Iris est la messagère des dieux et la personnification de l’arc-en-ciel, qu’elle emprunte pour passer d’un monde à l’autre. Le nom dit ce que nous voulons être : un lien entre les personnes, et une place pour toutes les couleurs.</p>
  </div>
</section>

<!-- Emplacement des textes des membres (à activer quand ils sont prêts et que chaque personne a donné son accord) :
<section class="bloc">
  <div class="wrap">
    <h2>Les voix de l’association</h2>
    <div class="liste-simple">
      <article><h3>Prénom ou pseudonyme</h3><p>Qui je suis, pourquoi je m’engage, ce que j’aimerais voir à Arc d’Iris.</p></article>
    </div>
  </div>
</section>
-->
{suite("activites.html", "Activités")}"""


def activites():
    acts = [
        ("Rencontres et jeux", "Des moments pour se retrouver, discuter et jouer ensemble. Le format et le rythme seront choisis avec les premières personnes qui nous rejoindront."),
        ("Cultures LGBTQIA+", "Mettre en avant l’histoire, les œuvres et les luttes des personnes LGBTQIA+, par des événements ouverts à toutes et à tous."),
        ("Accueil et écoute", "Un espace pour parler sans être jugé. Quand l’association ne peut pas répondre à une situation, elle oriente vers des structures spécialisées. Elle ne remplace ni un suivi médical, ni une aide juridique."),
        ("Sensibilisation", "Informer sur les discriminations liées à l’orientation sexuelle, à l’identité et à l’expression de genre, auprès de tous les publics."),
        ("Coopération", "Travailler avec les établissements d’enseignement et les autres associations, pour agir ensemble et mieux se faire entendre."),
    ]
    items = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in acts)
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Activités</h1>
    <p class="lead">Arc d’Iris est une jeune association : son programme se construit avec ses membres.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap">
    <h2>Ce que nous mettons en place</h2>
    <ul class="liste-arc">{items}</ul>
  </div>
</section>

<section class="bloc">
  <div class="wrap">
    <h2>Prochains rendez-vous</h2>
    <div class="vide">
      <p><strong>Aucun événement n’est annoncé pour le moment.</strong></p>
      <p>Écrivez-nous pour être prévenu du prochain rendez-vous, ou pour proposer une idée.</p>
      <p><a class="bouton" href="contact.html">Nous écrire</a></p>
    </div>
  </div>
</section>
{suite("allies.html", "Alliés")}"""


def allies():
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Les alliés ont leur place ici</h1>
    <p class="lead">Vous n’avez pas besoin d’être LGBTQIA+ pour rejoindre Arc d’Iris. Il suffit de respecter les personnes que vous y rencontrez.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap">
    <h2>Être un allié, concrètement</h2>
    <ul class="liste-simple">
      <li><strong>Écouter plus que parler.</strong> Les personnes concernées sont les mieux placées pour dire ce qu’elles vivent.</li>
      <li><strong>Ne jamais révéler l’orientation sexuelle ou l’identité de genre de quelqu’un.</strong> Ce n’est pas à vous de le dire, même par maladresse.</li>
      <li><strong>Apprendre par soi-même.</strong> Ne demandez pas à une personne de tout vous expliquer : des livres, des sites et des associations existent pour cela.</li>
      <li><strong>Réagir face aux propos ou aux gestes discriminatoires,</strong> sans mettre en danger la personne visée et sans parler à sa place.</li>
      <li><strong>Accepter de se tromper.</strong> Si on vous corrige, remerciez et continuez.</li>
    </ul>
  </div>
</section>

<section class="bloc teinte">
  <div class="wrap texte">
    <h2>Venir à Arc d’Iris</h2>
    <p>Les alliés font partie de l’association : ils participent aux rencontres et aux actions, aux côtés des personnes LGBTQIA+. Si vous voulez nous rejoindre ou simplement poser une question, écrivez-nous.</p>
    <p><a class="bouton" href="contact.html">Nous écrire</a></p>
  </div>
</section>
{suite("contact.html", "Contact")}"""


def contact():
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Contact</h1>
    <p class="lead">Une question, une envie de participer, une idée d’événement ? Écrivez-nous.</p>
  </div>
</section>

<section class="bloc">
  <div class="wrap texte">
    <h2>Par courriel</h2>
    <p class="carte-contact"><a href="mailto:arcdiris.niort@gmail.com">arcdiris.niort@gmail.com</a></p>
    <p>Nous répondons aux messages dès que nous le pouvons.</p>
    <h2 style="margin-top:2.5rem">Par courrier</h2>
    <address>Arc d’Iris<br>Maison des Associations<br>12 rue Joseph Cugnot<br>79000 Niort</address>
  </div>
</section>

<section class="bloc teinte">
  <div class="wrap texte">
    <h2>Besoin d’aide maintenant ?</h2>
    <p>Arc d’Iris est une jeune association de bénévoles : elle ne peut pas répondre en urgence. Si vous êtes en danger ou en détresse :</p>
    <ul class="liste-simple">
      <li><strong>Danger immédiat :</strong> appelez le 112.</li>
      <li><strong>Détresse, pensées suicidaires :</strong> le 3114, gratuit, 24 h sur 24 et 7 jours sur 7.</li>
      <li><strong>Discriminations et violences LGBTphobes :</strong> <a href="https://www.sos-homophobie.org" rel="noopener">SOS homophobie</a>, ligne d’écoute et aide aux victimes.</li>
      <li><strong>Jeunes en rupture familiale :</strong> <a href="https://www.le-refuge.org" rel="noopener">Le Refuge</a>, hébergement et accompagnement.</li>
    </ul>
  </div>
</section>
{suite("index.html", "Retour à l’accueil")}"""


def mentions():
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Mentions légales</h1>
  </div>
</section>

<section class="bloc legal">
  <div class="wrap">
    <h2>Éditeur du site</h2>
    <dl>
      <dt>Association</dt><dd>Arc d’Iris, association déclarée régie par la loi du 1er juillet 1901</dd>
      <dt>Siège</dt><dd>Maison des Associations, 12 rue Joseph Cugnot, 79000 Niort</dd>
      <dt>Déclaration en préfecture</dt><dd>Récépissé du 2 novembre 2026, numéro RNA W792010438</dd>
      <dt>SIREN</dt><dd>132 642 737</dd>
      <dt>SIRET</dt><dd>132 642 737 00010</dd>
      <dt>Représentation</dt><dd>L’association est dirigée par un collège de quatre co-présidents.</dd>
      <dt>Directeur de la publication</dt><dd>Le co-président ou la co-présidente qui dirige le pôle communication de l’association. Cette fonction change de titulaire au fil des renouvellements du collège. C’est à cette personne que doit être adressée toute demande de retrait d’un contenu.</dd>
      <dt>Contact</dt><dd><a href="mailto:arcdiris.niort@gmail.com">arcdiris.niort@gmail.com</a></dd>
    </dl>

    <h2>Hébergement</h2>
    <dl>
      <dt>Hébergeur</dt><dd>GitHub Pages, service de GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis</dd>
    </dl>

    <h2>Données personnelles</h2>
    <p class="texte">Ce site n’utilise ni cookies, ni outil de mesure d’audience, ni service publicitaire. Les polices de caractères sont hébergées sur le site lui-même : aucune donnée n’est envoyée à un tiers pour les afficher.</p>
    <p class="texte">Vos réglages d’accessibilité sont enregistrés uniquement dans votre navigateur, sur votre appareil. Ils ne nous sont jamais transmis.</p>
    <p class="texte">Si vous nous écrivez, nous utilisons votre message et votre adresse uniquement pour vous répondre. Vous pouvez demander à tout moment leur suppression en nous écrivant.</p>
    <p class="texte">Comme tout hébergeur, GitHub peut enregistrer l’adresse IP des personnes qui consultent le site dans ses journaux techniques.</p>

    <h2>Propriété et crédits</h2>
    <p class="texte">Les textes et éléments graphiques de ce site appartiennent à l’association Arc d’Iris, sauf mention contraire. Les polices Bricolage Grotesque, Figtree et Atkinson Hyperlegible sont utilisées sous licence libre SIL Open Font License.</p>
  </div>
</section>"""


def erreur404():
    return f"""<section class="page-tete">
  {coin_arc()}
  <div class="wrap">
    <h1>Page introuvable</h1>
    <p class="lead">L’adresse demandée n’existe pas ou a changé.</p>
    <p style="margin-top:1.5rem"><a class="bouton" href="index.html">Retourner à l’accueil</a></p>
  </div>
</section>"""


SORTIES = [
    ("accueil", "index.html", "Arc d’Iris – Association LGBTQIA+ et alliée à Niort",
     "Arc d’Iris est une association loi 1901 qui représente, soutient et défend les personnes LGBTQIA+ et leurs alliés, à Niort.", accueil, False),
    ("qui", "qui-sommes-nous.html", "Qui sommes-nous – Arc d’Iris",
     "Histoire, objet et fonctionnement d’Arc d’Iris, association LGBTQIA+ et alliée fondée en 2026 à Niort.", qui, False),
    ("activites", "activites.html", "Activités – Arc d’Iris",
     "Rencontres, valorisation des cultures LGBTQIA+, accueil et écoute, sensibilisation : les activités d’Arc d’Iris.", activites, False),
    ("allies", "allies.html", "Alliés – Arc d’Iris",
     "Les alliés ont leur place à Arc d’Iris : ce qu’ils peuvent faire, et comment participer.", allies, False),
    ("contact", "contact.html", "Contact – Arc d’Iris",
     "Contacter Arc d’Iris, et ressources d’aide en cas de détresse ou de discrimination.", contact, False),
    ("legal", "mentions-legales.html", "Mentions légales – Arc d’Iris",
     "Mentions légales du site de l’association Arc d’Iris.", mentions, False),
    ("legal", "404.html", "Page introuvable – Arc d’Iris",
     "Cette page n’existe pas.", erreur404, True),
]

if __name__ == "__main__":
    for cle, fichier, titre, desc, fabrique, noindex in SORTIES:
        (RACINE / fichier).write_text(page(cle, fichier, titre, desc, fabrique(), noindex), encoding="utf-8")
        print("écrit", fichier)
