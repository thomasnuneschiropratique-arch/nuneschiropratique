#!/usr/bin/env python3
"""
Importe les photos du cabinet, quel que soit leur format.

    python3 import-photos.py photos-a-importer

Accepte HEIC (photos iPhone), JPEG, PNG, TIFF, WebP. Chaque fichier est
converti en JPEG, redimensionné, et enregistré à l'emplacement du site qui
lui correspond, avec ses variantes pour petits écrans.

Le classement se fait sur le NOM du fichier : une photo dont le nom contient
« portrait » va à l'emplacement portrait, « salle » ou « cabinet » à la vue
du cabinet, « ajustement » au geste. C'est plus sûr que l'ordre alphabétique,
qui avait déjà envoyé un portrait sur la page d'accueil.

Pour forcer un emplacement précis :

    python3 import-photos.py --slot accueil ~/Desktop/ma-photo.jpg

N'utilise que `sips`, fourni avec macOS. Rien à installer.
"""
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(RACINE, "static", "img", "photos")
MAX_EDGE = 2000
QUALITY = 80
TARGET_BYTES = 450 * 1024
LARGEURS = (800, 1200)

# Emplacement -> (fichier, où il apparaît, mots-clés reconnus dans le nom source)
SLOTS = {
    "accueil": (
        "accueil.jpg",
        "Accueil - grande image d'ouverture",
        ("salle", "cabinet"),
    ),
    "accueil-chiropratique": (
        "accueil-chiropratique.jpg",
        "Accueil - « Qu'est ce que la chiropratique ? » (portrait)",
        ("=ajustement",),
    ),
    "accueil-approche": (
        "accueil-approche.jpg",
        "Accueil - « Mon approche » (portrait)",
        ("=thomas-ajustement-cervical",),
    ),
    "accueil-cabinet": (
        "accueil-cabinet.jpg",
        "Accueil - collage de « Mon approche » (vue large de la salle)",
        ("=ajustement first",),
    ),
    "chiropratique-ajustement": (
        "chiropratique-ajustement.jpg",
        "La chiropratique - à côté du « système nerveux » (portrait)",
        ("=ajustement droit",),
    ),
    "chiropratique-explication": (
        "chiropratique-explication.jpg",
        "La chiropratique - à côté de « Pourquoi la chiropratique ? »",
        ("colonne", "explication"),
    ),
    "a-propos-portrait": (
        "a-propos-portrait.jpg",
        "A propos de moi - « Qui suis-je ? » (portrait)",
        ("portrait",),
    ),
    "a-propos-examen": (
        "a-propos-examen.jpg",
        "A propos de moi - « Ce que vous trouverez au cabinet »",
        ("posture", "examen"),
    ),
}

EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp"}


