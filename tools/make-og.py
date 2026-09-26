#!/usr/bin/env python3
"""
Fabrique l'image de partage (Open Graph / Twitter), 1200x630.

C'est l'image qui s'affiche quand on colle le lien du site dans un message,
sur Facebook, LinkedIn ou WhatsApp. Elle doit exister même sans photos.

    python3 tools/make-og.py        -> static/img/og.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import png

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(RACINE, 'static', 'img', 'logo-lockup.png')
SORTIE = os.path.join(RACINE, 'static', 'img', 'og.png')

L, H = 1200, 630
PAPIER = (251, 250, 247)
PETROLE = (48, 90, 89)


def main():
    lw, lh, lp = png.read(LOGO)

    toile = bytearray(L * H * 4)
    for i in range(L * H):
        toile[i * 4:i * 4 + 4] = bytes(PAPIER) + b'\xff'

    def trait(y, hauteur, couleur, alpha=255):
        for yy in range(y, min(H, y + hauteur)):
            for xx in range(L):
                d = (yy * L + xx) * 4
                for c in range(3):
                    toile[d + c] = (couleur[c] * alpha + toile[d + c] * (255 - alpha)) // 255

    # bandeau pétrole en pied, et filet fin au-dessus : deux repères de marque
    trait(H - 14, 14, PETROLE)
    trait(H - 15, 1, PETROLE, 90)

    # logo centré, largeur confortable
    cible = 560
    nh = max(1, round(lh * cible / lw))
    petit = png.resize(lw, lh, lp, cible, nh)

    ox, oy = (L - cible) // 2, (H - 14 - nh) // 2
    for y in range(nh):
        for x in range(cible):
            s = (y * cible + x) * 4
            a = petit[s + 3]
            if not a:
                continue
            d = ((oy + y) * L + (ox + x)) * 4
            for c in range(3):
                toile[d + c] = (petit[s + c] * a + toile[d + c] * (255 - a)) // 255

    png.write(SORTIE, L, H, toile)
    print('✓ %s  (%d x %d, %d Ko)' % (
        os.path.relpath(SORTIE, RACINE), L, H, os.path.getsize(SORTIE) // 1024))


if __name__ == '__main__':
    main()
