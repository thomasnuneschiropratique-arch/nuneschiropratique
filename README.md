# nuneschiropratique.fr

Site du Cabinet chiropratique Thomas Nunes - 56 boulevard de Strasbourg, 31000 Toulouse.

Site statique, **sans aucune dépendance à installer**. Python 3 (déjà présent sur macOS)
suffit pour construire et prévisualiser. Pas de Node, pas de `npm install`, rien à
mettre à jour tous les six mois.

## Le plus simple : les deux raccourcis

Deux fichiers à double-cliquer depuis le Finder, sans passer par le Terminal :

- **`Voir le site.command`** - ouvre le site dans le navigateur.
- **`Importer les photos.command`** - importe les photos déposées dans le
  dossier `photos-a-importer`, puis reconstruit le site.

## Utilisation quotidienne (en ligne de commande)

Trois fichiers à double-cliquer dans le Finder, sans passer par le Terminal :

| Fichier | Ce qu'il fait |
|---|---|
| `Voir le site.command` | ouvre le site dans le navigateur, en local |
| `Importer les photos.command` | importe les photos déposées dans `photos-a-importer` |
| `Publier les modifications.command` | construit, contrôle, et met en ligne |

Ou en ligne de commande :

```bash
python3 build.py             # construit le site dans dist/
python3 serve.py             # prévisualise sur http://localhost:8788
python3 check.py             # contrôle liens, images, métadonnées, adresses
python3 import-photos.py photos-a-importer   # importe les photos
```

Pour travailler : lance `python3 serve.py` dans un terminal, modifie un fichier,
relance `python3 build.py` dans un autre, recharge la page.

## Où se trouve quoi

```
src/layout.html          en-tête, pied de page, <head> SEO - commun à toutes les pages
src/pages/*.html         une page = un fichier (texte + structure)
static/css/site.css      toute la mise en forme
static/css/fonts.css     déclarations des polices auto-hébergées
static/js/site.js        les animations et interactions
static/fonts/            les polices (woff2) - servies depuis le site
static/img/              logo, favicons, image de partage
static/img/photos/       les photos du cabinet + leurs variantes
tools/                   utilitaires (génération de l'image de partage)
build.py                 le générateur (navigation, sitemap, données structurées)
check.py                 les contrôles avant mise en ligne
dist/                    résultat de la construction - ne pas modifier à la main
```

## Ce qui est volontaire dans ce montage

**Aucune dépendance.** Pas de Node, pas de `npm install`, rien à mettre à jour.
Python 3 suffit, et il est déjà sur ton Mac comme sur le serveur de GitHub.

**Aucune requête vers un serveur tiers au chargement.** Les polices sont
servies depuis le site, pas depuis Google : c'est plus rapide (pas de
connexion supplémentaire à établir) et ça évite d'envoyer l'adresse IP de
chaque visiteur à Google - un vrai sujet RGPD. Seuls trois services
extérieurs interviennent, et uniquement là où ils sont utiles : PracticeHub
sur la page de rendez-vous, Google Maps sur la page contact, Formspree à
l'envoi du formulaire. `check.py` échoue si quoi que ce soit d'autre
s'ajoute.

**Images adaptées à l'écran.** Chaque photo existe en 800, 1200 et 2000 px ;
le navigateur prend la bonne. Les variantes sont fabriquées sur ton Mac par
`import-photos.py`, pas au moment de la mise en ligne - la construction
reste ainsi sans dépendance et continue de fonctionner sur le serveur.

**Politique de sécurité (CSP).** Chaque page déclare ce qu'elle s'autorise à
charger, en partant de « rien » et en n'ouvrant que le nécessaire. Un script
venu d'ailleurs - extension malveillante, injection, copier-coller distrait —
ne s'exécutera pas. Les scripts internes sont autorisés par leur empreinte,
recalculée à chaque construction : elle ne peut pas se périmer, et `check.py`
échoue si elle ne correspond plus.

**Pas de minification.** Le CSS tombe à 12 Ko une fois compressé par le
serveur, le JavaScript à 7 Ko. Minifier ferait gagner deux ou trois kilo-octets
en rendant le code illisible : le compte n'y est pas.

### Modifier un texte
Ouvre le fichier de la page dans `src/pages/`, change le texte, relance `build.py`.

### Modifier la navigation, le téléphone, l'adresse
Tout est en haut de `build.py` (constantes `NAV`, `PHONE`, `STREET`…) et dans
`src/layout.html` pour le pied de page.

### En-tête de page
Chaque fichier de `src/pages/` commence par un bloc entre `---` :
`title` et `description` sont le titre et la description Google de la page.

## Mise en ligne
Chaque `git push` sur `main` déclenche la construction et le déploiement
(voir `.github/workflows/deploy.yml`). Rien d'autre à faire.

Les étapes de première installation sont dans **DEPLOIEMENT.md**.
