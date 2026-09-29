#!/usr/bin/env python3
"""Contrôles avant mise en ligne : liens internes, images, métadonnées, accessibilité de base."""
import base64, hashlib, os, re, sys, json, html

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
errors, warnings = [], []

pages = []
for dp, _d, fs in os.walk(DIST):
    for f in fs:
        if f.endswith(".html"):
            pages.append(os.path.join(dp, f))

def rel(p): return os.path.relpath(p, DIST)

titles, descs = {}, {}
for p in pages:
    t = open(p, encoding="utf-8").read()
    name = rel(p)

    m = re.search(r"<title>(.*?)</title>", t, re.S)
    title = m.group(1).strip() if m else ""
    if not title: errors.append(f"{name}: <title> manquant")
    elif len(title) > 70: warnings.append(f"{name}: title {len(title)} car. (>70)")
    titles.setdefault(title, []).append(name)

    m = re.search(r'<meta name="description" content="(.*?)"', t, re.S)
    d = m.group(1).strip() if m else ""
    if not d: errors.append(f"{name}: meta description manquante")
    elif not (70 <= len(d) <= 175): warnings.append(f"{name}: description {len(d)} car. (viser 120-160)")
    descs.setdefault(d, []).append(name)

    if t.count("<h1") != 1: errors.append(f"{name}: {t.count('<h1')} <h1> (attendu 1)")
    if '<html lang="fr">' not in t: errors.append(f"{name}: lang manquant")
    if 'rel="canonical"' not in t: errors.append(f"{name}: canonical manquant")

    # images : fichier présent + alt présent
    for tag in re.findall(r"<img\b[^>]*>", t):
        src = re.search(r'src="([^"]+)"', tag)
        if not src: continue
        s = src.group(1)
        if s.startswith("/"):
            fp = os.path.join(DIST, s.lstrip("/").split("?")[0])
            if not os.path.exists(fp): errors.append(f"{name}: image absente {s}")
        if 'alt=' not in tag: errors.append(f"{name}: <img> sans alt -> {s}")
        if not re.search(r'width="\d+"', tag) or not re.search(r'height="\d+"', tag):
            warnings.append(f"{name}: <img> sans width/height (CLS) -> {s}")

    # liens internes
    for href in re.findall(r'href="(/[^"#?]*)"', t):
        target = href.lstrip("/")
        cand = [os.path.join(DIST, target), os.path.join(DIST, target, "index.html")]
        if not any(os.path.exists(c) for c in cand):
            errors.append(f"{name}: lien interne cassé -> {href}")

    # JSON-LD valide
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(block)
        except Exception as e: errors.append(f"{name}: JSON-LD invalide ({e})")

    # cibles externes sécurisées
    for tag in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', t):
        if "noopener" not in tag: errors.append(f"{name}: target=_blank sans rel=noopener")

    # NAP cohérent
    if "56 boulevard de Strasbourg" in t and "31000" not in t:
        warnings.append(f"{name}: adresse partielle")

for t, ps in titles.items():
    if len(ps) > 1: errors.append(f"title dupliqué sur {ps}")
for d, ps in descs.items():
    if len(ps) > 1: errors.append(f"description dupliquée sur {ps}")

for f in ("sitemap.xml", "robots.txt", "CNAME", "404.html", ".nojekyll",
          "site.webmanifest", "img/og.png", "css/fonts.css"):
    if not os.path.exists(os.path.join(DIST, f)): errors.append(f"fichier manquant : {f}")

# --- adresses de l'ancien site : elles ne doivent pas disparaître ---
# Ces adresses sont connues de Google, de la fiche Google Business, des
# publicités, et surtout de PracticeHub, qui renvoie les patients vers
# /reservation-confirmee/ après une réservation. Les supprimer, c'est leur
# afficher une erreur 404 au pire moment.
ANCIENNES_ADRESSES = (
    "a-propos", "la-chiropratique", "tarifs-et-remboursements",
    "contact-et-acces", "mentions-legales",
    "reservation-confirmee", "reservation-confirmee-copie",
)
for slug in ANCIENNES_ADRESSES:
    if not os.path.exists(os.path.join(DIST, slug, "index.html")):
        errors.append(f"adresse de l'ancien site disparue : /{slug}/")

# --- indépendance : aucune requête vers un serveur tiers au chargement ---
TIERS_TOLERES = ("practicehub.io", "google.com/maps", "formspree.io")
SITE_HOTE = "nuneschiropratique.fr"
# on ne regarde que ce qui déclenche vraiment un téléchargement
REL_CHARGEANTS = ("stylesheet", "preload", "preconnect", "dns-prefetch",
                  "icon", "apple-touch-icon", "manifest", "prefetch")

def _tiers(url):
    return SITE_HOTE not in url and not any(d in url for d in TIERS_TOLERES)

