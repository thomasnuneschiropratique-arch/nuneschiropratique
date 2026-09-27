# Les photos du site

| Fichier | Page | Contenu |
|---|---|---|
| `accueil.jpg` | Accueil, image d'ouverture | la salle de soin, trois tables, cheminée |
| `accueil-chiropratique.jpg` | Accueil, petite photo dans la phrase « Chaque jour… » | ajustement cervical de profil |
| `accueil-cabinet.jpg` | Accueil, grande photo du collage « Mon approche » | vue large de la salle, ajustement |
| `accueil-approche.jpg` | Accueil, photo en arche de « Et si vous commenciez aujourd'hui ? » | ajustement cervical, pull marine |
| `chiropratique-ajustement.jpg` | La chiropratique, « Le système nerveux » | ajustement cervical (portrait) |
| `chiropratique-explication.jpg` | La chiropratique, « Pourquoi la chiropratique ? » ; Accueil, « Votre première visite » | explication avec le modèle de colonne |
| `a-propos-portrait.jpg` | A propos, « Qui suis-je ? » ; Accueil, photo en arche du collage | portrait studio |
| `a-propos-examen.jpg` | A propos, « Ce que vous trouverez au cabinet » ; Accueil, petite photo dans la phrase | examen postural debout |

Les fichiers `-800` et `-1200` sont les versions pour petits écrans,
fabriquées automatiquement par `import-photos.py`.

Les portraits sont affichés dans leurs proportions d'origine, sans recadrage.
Sur l'accueil, les arches et les petites photos rondes recadrent l'image :
garder le sujet au centre.

## Changer une photo

```bash
python3 import-photos.py --slot accueil ~/Desktop/nouvelle-photo.jpg
python3 build.py
```

Les huit photos fournies sont toutes utilisées.
