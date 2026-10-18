# Les photos du site

| Fichier | Page | Contenu |
|---|---|---|
| `accueil.jpg` | Accueil, image d'ouverture | la salle de soin, trois tables, cheminée |
| `accueil-chiropratique.jpg` | Accueil, « Et si vous commenciez aujourd'hui ? » | ajustement cervical de profil |
| `accueil-cabinet.jpg` | Accueil, grande photo de « Mon approche » | vue large de la salle, ajustement |
| `accueil-approche.jpg` | La chiropratique, « Au-delà des symptômes » | ajustement cervical, pull marine |
| `chiropratique-ajustement.jpg` | La chiropratique, « Le système nerveux » | ajustement cervical (portrait) |
| `chiropratique-explication.jpg` | La chiropratique, sous « Pourquoi la chiropratique ? » ; Accueil, « Votre première visite » | explication avec le modèle de colonne |
| `a-propos-portrait.jpg` | À propos, « Qui suis-je ? » ; Accueil, « Mon approche » | portrait studio |
| `a-propos-examen.jpg` | À propos, « Ce que vous trouverez au cabinet » | examen postural debout |

Les fichiers `-800` et `-1200` sont les versions pour petits écrans,
fabriquées automatiquement par `import-photos.py`. Une photo n'est jamais
agrandie : une variante n'existe que si elle est plus étroite et plus légère
que la photo elle-même (les portraits de 1066 px de large n'ont donc pas de
`-1200`).

`accueil-cabinet-mobile.jpg` et `accueil-cabinet-mobile-800.jpg` sont un
recadrage vertical fait à part, pour l'ouverture de la page de publicité sur
téléphone : le script ne les refait pas.

L'aperçu affiché quand on partage un lien du site (`static/img/og-cabinet.jpg`,
1200×630) est découpé dans `accueil.jpg` ; la commande est notée dans `build.py`.

Les portraits sont affichés dans leurs proportions d'origine sur les pages
intérieures. Sur l'accueil, les cadres recadrent l'image : garder le sujet
au centre.

## Changer une photo

```bash
python3 import-photos.py --slot accueil ~/Desktop/nouvelle-photo.jpg
python3 build.py
```

Les huit photos sont toutes utilisées. Une photo qu'aucune page n'affiche
n'est pas publiée.

Une photo n'est jamais agrandie, et une photo qui contient sa position GPS
est refusée (sur l'iPhone : Partager > Options > désactiver « Localisation »).
Après un changement de `accueil.jpg`, le script refait aussi l'aperçu de
partage, `static/img/og-cabinet.jpg`.

## Les dessins

Le système nerveux (accueil, et la carte des motifs de La chiropratique) et
le vase des 3 stress sont générés par `tools/dessin-nerfs.py` et
`tools/dessin-vase.py`, dans le style du logo. Après une retouche :

```bash
python3 tools/dessin-nerfs.py
python3 tools/dessin-vase.py
python3 build.py
```
