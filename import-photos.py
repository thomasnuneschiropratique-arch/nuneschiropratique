#!/usr/bin/env python3
"""
Importe les photos du cabinet, quel que soit leur format.

    python3 import-photos.py photos-a-importer

Accepte HEIC (photos iPhone), JPEG, PNG, TIFF, WebP. Chaque fichier est
converti en JPEG, réduit s'il dépasse 2000 px (jamais agrandi), et
enregistré à l'emplacement du site qui lui correspond, avec ses variantes
pour petits écrans.

Le classement se fait sur le NOM du fichier : une photo dont le nom contient
« portrait » va à l'emplacement portrait, « salle » ou « cabinet » à la vue
du cabinet, « ajustement » au geste. C'est plus sûr que l'ordre alphabétique,
qui avait déjà envoyé un portrait sur la page d'accueil.

Pour forcer un emplacement précis :

    python3 import-photos.py --slot accueil ~/Desktop/ma-photo.jpg

N'utilise que `sips`, fourni avec macOS. Rien à installer.
"""
import os
import shutil
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(RACINE, "static", "img", "photos")
# image de partage (WhatsApp, Messenger, SMS…), tirée de la photo d'ouverture
OG = os.path.join(RACINE, "static", "img", "og-cabinet.jpg")
MAX_EDGE = 2000
# Attention, sips a sa propre échelle : « formatOptions 60 » donne un JPEG de
# qualité 85 environ (lue dans les tables de quantification du fichier).
# L'ancien réglage de 80 donnait une qualité 93 environ : des fichiers
# presque moitié plus lourds, pour une différence invisible à l'œil.
QUALITY = 60
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
    """mode 'fit'   : réduit le plus grand côté à `edge`
       mode 'width' : réduit la largeur à `edge` — c'est ce qu'attend srcset
       edge None    : garde la taille, ne fait que convertir en JPEG.

    Attention : « sips -Z » et « --resampleWidth » AGRANDISSENT une image plus
    petite que la cible. Les appels ci-dessous ne les utilisent donc que pour
    réduire (voir convert)."""
    if edge is None:
        dimension = []
    elif mode == "fit":
        dimension = ["-Z", str(edge)]
    else:
        dimension = ["--resampleWidth", str(edge)]
    subprocess.run(
        ["sips"] + dimension +
        ["-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         src, "--out", dest],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    return os.path.getsize(dest)


def _dimensions(chemin):
    """(largeur, hauteur) en pixels, lues par sips."""
    r = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", chemin],
                       capture_output=True, text=True)
    valeurs = {}
    for ligne in r.stdout.split("\n"):
        if ":" in ligne and ligne.strip().startswith("pixel"):
            cle, val = ligne.split(":", 1)
            valeurs[cle.strip()] = int(val)
    return valeurs.get("pixelWidth"), valeurs.get("pixelHeight")


def _jpeg_sans_metadonnees(chemin):
    """Vrai pour un JPEG qui ne porte ni EXIF, ni XMP, ni IPTC, ni commentaire.

    Ces blocs peuvent contenir la position GPS, la date ou l'appareil : on ne
    copie donc tel quel qu'un JPEG qui n'en a pas, ce qui évite toute perte.
    Les autres passent par sips, qui NE retire PAS ces données : la position
    GPS est donc contrôlée après coup, sur chaque fichier produit (voir
    _position_gps). Seuls sont admis ici JFIF (APP0), le profil de couleur
    (APP2) et Adobe (APP14).
    """
    try:
        with open(chemin, "rb") as f:
            d = f.read()
    except OSError:
        return False
    if d[:2] != b"\xff\xd8":
        return False
    pos = 2
    while pos + 4 <= len(d) and d[pos] == 0xFF:
        marqueur = d[pos + 1]
        if marqueur == 0xDA:                 # début des données de l'image
            return True
        if marqueur == 0xFE or (0xE0 <= marqueur <= 0xEF
                                and marqueur not in (0xE0, 0xE2, 0xEE)):
            return False
        pos += 2 + int.from_bytes(d[pos + 2:pos + 4], "big")
    return False


def _position_gps(chemin):
    """Vrai si le JPEG porte une position GPS (balise 0x8825 de son EXIF).

    Le dépôt du site est public : une photo prise avec la localisation
    activée dévoilerait l'endroit où elle a été prise.
    """
    try:
        with open(chemin, "rb") as f:
            d = f.read()
    except OSError:
        return False
    pos = 2
    while pos + 4 <= len(d) and d[pos] == 0xFF:
        marqueur = d[pos + 1]
        longueur = int.from_bytes(d[pos + 2:pos + 4], "big")
        if marqueur == 0xDA:
            return False
        bloc = d[pos + 4:pos + 2 + longueur]
        if marqueur == 0xE1 and bloc[:6] == b"Exif\x00\x00":
            tiff = bloc[6:]
            ordre = "little" if tiff[:2] == b"II" else "big"
            ifd = int.from_bytes(tiff[4:8], ordre)
            n = int.from_bytes(tiff[ifd:ifd + 2], ordre)
            for k in range(n):
                e = ifd + 2 + 12 * k
                if int.from_bytes(tiff[e:e + 2], ordre) == 0x8825:
                    return True
        pos += 2 + longueur
    return False


def convert(src, dest):
    """Convertit en JPEG web, puis produit les variantes pour petits écrans.

    On n'agrandit jamais une image : cela n'ajoute aucun détail, seulement
    du poids. Une photo plus grande que 2000 px est réduite à 2000 px ; une
    photo plus petite garde sa taille. Si c'est déjà un JPEG sans
    métadonnées, il est copié tel quel : le réencoder ne ferait que perdre
    un peu de finesse.

    Si le fichier dépasse ~450 Ko, on redescend la qualité : une page qui
    s'affiche vite compte plus que 2 % de finesse.
    """
    largeur_src, hauteur_src = _dimensions(src)
    if not largeur_src or not hauteur_src:
        sys.exit("Image illisible : " + src)
    trop_grande = max(largeur_src, hauteur_src) > MAX_EDGE
    edge = MAX_EDGE if trop_grande else None

    # Tout est fabriqué à part, dans un dossier temporaire : si la photo est
    # refusée (position GPS), celle qui est en place sur le site ne bouge pas.
    atelier = tempfile.mkdtemp(prefix="import-photo-")
    try:
        tmp = os.path.join(atelier, os.path.basename(dest))
        if not trop_grande and _jpeg_sans_metadonnees(src):
            shutil.copyfile(src, tmp)
            taille = os.path.getsize(tmp)
            if taille > TARGET_BYTES:
                taille = _sips(src, tmp, edge, QUALITY)
        else:
            taille = _sips(src, tmp, edge, QUALITY)
        for quality in (55, 50, 45):
            if taille <= TARGET_BYTES:
                break
            taille = _sips(src, tmp, edge, quality)

        # Variantes : seulement plus étroites que la photo, et seulement si
        # elles pèsent moins qu'elle. Sinon le navigateur prendrait autant de
        # poids pour moins de détail.
        tbase, ext = os.path.splitext(tmp)
        large, _haut = _dimensions(tmp)
        gardees = []
        for largeur in LARGEURS:
            variante = "%s-%d%s" % (tbase, largeur, ext)
            if large and largeur < large:
                if _sips(tmp, variante, largeur, QUALITY, mode="width") < taille:
                    gardees.append(largeur)
                    continue
            if os.path.exists(variante):
                os.remove(variante)

        produits = [tmp] + ["%s-%d%s" % (tbase, l, ext) for l in gardees]
        if any(_position_gps(f) for f in produits):
            sys.exit("Cette photo contient sa position GPS : elle n'a pas été importée, "
                     "la photo actuelle du site est conservée.\n"
                     "Sur l'iPhone : Partager > Options > désactiver « Localisation », "
                     "enregistrer la photo, puis la réimporter.")

        # Acceptée : on remplace la photo du site et ses variantes ; une
        # ancienne variante devenue inutile est effacée.
        base, _ext = os.path.splitext(dest)
        shutil.move(tmp, dest)
        for largeur in LARGEURS:
            cible = "%s-%d%s" % (base, largeur, ext)
            if largeur in gardees:
                shutil.move("%s-%d%s" % (tbase, largeur, ext), cible)
            elif os.path.exists(cible):
                os.remove(cible)
    finally:
        shutil.rmtree(atelier, ignore_errors=True)
    return taille, large


def apercu_de_partage(photo):
    """Refait l'image de partage (WhatsApp, Messenger, SMS…), img/og-cabinet.jpg,
    à partir de la photo d'ouverture : bande du haut, au format 1200×630.
    Le cadre part de 1,5 % sous le haut de la photo : sur accueil.jpg, la
    suspension en osier reste entière. Attention, pour sips, un décalage de 0
    veut dire « cadre centré » : le décalage vaut donc au moins 1."""
    largeur, hauteur = _dimensions(photo)
    bande = round(largeur * 630 / 1200) if largeur else 0
    decalage = max(1, round(hauteur * 0.015)) if hauteur else 0
    if not bande or not hauteur or bande + decalage > hauteur:
        print("     ! Aperçu de partage à refaire à la main : voir build.py.")
        return
    tmp = os.path.join(tempfile.gettempdir(), "og-cabinet.bmp")
    subprocess.run(["sips", "--cropToHeightWidth", str(bande), str(largeur), "--cropOffset", str(decalage), "0",
                    "-s", "format", "bmp", photo, "--out", tmp], check=True, capture_output=True)
    subprocess.run(["sips", "--resampleHeightWidth", "630", "1200", "-s", "format", "jpeg",
                    "-s", "formatOptions", str(QUALITY), tmp, "--out", OG], check=True, capture_output=True)
    os.remove(tmp)
    print("     ✓ aperçu de partage refait : img/og-cabinet.jpg")


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
    if cle == "accueil":
        apercu_de_partage(os.path.join(DEST, fichier))


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
