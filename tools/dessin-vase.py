#!/usr/bin/env python3
"""
Le vase des « 3 types de stress » (page La chiropratique), dans le style
du logo, en version épurée : un contour fin qui s'épaissit à peine au
galbe, trois filets déliés qui s'y déversent, un liquide translucide.

    python3 tools/dessin-vase.py   -> réécrit le vase dans src/pages/la-chiropratique.html

Les classes (.vase, .flux, .vase__eau--N, .vase__debord…) sont celles
qu'attendent le script et la feuille de style : seul le dessin change.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trait import echantillons, effile  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(RACINE, "src", "pages", "la-chiropratique.html")
MIROIR = "matrix(-1 0 0 1 160 0)"   # symétrie autour de x = 80

PROFIL = ("M106 100C105.58 103 103.08 111.33 103.5 118C103.92 124.67 106.33 132.67 108.5 140"
          "C110.67 147.33 114.08 154.67 116.5 162C118.92 169.33 121.5 177 123 184"
          "C124.5 191 125.83 197.33 125.5 204C125.17 210.67 123.08 218 121 224"
          "C118.92 230 115.5 235.67 113 240C110.5 244.33 107.17 248.33 106 250")
INTERIEUR = ("M106 100C105.58 103 103.08 111.33 103.5 118C103.92 124.67 106.33 132.67 108.5 140"
             "C110.67 147.33 114.08 154.67 116.5 162C118.92 169.33 121.5 177 123 184"
             "C124.5 191 125.83 197.33 125.5 204C125.17 210.67 123.08 218 121 224"
             "C118.92 230 115.5 235.67 113 240C110.5 244.33 107.17 248.33 106 250L54 250"
             "C52.83 248.33 49.5 244.33 47 240C44.5 235.67 41.08 230 39 224C36.92 218 34.83 210.67 34.5 204"
             "C34.17 197.33 35.5 191 37 184C38.5 177 41.08 169.33 43.5 162C45.92 154.67 49.33 147.33 51.5 140"
             "C53.67 132.67 56.08 124.67 56.5 118C56.92 111.33 54.42 103 54 100Z")
PIED = "M52.5 250.4C64 252.2 96 252.2 107.5 250.4"

FILETS = ["M31 0C31 42 43.5 73 66.5 104", "M80 0C80 40 80 70 80.5 104",
          "M129 0C129 42 116.5 73 93.5 104"]


def tresse(d, amplitude, tours, phase):
    """Ligne médiane ondulant de part et d'autre de d : un brin de la tresse."""
    pts = echantillons(d, 48)
    out = []
    for i, p in enumerate(pts):
        s = i / (len(pts) - 1)
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        # l'ondulation s'ouvre en haut et se referme en entrant dans le vase
        o = amplitude * math.sin(phase + 2 * math.pi * tours * s) * (0.35 + 0.65 * (1 - s))
        out.append((p[0] - dy / l * o, p[1] + dx / l * o))
    return "M" + "L".join("%.2f %.2f" % q for q in out)


def vague(largeur=220, pas=18, amplitude=.7):
    """Surface ondulée d'une strate, prolongée vers le bas."""
    d = ["M-40 0"]
    x, haut = -40, True
    while x < largeur:
        d.append("Q%.1f %.1f %.1f 0" % (x + pas / 2, -amplitude if haut else amplitude, x + pas))
        x += pas
        haut = not haut
    d.append("V300H-40Z")
    return "".join(d)


def dessin():
    cote = effile(PROFIL, .55, .8, n=40, galbe=.8)
    L = ['<svg class="vase" viewBox="0 0 160 300" aria-hidden="true" focusable="false">',
         '  <defs>',
         '    <clipPath id="vInterieur"><path d="%s"/></clipPath>' % INTERIEUR,
         '  </defs>']
    # filets qui se déversent
    L.append('  <g class="vase__flux">')
    for k, d in enumerate(FILETS, 1):
        # un seul brin délié, à peine ondulé
        brin = effile(tresse(d, .9, 1.2, 0), .15, 1.1, n=36, courbe=.8)
        L.append('    <g class="flux flux--%d"><path class="flux__corps" d="%s"/></g>' % (k, brin))
    L.append('  </g>')
    # les trois strates d'eau, translucides
    L.append('  <g clip-path="url(#vInterieur)">')
    for k in (3, 2, 1):
        L.append('    <g class="vase__eau vase__eau--%d"><path class="vase__vague" d="%s"/></g>' % (k, vague()))
    L.append('  </g>')
    # débordement
    L.append('  <g class="vase__debord">'
             '<path class="debord__filet debord__filet--g" d="M53.2 100C53.63 103.83 56.04 111.5 55.6 118'
             'C55.16 124.5 52.77 132.67 50.6 140C48.43 147.33 45.02 154.67 42.6 162C40.18 169.33 37.48 178 36.1 184'
             'C34.73 190 34.64 195.67 34.35 202"/>'
             '<path class="debord__filet debord__filet--d" d="M106.8 100C106.37 103.83 103.96 111.5 104.4 118'
             'C104.84 124.5 107.23 132.67 109.4 140C111.57 147.33 114.98 154.67 117.4 162C119.82 169.33 122.52 178 123.9 184'
             'C125.27 190 125.36 195.67 125.65 202"/>'
             '<circle class="debord__goutte debord__goutte--1" cx="34.35" cy="210" r="1.5"/>'
             '<circle class="debord__goutte debord__goutte--2" cx="125.65" cy="210" r="1.3"/></g>')
    # le contour, par-dessus tout
    moitie = '<path d="%s"/>' % cote
    L.append('  <g class="vase__contour"><g id="vMoitie">%s</g><use href="#vMoitie" transform="%s"/>'
             '<path d="%s"/></g>' % (moitie, MIROIR, effile(PIED, .8, .8, n=16, galbe=.3)))
    L.append('</svg>')
    return "\n".join(("          " if i else "") + l for i, l in enumerate(L))


if __name__ == "__main__":
    svg = dessin()
    page = open(PAGE, encoding="utf-8").read()
    page, n = re.subn(r'<svg class="vase".*?</svg>', lambda m: svg, page, flags=re.S)
    if n != 1:
        sys.exit("vase introuvable dans la-chiropratique.html")
    open(PAGE, "w", encoding="utf-8").write(page)
    print("vase réécrit (%d Ko)" % (len(svg) // 1024))
