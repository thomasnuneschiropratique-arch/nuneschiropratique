#!/bin/bash
# Construit le site, le contrôle, enregistre les modifications, puis ouvre
# GitHub Desktop pour le dernier geste : cliquer sur « Push origin ».
#
# L'envoi lui-même passe par GitHub Desktop parce que c'est lui qui garde ta
# connexion à GitHub. Le Terminal n'y a pas accès.
cd "$(dirname "$0")" || exit 1

echo "──────────────────────────────────────────────"
echo "  Préparation de la mise en ligne"
echo "──────────────────────────────────────────────"
echo

echo "→ Construction…"
if ! python3 build.py; then
  echo; echo "✗ La construction a échoué. Rien n'a été enregistré."
  read -r -p "Appuyez sur Entrée pour fermer." _; exit 1
fi

echo
echo "→ Contrôles…"
if ! python3 check.py; then
  echo; echo "✗ Des problèmes ont été détectés. Rien n'a été enregistré."
  read -r -p "Appuyez sur Entrée pour fermer." _; exit 1
fi

echo
if [ -z "$(git status --porcelain)" ]; then
  echo "Aucune nouvelle modification à enregistrer."
else
  git add -A
  echo "→ Décris tes modifications en une phrase (ou Entrée pour « Mise à jour du site ») :"
  read -r msg
  [ -z "$msg" ] && msg="Mise à jour du site"
  git commit -q -m "$msg"
  echo "  Enregistré."
fi

echo
echo "──────────────────────────────────────────────"
echo "  Dernier geste : dans GitHub Desktop,"
echo "  clique sur « Push origin » (en haut à droite)."
echo "──────────────────────────────────────────────"
echo
if open -a "GitHub Desktop" "$(pwd)" 2>/dev/null; then
  echo "GitHub Desktop est ouvert sur ce dossier."
else
  echo "Ouvre GitHub Desktop toi-même : le dossier Sitechiro y est déjà."
fi
echo "Le site se met à jour environ deux minutes après l'envoi."

echo
read -r -p "Appuyez sur Entrée pour fermer." _
