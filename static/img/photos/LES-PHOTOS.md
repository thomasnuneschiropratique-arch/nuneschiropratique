# Les photos du site

| Fichier | Page | Contenu |
|---|---|---|
| `accueil.jpg` | Accueil, image d'ouverture | la salle de soin, trois tables, cheminée |
| `chiropratique-ajustement.jpg` | La chiropratique, « Le système nerveux » | ajustement cervical (portrait) |
| `chiropratique-explication.jpg` | La chiropratique, « Pourquoi la chiropratique ? » | explication avec le modèle de colonne |
| `a-propos-portrait.jpg` | A propos, « Qui suis-je ? » | portrait studio |
| `a-propos-examen.jpg` | A propos, « Ce que vous trouverez au cabinet » | examen postural debout |

Les fichiers `-800` et `-1200` sont les versions pour petits écrans,
fabriquées automatiquement par `import-photos.py`.

Les portraits sont affichés dans leurs proportions d'origine, sans recadrage.

## Changer une photo

```bash
python3 import-photos.py --slot accueil ~/Desktop/nouvelle-photo.jpg
python3 build.py
```

Photos disponibles non utilisées : `ajustement.jpeg`, `ajustement first.jpeg`, `thomas-ajustement-cervical.jpg`.
