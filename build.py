#!/usr/bin/env python3
"""
Générateur statique du site nuneschiropratique.fr
Aucune dépendance : Python 3.8+ suffit (déjà présent sur macOS et sur GitHub Actions).

    python3 build.py           -> construit dans dist/
    python3 build.py --serve   -> construit puis sert sur http://localhost:8000
"""
import base64
import hashlib
import html
import json
import os
import re
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
STATIC = os.path.join(ROOT, "static")
DIST = os.path.join(ROOT, "dist")

SITE = "https://nuneschiropratique.fr"
NAME = "Cabinet chiropratique Thomas Nunes"
PHONE = "06 88 75 54 52"
PHONE_E164 = "+33688755452"
EMAIL = "thomasnunes.chiropratique@gmail.com"
STREET = "56 boulevard de Strasbourg"
POSTAL = "31000"
CITY = "Toulouse"

NAV = [
    ("/", "Accueil"),
    ("/la-chiropratique/", "La chiropratique"),
    ("/a-propos/", "À propos de moi"),
    ("/avis/", "Avis"),
    ("/contact-et-acces/", "Contact et accès"),
    ("/tarifs-et-remboursements/", "Tarifs et remboursements"),
]

SOCIAL = [
    ("Instagram", "https://www.instagram.com/nuneschiropratique/"),
    ("Facebook", "https://www.facebook.com/profile.php?id=61585701608209"),
    ("LinkedIn", "https://www.linkedin.com/in/thomas-nunes-5853b5300/"),
]


def _json_str(v):
    return json.dumps(v, ensure_ascii=False)


def parse_front_matter(text):
    """--- key: value ... --- en tête de fichier."""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        block = text[3:end]
        text = text[end + 4:].lstrip("\n")
        for line in block.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text


def nav_markup(current):
    items = []
    for href, label in NAV:
        active = ' aria-current="page"' if href == current else ""
        cls = " is-active" if href == current else ""
        items.append(
            f'<li><a class="nav__link{cls}" href="{href}"{active}>'
            f'<span data-split-hover><span>{html.escape(label)}</span>'
            f'<span aria-hidden="true">{html.escape(label)}</span></span></a></li>'
        )
    return "\n          ".join(items)


def mobile_nav_markup(current):
    items = []
    for i, (href, label) in enumerate(NAV, 1):
        active = ' aria-current="page"' if href == current else ""
        items.append(
            f'<li><a href="{href}"{active}>'
            f'<span class="drawer__idx">{i:02d}</span>{html.escape(label)}</a></li>'
        )
    return "\n            ".join(items)


_GABARITS = {}


def gabarit(nom):
    """layout.html par défaut ; « layout: tunnel » -> layout-tunnel.html."""
    fichier = "layout.html" if not nom else "layout-%s.html" % nom
    if fichier not in _GABARITS:
        _GABARITS[fichier] = open(os.path.join(SRC, fichier), encoding="utf-8").read()
    return _GABARITS[fichier]


