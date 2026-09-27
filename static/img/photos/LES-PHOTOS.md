# Les photos du site

| Fichier | Page | Contenu |
|---|---|---|
| `accueil.jpg` | Accueil, image d'ouverture | la salle de soin, trois tables, cheminée |
| `accueil-chiropratique.jpg` | Accueil, « Et si vous commenciez aujourd'hui ? » | ajustement cervical de profil |
| `accueil-cabinet.jpg` | Accueil, grande photo de « Mon approche » | vue large de la salle, ajustement |
| `accueil-approche.jpg` | aucune pour l'instant (non publiée) | ajustement cervical, pull marine |
| `chiropratique-ajustement.jpg` | La chiropratique, « Le système nerveux » | ajustement cervical (portrait) |
| `chiropratique-explication.jpg` | La chiropratique, « Pourquoi la chiropratique ? » ; Accueil, « Votre première visite » | explication avec le modèle de colonne |
| `a-propos-portrait.jpg` | A propos, « Qui suis-je ? » ; Accueil, « Mon approche » | portrait studio |
| `a-propos-examen.jpg` | A propos, « Ce que vous trouverez au cabinet » | examen postural debout |

Les fichiers `-800` et `-1200` sont les versions pour petits écrans,
fabriquées automatiquement par `import-photos.py`.

Les portraits sont affichés dans leurs proportions d'origine sur les pages
intérieures. Sur l'accueil, les cadres recadrent l'image : garder le sujet
au centre.

## Changer une photo

```bash
python3 import-photos.py --slot accueil ~/Desktop/nouvelle-photo.jpg
python3 build.py
```

Photo disponible non utilisée : `accueil-approche.jpg` (pull marine). Une photo
qu'aucune page n'affiche n'est pas publiée.
