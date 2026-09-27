"""
Traits effilés, dans l'esprit du logo : un nerf est épais à sa racine et
s'affine jusqu'à un fil. Le SVG ne sait tracer que des traits d'épaisseur
constante ; on dessine donc chaque nerf comme une forme pleine, calculée
de part et d'autre de sa ligne médiane.

Utilisé par tools/dessin-nerfs.py et tools/dessin-vase.py. Sans dépendance.
"""
import math
import re


def lire_chemin(d):
    """Découpe un chemin SVG absolu (M, C, L, H, V) en segments cubiques."""
    jetons = re.findall(r"[MCLHV]|-?\d*\.?\d+", d)
    segs, i, cmd = [], 0, None
    x = y = 0.0
    while i < len(jetons):
        t = jetons[i]
        if t in "MCLHV":
            cmd = t
            i += 1
            continue
        n = lambda k: float(jetons[i + k])
        if cmd == "M":
            x, y = n(0), n(1)
            i += 2
        elif cmd == "C":
            p = [(x, y), (n(0), n(1)), (n(2), n(3)), (n(4), n(5))]
            segs.append(p)
            x, y = p[3]
            i += 6
        elif cmd in "LHV":
            if cmd == "L":
                nx, ny = n(0), n(1)
                i += 2
            elif cmd == "H":
                nx, ny = n(0), y
                i += 1
            else:
                nx, ny = x, n(0)
                i += 1
            segs.append([(x, y), (x + (nx - x) / 3, y + (ny - y) / 3),
                         (x + 2 * (nx - x) / 3, y + 2 * (ny - y) / 3), (nx, ny)])
            x, y = nx, ny
    return segs


def _point(s, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = s
    u = 1 - t
    return (u * u * u * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3,
            u * u * u * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3)


def echantillons(d, n=28):
    """n points régulièrement espacés le long du chemin (à la longueur)."""
    fins = []
    for s in lire_chemin(d):
        for k in range(40):
            fins.append(_point(s, k / 40))
    fins.append(_point(lire_chemin(d)[-1], 1))
    cumul = [0.0]
    for a, b in zip(fins, fins[1:]):
        cumul.append(cumul[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cumul[-1] or 1
    pts, j = [], 0
    for k in range(n):
        cible = total * k / (n - 1)
        while j < len(cumul) - 2 and cumul[j + 1] < cible:
            j += 1
        seg = (cumul[j + 1] - cumul[j]) or 1
        f = (cible - cumul[j]) / seg
        a, b = fins[j], fins[j + 1]
        pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return pts


def _lisse(pts):
    """Courbe douce passant par les milieux : M, puis Q point -> milieu."""
    f = lambda p: "%.1f %.1f" % p
    mil = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    out = ["L" + f(mil(pts[0], pts[1]))]
    for i in range(1, len(pts) - 1):
        out.append("Q" + f(pts[i]) + " " + f(mil(pts[i], pts[i + 1])))
    out.append("L" + f(pts[-1]))
    return "".join(out)


def effile(d, debut, fin, n=28, galbe=0.0, courbe=1.0):
    """Forme pleine autour de la ligne médiane d.

    debut, fin : épaisseurs aux deux bouts
    galbe      : renflement ajouté au milieu (0 = aucun)
    courbe     : > 1 garde l'épaisseur plus longtemps avant de s'affiner
    """
    pts = echantillons(d, n)
    gauche, droite = [], []
    for i, p in enumerate(pts):
        s = i / (len(pts) - 1)
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = debut + (fin - debut) * (s ** courbe) + galbe * math.sin(math.pi * s)
        gauche.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        droite.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    retour = list(reversed(droite))
    return ("M%.1f %.1f" % gauche[0] + _lisse(gauche)
            + "L%.1f %.1f" % retour[0] + _lisse(retour) + "Z")