def build_page(path, layout=None):
    raw = open(path, encoding="utf-8").read()
    meta, body = parse_front_matter(raw)
    layout = gabarit(meta.get("layout"))

    slug = meta.get("slug", "")
    url = SITE + ("/" + slug + "/" if slug else "/")
    canonical = "/" + slug + "/" if slug else "/"
    # Carte de partage (lien envoyé sur WhatsApp, Messenger, par SMS…) : la
    # salle de soin, img/og-cabinet.jpg, 1200×630 comme l'annonce layout.html.
    # Elle est découpée dans photos/accueil.jpg (bande du haut, suspension en
    # osier entière ; pour sips, --cropOffset 0 voudrait dire « centré ») par
    # import-photos.py, à chaque nouvelle photo d'ouverture :
    #   sips --cropToHeightWidth 1050 2000 --cropOffset 20 0 -s format bmp \
    #        static/img/photos/accueil.jpg --out /tmp/og.bmp
    #   sips --resampleHeightWidth 630 1200 -s format jpeg \
    #        -s formatOptions 60 /tmp/og.bmp --out static/img/og-cabinet.jpg
    # Une page peut la remplacer avec « og_image: photos/xxx.jpg » dans son
    # en-tête (c'est le cas de /bilan/). L'ancienne carte, le logo sur fond
    # papier (img/og.png, tools/make-og.py), reste en réserve.
    og_image = SITE + "/img/" + meta.get("og_image", "og-cabinet.jpg")

    out = layout
    repl = {
        "TITLE": html.escape(meta.get("title", NAME)),
        "DESCRIPTION": html.escape(meta.get("description", "")),
        "CANONICAL": url,
        "OG_IMAGE": og_image,
        "OG_TYPE": meta.get("og_type", "website"),
        "BODY_CLASS": meta.get("body_class", ""),
        # « layout: tunnel » : la page de publicité. Le script y lit data-tunnel
        # pour transmettre les utm_ de l'annonce à l'agenda.
        "BODY_ATTRS": " data-tunnel" if meta.get("layout") == "tunnel" else "",
        "NAV": nav_markup(canonical),
        "MOBILE_NAV": mobile_nav_markup(canonical),
        "CONTENT": body,
        "EXTRA_HEAD": meta.get("extra_head", ""),
        "SCHEMA": meta.get("schema", ""),
        "YEAR": str(date.today().year),
        "PHONE": PHONE,
        "PHONE_E164": PHONE_E164,
        "EMAIL": EMAIL,
    }
    for k, v in repl.items():
        out = out.replace("{{" + k + "}}", v)

    # pagination éditoriale : page suivante dans l'ordre de lecture
    pager = ""
    order = [h for h, _l in NAV]
    if canonical in order:
        i = order.index(canonical)
        nxt = order[i + 1] if i + 1 < len(order) else None
        if nxt:
            label = dict(NAV)[nxt]
            pager = (
                '<nav class="pager" aria-label="Page suivante"><a class="pager__link" href="'
                + nxt + '">'
                + '<span class="pager__kicker">Page suivante</span>'
                + '<span class="pager__title">' + html.escape(label) + '</span>'
                + '<span class="pager__arrow" aria-hidden="true">&#8594;</span>'
                + "</a></nav>"
            )
    out = out.replace("<!--PAGER-->", pager)

    # fil d'Ariane structuré (généré depuis la navigation)
    if slug:
        label = next((l for h, l in NAV if h == canonical), meta.get("title", "").split(" - ")[0])
        crumb = (
            '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Accueil","item":"' + SITE + '/"},'
            '{"@type":"ListItem","position":2,"name":' + _json_str(label) + ',"item":"' + url + '"}]}'
        )
        out = out.replace(
            "<!--BREADCRUMB-->",
            '<script type="application/ld+json">' + crumb + "</script>",
        )

    # bloc JSON-LD propre à la page : FAQ générée depuis le balisage, ou
    # fichier src/schema/<slug>.json pour les cas particuliers
    extra = schema_faq(body)
    if not extra:
        schema_file = os.path.join(SRC, "schema", (slug or "index") + ".json")
        if os.path.exists(schema_file):
            extra = ('<script type="application/ld+json">'
                     + open(schema_file, encoding="utf-8").read().strip()
                     + "</script>")
    if extra:
        out = out.replace("<!--PAGE_SCHEMA-->", extra)

    out = injecter_srcset(out)
    out = out.replace("<!--CSP-->", politique_securite(out))

    if slug == "404":                      # GitHub Pages attend /404.html
        with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f:
            f.write(out)
        return canonical, meta

    dest_dir = os.path.join(DIST, slug) if slug else DIST
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    return canonical, meta


# Domaines tiers réellement nécessaires, et uniquement pour ce qu'ils font.
PRACTICEHUB = "https://thomasnuneschiropratique.neptune.practicehub.io"
FORMSPREE = "https://formspree.io"


def politique_securite(page_html):
    """Construit l'en-tête Content-Security-Policy de la page.

    Le principe : on part de « rien n'est autorisé » (default-src 'none') et
    on n'ouvre que ce qui sert vraiment. Si une balise venait à charger un
    script d'ailleurs — extension malveillante, copier-coller distrait,
    injection — le navigateur refuserait de l'exécuter.

    Les scripts en ligne sont autorisés par leur empreinte, calculée ici à
    chaque construction : impossible qu'elle se périme, et impossible
    d'exécuter un autre script en ligne que celui-ci.

    Note : placé en <meta>, le CSP ne gère ni frame-ancestors ni report-uri,
    qui n'existent qu'en en-tête HTTP. GitHub Pages ne permettant pas de
    définir d'en-têtes, c'est la meilleure protection disponible ici.
    """
    empreintes = []
    for corps in re.findall(r"<script>(.*?)</script>", page_html, re.S):
        h = hashlib.sha256(corps.encode("utf-8")).digest()
        empreintes.append("'sha256-" + base64.b64encode(h).decode("ascii") + "'")

    directives = [
        ("default-src", "'none'"),
        ("script-src", " ".join(["'self'"] + empreintes)),
        ("style-src", "'self'"),
        ("img-src", "'self' data:"),
        ("font-src", "'self'"),
        ("connect-src", "'self' " + FORMSPREE),
        # 'self' : après une réservation, PracticeHub redirige son cadre vers
        # /reservation-confirmee/ (notre site). Sans 'self', le navigateur
        # bloque cette page dans le cadre et le patient ne voit aucune
        # confirmation.
        ("frame-src", "'self' " + PRACTICEHUB + " https://www.google.com https://maps.google.com"),
        ("form-action", "'self' " + FORMSPREE),
        ("base-uri", "'self'"),
        ("manifest-src", "'self'"),
    ]
    contenu = "; ".join("%s %s" % (k, v) for k, v in directives)
    # L'attribut est délimité par des guillemets doubles : les apostrophes de
    # 'self' et 'none' doivent rester littérales, sans quoi la politique est
    # invalide. On n'échappe donc que &, < et >.
    assert '"' not in contenu, "guillemet double dans la politique"
    return ('<meta http-equiv="Content-Security-Policy" content="'
            + html.escape(contenu, quote=False) + '">')