def _sips(src, dest, edge, quality, mode="fit"):
    """mode 'fit'   : contraint le plus grand côté (plafond général)
       mode 'width' : contraint la largeur — c'est ce qu'attend srcset."""
    dimension = ["-Z", str(edge)] if mode == "fit" else ["--resampleWidth", str(edge)]
    subprocess.run(
        ["sips"] + dimension +
        ["-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         src, "--out", dest],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    return os.path.getsize(dest)


def _largeur(chemin):
    r = subprocess.run(["sips", "-g", "pixelWidth", chemin],
                       capture_output=True, text=True)
    for ligne in r.stdout.split("\n"):
        if "pixelWidth" in ligne:
            return int(ligne.split(":")[1])
    return None


def convert(src, dest):
    """Convertit en JPEG web, puis produit les variantes pour petits écrans.

    On vise 2000 px et une qualité de 80. Si le fichier dépasse ~450 Ko, on
    redescend la qualité : une page qui s'affiche vite compte plus que 2 %
    de finesse. On n'agrandit jamais une image — cela n'ajoute aucun détail.
    """
    taille = _sips(src, dest, MAX_EDGE, QUALITY)
    for quality in (72, 64, 56):
        if taille <= TARGET_BYTES:
            break
        taille = _sips(src, dest, MAX_EDGE, quality)

    base, ext = os.path.splitext(dest)
    large = _largeur(dest)
    for largeur in LARGEURS:
        variante = "%s-%d%s" % (base, largeur, ext)
        if large and largeur >= large:
            if os.path.exists(variante):
                os.remove(variante)
            continue
        _sips(dest, variante, largeur, 78, mode="width")
    return taille, large


def deviner(nom_fichier):
    """Devine l'emplacement d'après le nom du fichier source.

    Un mot-clé préfixé de « = » demande une correspondance exacte. C'est
    indispensable quand plusieurs fichiers se ressemblent : « ajustement »
    est contenu dans « ajustement droit » et « thomas-ajustement-cervical »,
    et raflerait le mauvais fichier.

    Les correspondances exactes sont examinées avant les approchantes, pour
    qu'un nom précis l'emporte toujours sur un simple fragment.
    """
    nom = os.path.splitext(os.path.basename(nom_fichier))[0].lower()
    for cle, (_f, _d, mots) in SLOTS.items():
        if any(m.startswith("=") and nom == m[1:] for m in mots):
            return cle
    for cle, (_f, _d, mots) in SLOTS.items():
        if any(not m.startswith("=") and m in nom for m in mots):
            return cle
    return None


def importer(src, cle):
    fichier, description, _ = SLOTS[cle]
    taille, large = convert(src, os.path.join(DEST, fichier))
    print("  ✓ %-28s -> %-20s %4d px  %3d Ko" % (
        os.path.basename(src)[:28], fichier, large or 0, taille // 1024))
    print("     %s" % description)


def main():
    args = [a for a in sys.argv[1:] if a != "--yes"]
    assume_yes = "--yes" in sys.argv[1:]

    if "--slot" in args:
        i = args.index("--slot")
        try:
            cle, src = args[i + 1], os.path.expanduser(args[i + 2])
        except IndexError:
            sys.exit("Usage : --slot <%s> <fichier>" % "|".join(SLOTS))
        if cle not in SLOTS:
            sys.exit("Emplacement inconnu. Au choix : %s" % ", ".join(SLOTS))
        if not os.path.isfile(src):
            sys.exit("Fichier introuvable : " + src)
        importer(src, cle)
        print("\nRelance ensuite : python3 build.py")
        return

    if not args:
        sys.exit(__doc__)

    dossier = os.path.expanduser(args[0])
    if not os.path.isdir(dossier):
        sys.exit("Dossier introuvable : " + dossier)

    fichiers = sorted(
        os.path.join(dossier, f) for f in os.listdir(dossier)
        if os.path.splitext(f)[1].lower() in EXTS and not f.startswith(".")
    )
    if not fichiers:
        sys.exit("Aucune image trouvée dans " + dossier)

    # une photo par emplacement : la première dont le nom correspond
    choix, restants = {}, []
    for f in fichiers:
        cle = deviner(f)
        if cle and cle not in choix:
            choix[cle] = f
        else:
            restants.append(f)

    print("Correspondance proposée :\n")
    for cle, (fichier, description, _) in SLOTS.items():
        src = choix.get(cle)
        if src:
            print("  %-28s -> %s" % (os.path.basename(src)[:28], fichier))
            print("     %s" % description)
        else:
            print("  (aucune photo reconnue)       -> %s" % fichier)
            print("     %s — emplacement inchangé" % description)
    if restants:
        print("\n  Non utilisées : %s" % ", ".join(os.path.basename(f) for f in restants))
        print("  Pour en placer une : --slot <%s> <fichier>" % "|".join(SLOTS))

    if not choix:
        sys.exit("\nAucun nom de fichier reconnu. Utilise --slot pour choisir.")

    if not assume_yes:
        print()
        if input("Confirmer ? [o/N] ").strip().lower() not in ("o", "oui", "y", "yes"):
            sys.exit("Annulé, rien n'a été modifié.")

    print()
    for cle, src in choix.items():
        importer(src, cle)
    print("\nRelance ensuite : python3 build.py")


if __name__ == "__main__":
    main()
