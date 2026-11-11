# Site d'Arc d'Iris — première version

Site statique (HTML, CSS, un peu de JavaScript). Aucun cookie, aucune ressource externe : les polices sont dans `assets/fonts`.

## Publier sur GitHub Pages
1. Créer une **organisation** GitHub pour l'association (pour ne pas exposer un compte personnel).
2. Y créer un dépôt public, par exemple `arc-d-iris.github.io` (ou n'importe quel nom).
3. Y déposer **tout le contenu de ce dossier** (pas le dossier lui-même).
4. Dépôt → Settings → Pages → Source : « Deploy from a branch », branche `main`, dossier `/ (root)`.
5. L'adresse est donnée au bout d'une ou deux minutes.

## À compléter avant d'envoyer le lien (surlignés en jaune sur le site)
- `contact.html` : l'adresse e-mail de l'association.
- `mentions-legales.html` : l'adresse e-mail, le numéro SIREN, le nom du directeur ou de la directrice de la publication.
- À vérifier : le numéro RNA et la date du récépissé, l'adresse de GitHub dans l'hébergement.
Les modifier dans `build.py` (cherche `todo(`) puis lancer `python3 build.py`, ou directement dans les fichiers `.html`.

## Modifier le site
Les pages sont générées par `build.py` : l'en-tête, la barre d'onglets, le panneau d'accessibilité et le pied de page y sont écrits une seule fois. Après une modification : `python3 build.py`, puis envoyer les fichiers `.html` modifiés sur GitHub.

## Apparaître dans Google
Une fois le site en ligne, l'ajouter dans Google Search Console (propriété « préfixe d'URL ») et demander l'indexation de la page d'accueil. C'est plus rapide qu'attendre.

## Textes des membres
Le bloc est prêt, en commentaire, à la fin de `qui()` dans `build.py`. À activer quand chaque personne a donné son accord (prénom ou pseudonyme, pas de photo).
