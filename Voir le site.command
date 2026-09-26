#!/bin/bash
# Double-cliquez ce fichier pour ouvrir le site dans votre navigateur.
# Laissez cette fenêtre ouverte tant que vous regardez le site.

cd "$(dirname "$0")" || exit 1

printf '\n  Le site s ouvre dans votre navigateur...\n'
printf '  Laissez cette fenêtre ouverte pendant que vous le regardez.\n'
printf '  Pour arrêter : fermez cette fenêtre, ou Ctrl+C.\n\n'

sleep 1 && open "http://localhost:8788" &
python3 serve.py 8788