def schema_faq(contenu):
    """Données structurées FAQPage, extraites du balisage de la page.

    On lit les questions/réponses réellement affichées plutôt que de tenir
    une liste séparée : les deux ne peuvent donc pas diverger. C'est une
    erreur classique — Google sanctionne un balisage qui annonce autre chose
    que ce que voit le visiteur.
    """
    items = re.findall(
        r'<button class="faq__q".*?>(.*?)<span class="faq__sign".*?'
        r'<div class="faq__a"[^>]*><div>(.*?)</div></div>',
        contenu, re.S)
    if not items:
        return ""

    def texte(html_brut):
        t = re.sub(r"<[^>]+>", " ", html_brut)
        t = html.unescape(t)
        t = t.replace("\u00a0", " ")
        return re.sub(r"\s+", " ", t).strip()

    entrees = []
    for question, reponse in items:
        q, r = texte(question), texte(reponse)
        if not q or not r:
            continue
        entrees.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": r},
        })
    if not entrees:
        return ""

    bloc = {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": entrees}
    return ('<script type="application/ld+json">'
            + json.dumps(bloc, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def dimensions_jpeg(chemin):
    """Largeur et hauteur d'un JPEG, sans bibliothèque externe.

    On parcourt les marqueurs jusqu'au segment SOF (Start Of Frame), qui
    porte les dimensions. Évite d'avoir à installer Pillow — la construction
    doit rester exécutable partout, y compris sur le serveur de GitHub.
    """
    try:
        with open(chemin, "rb") as f:
            if f.read(2) != b"\xff\xd8":
                return None
            while True:
                octet = f.read(1)
                if not octet:
                    return None
                if octet != b"\xff":
                    continue
                while octet == b"\xff":
                    octet = f.read(1)
                marqueur = octet[0]
                if marqueur in (0xD8, 0xD9) or 0xD0 <= marqueur <= 0xD7:
                    continue
                longueur = int.from_bytes(f.read(2), "big")
                # SOF0..SOF15, hors marqueurs de table (C4, C8, CC)
                if 0xC0 <= marqueur <= 0xCF and marqueur not in (0xC4, 0xC8, 0xCC):
                    f.read(1)                       # précision
                    hauteur = int.from_bytes(f.read(2), "big")
                    largeur = int.from_bytes(f.read(2), "big")
                    return largeur, hauteur
                f.seek(longueur - 2, 1)
    except OSError:
        return None


def injecter_srcset(html):
    """Ajoute srcset/sizes aux photos qui possèdent des variantes.

    On cherche les <img> portant un attribut data-sizes et dont le fichier
    a des déclinaisons -800 / -1200 dans static/img/photos/. Le navigateur
    choisit alors la largeur adaptée à l'écran plutôt que de télécharger
    systématiquement la version 2000 px.

    Les variantes sont fabriquées par import-photos.py, sur le poste de
    travail : la construction du site reste sans dépendance.
    """
    def remplacer(m):
        tag = m.group(0)
        src = re.search(r'src="(/img/photos/([^"]+?)\.jpg)"', tag)
        taille = re.search(r'data-sizes="([^"]*)"', tag)
        if not src:
            return tag

        base = src.group(2)
        dossier = os.path.join(STATIC, "img", "photos")
        original = os.path.join(dossier, base + ".jpg")
        dim = dimensions_jpeg(original)

        # width/height recalés sur le fichier réel : le navigateur réserve
        # la bonne place et la page ne sursaute pas au chargement
        if dim:
            tag = re.sub(r'width="\d+"', 'width="%d"' % dim[0], tag)
            tag = re.sub(r'height="\d+"', 'height="%d"' % dim[1], tag)

        if not taille:
            return tag
        tag = tag.replace(' data-sizes="%s"' % taille.group(1), '')

        # chaque variante est décrite par sa largeur mesurée, pas supposée
        vues, entrees = set(), []
        for suffixe in ("-800", "-1200", ""):
            chemin = os.path.join(dossier, base + suffixe + ".jpg")
            d = dimensions_jpeg(chemin)
            if not d or d[0] in vues:
                continue
            # une variante agrandie ne sert à rien : on l'écarte, de même
            # qu'une variante plus lourde que l'original, plus grand
            if suffixe and dim and d[0] >= dim[0]:
                continue
            if suffixe and os.path.getsize(chemin) >= os.path.getsize(original):
                continue
            vues.add(d[0])
            entrees.append("/img/photos/%s%s.jpg %dw" % (base, suffixe, d[0]))
        if len(entrees) < 2:
            return tag

        entrees.sort(key=lambda e: int(e.rsplit(" ", 1)[1][:-1]))
        return tag[:-1].rstrip() + ' srcset="%s" sizes="%s">' % (
            ", ".join(entrees), taille.group(1))

    return re.sub(r'<img\b[^>]*>', remplacer, html)


def elaguer_photos():
    """Ne publie que les photos réellement affichées par une page.

    Les huit emplacements restent dans le dépôt — ce sont les cases où
    déposer les vraies photos — mais une image qu'aucune page n'utilise n'a
    rien à faire en ligne. Le tri se fait d'après le HTML construit : si une
    photo est remise sur une page, elle repart automatiquement.
    """
    dossier = os.path.join(DIST, "img", "photos")
    if not os.path.isdir(dossier):
        return 0, 0

    utilisees = set()
    for dirpath, _d, fichiers in os.walk(DIST):
        for fn_ in fichiers:
            if not fn_.endswith(".html"):
                continue
            texte = open(os.path.join(dirpath, fn_), encoding="utf-8").read()
            for chemin in re.findall(r'/img/photos/([\w.-]+\.jpg)', texte):
                utilisees.add(chemin)

    retirees = octets = 0
    for fichier in os.listdir(dossier):
        if not fichier.endswith(".jpg"):
            continue
        if fichier not in utilisees:
            chemin = os.path.join(dossier, fichier)
            octets += os.path.getsize(chemin)
            os.remove(chemin)
            retirees += 1
    return retirees, octets


def copytree(src, dst):
    for dirpath, _dirnames, filenames in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        target = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(target, exist_ok=True)
        for fn in filenames:
            # notes de travail : elles restent dans le dépôt, pas dans le site publié
            if fn == ".DS_Store" or fn.endswith(".md"):
                continue
            shutil.copy2(os.path.join(dirpath, fn), os.path.join(target, fn))


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    copytree(STATIC, DIST)


    pages = sorted(
        os.path.join(SRC, "pages", f)
        for f in os.listdir(os.path.join(SRC, "pages"))
        if f.endswith(".html")
    )
    built = []
    for p in pages:
        canonical, meta = build_page(p)
        built.append((canonical, meta))
        print("  ·", canonical)

    # ---- sitemap.xml ----
    today = date.today().isoformat()
    urls = []
    for canonical, meta in built:
        if meta.get("noindex") == "true":
            continue
        prio = meta.get("priority", "0.7")
        urls.append(
            "  <url>\n"
            f"    <loc>{SITE}{canonical}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{meta.get('changefreq', 'monthly')}</changefreq>\n"
            f"    <priority>{prio}</priority>\n"
            "  </url>"
        )
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    # ---- cache-busting sur css/js ----
    import hashlib

    stamps = {}
    for rel in ("css/site.css", "js/site.js"):
        fp = os.path.join(DIST, rel)
        if os.path.exists(fp):
            stamps[rel] = hashlib.md5(open(fp, "rb").read()).hexdigest()[:8]
    for dirpath, _d, files in os.walk(DIST):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(dirpath, fn)
            t = open(fp, encoding="utf-8").read()
            for rel, h in stamps.items():
                t = t.replace("/" + rel + '"', "/" + rel + "?v=" + h + '"')
            open(fp, "w", encoding="utf-8").write(t)

    retirees, octets = elaguer_photos()
    if retirees:
        print(f"  ({retirees} photos non utilisées écartées de la publication, "
              f"{octets // 1024} Ko)")

    print(f"\n✓ {len(built)} pages construites dans dist/")

    if "--serve" in sys.argv:
        import functools
        import http.server
        import socketserver

        os.chdir(DIST)
        handler = functools.partial(CleanURLHandler, directory=DIST)
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("→ http://localhost:8000  (Ctrl+C pour arrêter)")
            httpd.serve_forever()


class CleanURLHandler(getattr(__import__("http.server", fromlist=["x"]), "SimpleHTTPRequestHandler")):
    def translate_path(self, path):
        p = super().translate_path(path)
        if os.path.isdir(p):
            return os.path.join(p, "index.html")
        return p

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    main()