for p in pages:
    t = open(p, encoding="utf-8").read()
    name = rel(p)
    for m in re.finditer(r'<script\b[^>]*?src="(https?://[^"]+)"', t):
        if _tiers(m.group(1)):
            errors.append(f"{name}: script tiers -> {m.group(1)}")
    for m in re.finditer(r'<img\b[^>]*?src="(https?://[^"]+)"', t):
        if _tiers(m.group(1)):
            errors.append(f"{name}: image tierce -> {m.group(1)}")
    for m in re.finditer(r'<link\b([^>]*)>', t):
        attrs = m.group(1)
        r = re.search(r'rel="([^"]+)"', attrs)
        h = re.search(r'href="(https?://[^"]+)"', attrs)
        if r and h and r.group(1) in REL_CHARGEANTS and _tiers(h.group(1)):
            errors.append(f"{name}: ressource tierce ({r.group(1)}) -> {h.group(1)}")
    for m in re.finditer(r'<iframe\b[^>]*src="(https?://[^"]+)"', t):
        url = m.group(1)
        if not any(d in url for d in TIERS_TOLERES):
            errors.append(f"{name}: iframe tierce -> {url}")

# --- politique de sécurité : présente, et empreintes à jour ---
for p in pages:
    t = open(p, encoding="utf-8").read()
    name = rel(p)
    meta = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', t)
    if not meta:
        errors.append(f"{name}: politique de sécurité (CSP) absente")
        continue
    politique = html.unescape(meta.group(1))

    for directive in ("default-src 'none'", "script-src", "style-src 'self'",
                      "base-uri 'self'", "form-action"):
        if directive not in politique:
            errors.append(f"{name}: CSP sans « {directive} »")

    if "'unsafe-inline'" in politique or "'unsafe-eval'" in politique:
        errors.append(f"{name}: CSP affaibli par unsafe-inline / unsafe-eval")

    # chaque script en ligne doit être couvert par une empreinte de la politique
    for corps in re.findall(r"<script>(.*?)</script>", t, re.S):
        h = base64.b64encode(hashlib.sha256(corps.encode("utf-8")).digest()).decode()
        if f"'sha256-{h}'" not in politique:
            errors.append(f"{name}: script en ligne non couvert par le CSP "
                          f"(empreinte attendue sha256-{h})")

# --- pages de publicité : cachées, et seules à parler à Meta ---
# Le tunnel ne doit être relié par aucune page du site, ni indexé par Google.
# Les domaines de Meta ne doivent être ouverts que sur les pages à pixel.
for p in pages:
    t = open(p, encoding="utf-8").read()
    name = rel(p)
    a_pixel = 'data-pixel="' in t
    csp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', t)
    if csp and "facebook" in csp.group(1) and not a_pixel:
        errors.append(f"{name}: CSP ouvert à Meta sur une page sans pixel")
    if a_pixel and 'content="noindex"' not in t:
        errors.append(f"{name}: page à pixel Meta sans noindex")
    if not a_pixel and re.search(r'href="/bilan/?"', t):
        errors.append(f"{name}: lien vers le tunnel /bilan/ (il doit rester caché)")
    if a_pixel and name.startswith("reservation-confirmee"):
        errors.append(f"{name}: pixel sur la page de confirmation (elle reçoit des données patient)")
if not os.path.exists(os.path.join(DIST, "bilan", "index.html")):
    errors.append("tunnel /bilan/ absent")
if "/bilan/" in open(os.path.join(DIST, "sitemap.xml"), encoding="utf-8").read():
    errors.append("le tunnel /bilan/ figure dans le sitemap")

# --- srcset : chaque largeur annoncée doit correspondre au fichier réel ---
def _jpeg_w(chemin):
    try:
        with open(chemin, "rb") as f:
            if f.read(2) != b"\xff\xd8": return None
            while True:
                o = f.read(1)
                if not o: return None
                if o != b"\xff": continue
                while o == b"\xff": o = f.read(1)
                mk = o[0]
                if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7: continue
                ln = int.from_bytes(f.read(2), "big")
                if 0xC0 <= mk <= 0xCF and mk not in (0xC4, 0xC8, 0xCC):
                    f.read(1); f.read(2)
                    return int.from_bytes(f.read(2), "big")
                f.seek(ln - 2, 1)
    except OSError:
        return None

for p in pages:
    t = open(p, encoding="utf-8").read()
    name = rel(p)
    for srcset in re.findall(r'srcset="([^"]+)"', t):
        for entree in srcset.split(","):
            bits = entree.strip().split()
            if len(bits) != 2 or not bits[1].endswith("w"): continue
            chemin = os.path.join(DIST, bits[0].lstrip("/"))
            reelle = _jpeg_w(chemin)
            annoncee = int(bits[1][:-1])
            if reelle is None:
                errors.append(f"{name}: srcset pointe vers un fichier absent -> {bits[0]}")
            elif reelle != annoncee:
                errors.append(f"{name}: srcset annonce {annoncee}w mais le fichier "
                              f"fait {reelle}px -> {bits[0]}")

print(f"{len(pages)} pages analysées\n")
if warnings:
    print("AVERTISSEMENTS")
    for w in sorted(set(warnings)): print("  ~", w)
    print()
if errors:
    print("ERREURS")
    for e in sorted(set(errors)): print("  ✗", e)
    sys.exit(1)
print("✓ aucun problème bloquant")
