#!/bin/bash
# Envoie le site vers GitHub, ce qui déclenche sa mise en ligne.
cd "$(dirname "$0")" || exit 1

echo "──────────────────────────────────────────────"
echo "  Publication du site"
echo "──────────────────────────────────────────────"
echo

echo "→ Construction…"
if ! python3 build.py; then
  echo; echo "✗ La construction a échoué. Rien n'a été envoyé."
  read -r -p "Appuyez sur Entrée pour fermer." _; exit 1
fi

echo
echo "→ Contrôles…"
if ! python3 check.py; then
  echo; echo "✗ Des problèmes ont été détectés. Rien n'a été envoyé."
  read -r -p "Appuyez sur Entrée pour fermer." _; exit 1
fi

echo
if [ -z "$(git status --porcelain)" ]; then
  echo "Aucune modification à publier."
else
  git add -A
  echo "→ Description des modifications (ou Entrée pour « Mise à jour du site ») :"
  read -r msg
  [ -z "$msg" ] && msg="Mise à jour du site"
  git commit -q -m "$msg"
  echo "  Enregistré."
fi

echo
echo "→ Envoi vers GitHub…"
if git push origin main; then
  echo
  echo "✓ Envoyé. La mise en ligne prend une à deux minutes."
  echo "  Suivi : https://github.com/thomasnuneschiropratique-arch/nuneschiropratique/actions"
else
  echo
  echo "✗ L'envoi a échoué."
  echo "  Si c'est la première fois, il faut se connecter à GitHub :"
  echo "  voir DEPLOIEMENT.md, étape 1."
fi

echo
read -r -p "Appuyez sur Entrée pour fermer." _
