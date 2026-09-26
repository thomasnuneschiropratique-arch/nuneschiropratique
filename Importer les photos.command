#!/bin/bash
# Double-cliquez ce fichier depuis le Finder pour importer les photos
# déposées dans le dossier « photos-a-importer », puis reconstruire le site.

cd "$(dirname "$0")" || exit 1

printf '\n  Cabinet chiropratique — import des photos\n'
printf '  =========================================\n\n'

shopt -s nullglob nocaseglob
fichiers=(photos-a-importer/*.{jpg,jpeg,png,heic,heif,tif,tiff,webp})
shopt -u nullglob nocaseglob

if [ ${#fichiers[@]} -eq 0 ]; then
  printf '  Le dossier « photos-a-importer » est vide.\n\n'
  printf '  Glissez-y vos photos, puis relancez ce fichier.\n\n'
  read -r -p '  Appuyez sur Entrée pour fermer. '
  exit 0
fi

python3 import-photos.py photos-a-importer || {
  printf '\n  L import a échoué. Envoyez-moi le message ci-dessus.\n\n'
  read -r -p '  Appuyez sur Entrée pour fermer. '
  exit 1
}

printf '\n  Reconstruction du site...\n'
python3 build.py >/dev/null && printf '  Site reconstruit.\n'

printf '\n  Terminé. Lancez « Voir le site.command » pour le regarder.\n\n'
read -r -p '  Appuyez sur Entrée pour fermer. '
