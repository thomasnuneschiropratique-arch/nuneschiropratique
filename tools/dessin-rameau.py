#!/usr/bin/env python3
"""
Le rameau de « Mon approche » (accueil) : trois nerfs qui partent de la
colonne et s'effilent vers la droite en se croisant, comme les nerfs
latéraux du logo. Défini une fois (<symbol>) et réutilisé devant chaque
engagement.

    python3 tools/dessin-rameau.py   -> réécrit le symbole dans src/pages/index.html
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trait import effile  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(RACINE, "src", "pages", "index.html")

# (ligne médiane, épaisseur à la racine, épaisseur au bout)
BRINS = [
    ("M0 30C16 30 26 16 46 14C70 12 92 22 138 10", 4.2, .2),
    ("M0 30C22 34 40 21 62 24C86 27 104 35 136 28", 3.2, .18),
    ("M1 30C22 38 44 47 70 43C94 39 112 47 132 52", 2.4, .15),
    ("M50 15C66 18 80 27 100 30C112 32 122 30 130 24", 1.2, .12),
]


def symbole():
    formes = "".join('<path d="%s"/>' % effile(d, a, b, n=26, courbe=1.2) for d, a, b in BRINS)
    return '<symbol id="rameau" viewBox="0 0 140 56">%s</symbol>' % formes


if __name__ == "__main__":
    s = symbole()
    page = open(PAGE, encoding="utf-8").read()
    page, n = re.subn(r'<symbol id="rameau".*?</symbol>', lambda m: s, page, flags=re.S)
    if n != 1:
        sys.exit("symbole « rameau » introuvable dans index.html")
    open(PAGE, "w", encoding="utf-8").write(page)
    print("rameau réécrit (%d octets)" % len(s))
