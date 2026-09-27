#!/usr/bin/env python3
"""
Dessin du système nerveux de la page d'accueil, dans le style du logo :
cerveau clair et nuancé, colonne épaisse arrondie, côtes en boucles
emboîtées, nerfs qui s'effilent jusqu'aux mains et aux pieds.

    python3 tools/dessin-nerfs.py
      -> réécrit le dessin de l'accueil (src/pages/index.html)
         et la carte des motifs de La chiropratique (src/pages/la-chiropratique.html)

La moitié droite est dessinée ; la gauche en est le reflet (<use>).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trait import effile  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(RACINE, "src", "pages")
MIROIR = "matrix(-1 0 0 1 400 0)"   # symétrie autour de x = 200

# ---------------------------------------------------------------- cerveau
CERVEAU = ("M200 19C210 15 224 17 229 27C236 31 238 41 233 48C236 56 229 65 219 64"
           "C214 70 205 70 200 65Z")
SILLONS = ["M206 27C213 28 217 33 213 38", "M222 35C216 38 215 44 220 48",
           "M207 45C212 47 213 53 208 57", "M224 55C220 57 216 57 214 61"]

# ---------------------------------------------------------------- colonne
COLONNE = "M200 62V372"

# ---------------------------------------------------------------- nerfs (moitié droite)
# (ligne médiane, épaisseur à la racine, épaisseur au bout, courbe)
NUQUE = [("M203 %d C212 %d 236 %d %d %d" % (y, y - 14, y - 10, 248 + 6 * k, 132 + 8 * k), 2.2, .3, 1.0)
         for k, y in enumerate((100, 108, 116, 124))]
BRAS = [
    ("M203 118C236 120 262 128 272 150C282 190 286 240 292 290C296 320 300 345 306 372", 3.2, .35, 1.3),
    ("M203 128C232 134 256 142 266 162C276 200 284 250 288 300C290 330 292 350 296 376", 2.8, .3, 1.3),
    ("M203 138C228 146 250 156 260 176C268 214 278 262 282 310C284 335 286 355 286 378", 2.6, .3, 1.3),
    ("M298 338C302 350 308 360 318 366", 1.1, .15, 1.0),
    ("M290 344C292 356 291 368 289 382", 1.0, .15, 1.0),
    ("M294 342C298 354 300 364 304 378", 1.0, .15, 1.0),
]
COTES = []
for k, (y, xm) in enumerate(zip((176, 204, 232, 260, 288), (256, 264, 268, 268, 262))):
    d = "M203 %d C226 %d %d %d %d %d C%d %d %d %d 226 %d" % (
        y, y - 8, xm - 8, y - 6, xm, y + 10, xm + 4, y + 24, xm - 20, y + 32, y + 30)
    COTES.append((d, 3.0, .7, 1.0))
JAMBES = [
    ("M203 330C222 346 232 370 232 404C232 450 236 500 236 540C236 570 238 594 244 616", 3.0, .3, 1.4),
    ("M203 342C216 360 224 384 224 414C224 460 228 510 228 550C228 578 230 598 232 620", 2.8, .3, 1.4),
    ("M203 354C212 372 216 396 216 426C216 470 220 516 222 556C224 584 222 604 220 622", 2.6, .3, 1.4),
    ("M238 596C244 606 252 612 262 616", 1.0, .15, 1.0),
]

# repères des légendes : (point visé, fin du trait)
REPERES = [("cerveau", (234, 36)), ("colonne", (205, 80)), ("corps", (320, 364))]

# zones de la carte des motifs : (nom, x, y, rayon)
ZONES = [("tete", 200, 42, 30), ("dos", 200, 232, 26), ("ventre", 200, 314, 18),
         ("bassin", 200, 362, 18), ("jambe", 226, 440, 20),
         ("membres", 282, 252, 18), ("membres", 172, 520, 18),
         ("peau", 297, 336, 16), ("peau", 103, 336, 16)]


def formes(liste):
    return "".join('<path d="%s"/>' % effile(d, a, b, n=22, courbe=c) for d, a, b, c in liste)


def moitie(ident, contenu):
    return ('<g id="%s">%s</g><use href="#%s" transform="%s"/>' % (ident, contenu, ident, MIROIR))


def dessin(classe="nerfs__svg", largeur=560, reperes=True, zones=False):
    L = ['<svg class="%s" viewBox="0 0 %d 640" aria-hidden="true" focusable="false">' % (classe, largeur)]
    L.append('  <defs><linearGradient id="nfTeinte" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#BFCDCB"/>'
             '</linearGradient></defs>')
    L.append('  <g class="nerf nerf--cotes">' + moitie("nfCotes", formes(COTES)) + '</g>')
    L.append('  <g class="nerf nerf--bras">' + moitie("nfBras", formes(NUQUE + BRAS)) + '</g>')
    L.append('  <g class="nerf nerf--jambes">' + moitie("nfJambes", formes(JAMBES)) + '</g>')
    colonne = effile(COLONNE, 7.5, 10.5, n=12)
    L.append('  <g class="nerf nerf--colonne"><path d="%s"/><circle cx="200" cy="372" r="5.25"/></g>' % colonne)
    # couleurs en attributs : la copie en miroir (<use>) ne reçoit pas
    # les règles CSS visant l'original, seulement ce qu'il porte lui-même
    cerveau = ('<path d="%s" fill="url(#nfTeinte)" stroke="#9CB0AE" stroke-width=".9"/>' % CERVEAU
               + "".join('<path d="%s" fill="none" stroke="#9CB0AE" stroke-width="1" stroke-linecap="round"/>' % s
                         for s in SILLONS))
    L.append('  <g class="nerf nerf--cerveau">' + moitie("nfCerveau", cerveau)
             + '<path d="M200 20V64" fill="none" stroke="#9CB0AE" stroke-width="1"/></g>')
    # influx : lignes médianes, parcourues par un point de lumière. Pas de
    # <use> ici : une animation CSS ne traverse pas toujours la copie.
    membres = ('<path class="influx__bras" d="%s" pathLength="1"/>' % BRAS[0][0]
               + '<path class="influx__jambe" d="%s" pathLength="1"/>' % JAMBES[0][0])
    L.append('  <g class="influx">'
             '<path class="influx__axe" d="M200 64V372" pathLength="1"/>'
             + '<g>' + membres + '</g><g transform="%s">' % MIROIR + membres + '</g>'
             + '</g>')
    if reperes:
        L.append('  <g class="reperes">')
        for nom, (x, y) in REPERES:
            L.append('    <path class="repere repere--%s" d="M%d %dH406"/>'
                     '<circle class="repere__pt repere--%s" cx="%d" cy="%d" r="2.6"/>' % (nom, x + 6, y, nom, x, y))
        L.append('  </g>')
    if zones:
        L.append('  <g class="zones">' + "".join(
            '<g class="zone" data-zone="%s"><circle class="zone__onde" cx="%d" cy="%d" r="%d"/>'
            '<circle class="zone__disque" cx="%d" cy="%d" r="%d"/></g>' % (nom, x, y, r, x, y, r)
            for nom, x, y, r in ZONES) + '</g>')
    L.append('</svg>')
    return "\n".join(("            " if i else "") + l for i, l in enumerate(L))


def ecrire(fichier, classe, svg):
    chemin = os.path.join(PAGES, fichier)
    page = open(chemin, encoding="utf-8").read()
    page, n = re.subn(r'<svg class="%s".*?</svg>' % classe, lambda m: svg, page, flags=re.S)
    if n != 1:
        sys.exit("dessin introuvable dans %s" % fichier)
    open(chemin, "w", encoding="utf-8").write(page)
    print("%s : dessin réécrit (%d Ko)" % (fichier, len(svg) // 1024))


if __name__ == "__main__":
    ecrire("index.html", "nerfs__svg", dessin())
    ecrire("la-chiropratique.html", "carte__svg",
           dessin("carte__svg", largeur=400, reperes=False, zones=True))
