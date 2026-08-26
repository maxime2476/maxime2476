# -*- coding: utf-8 -*-
"""Genere les SVG du README, en variante claire et sombre.

Usage : python tools/render_assets.py

Deux regles tenues partout :

1. L'etat de base d'un element est son etat FINAL. Les animations sont des
   animations CSS qui partent d'un etat transitoire ; un rendu qui les ignore
   affiche donc la figure terminee, jamais une page vide.
2. Toute animation est desactivee sous `prefers-reduced-motion: reduce`.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import ICONS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
IRF_CSV = ROOT / "data" / "headline_irf.csv"

PALETTES = {
    "light": dict(bg="#FDFCFB", border="#E5E1DA", ink="#17181A", muted="#6B655E",
                  accent="#C2410C", grid="#E9E4DC", chip="#FFFFFF",
                  band="0.13", band2="0.18", ghost="#B9B2A9"),
    "dark": dict(bg="#0E1116", border="#222A33", ink="#E9EDF2", muted="#8B949E",
                 accent="#F97316", grid="#1B222B", chip="#141A21",
                 band="0.13", band2="0.14", ghost="#4C5561"),
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

STYLE = """<style>
  .rise{animation:rise .55s cubic-bezier(.22,.61,.36,1) both}
  .wipe{animation:wipe 1.3s cubic-bezier(.22,.61,.36,1) both}
  .halo{animation:halo 2.6s ease-out .9s infinite}
  .travel{animation:travel 5s linear infinite}
  @keyframes rise{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
  @keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
  @keyframes halo{0%{r:3.6;opacity:.55}70%{r:13;opacity:0}100%{r:13;opacity:0}}
  @keyframes travel{from{opacity:.85;transform:translateX(0)}to{opacity:.85;transform:translateX(812px)}}
  @media (prefers-reduced-motion: reduce){
    .rise,.wipe,.halo,.travel{animation:none}
  }
</style>"""


def delay(seconds):
    return f' style="animation-delay:{round(seconds, 2)}s"'


def marker(cx, cy, color):
    """Point plein, entoure d'un halo qui bat en boucle."""
    return (f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{color}"/>'
            f'<circle class="halo" cx="{cx}" cy="{cy}" r="3.6" fill="none" '
            f'stroke="{color}" stroke-width="1.4" opacity="0"/>')


# --------------------------------------------------------------------------- #
# 1. Banniere
# --------------------------------------------------------------------------- #
CURVE = ("M560,62 H596 V74 H620 V83 H652 V95 H682 V104 H714 V118 H752 V127 "
         "H790 V139 H824 V148 H856")
BAND = ("M560,53 H596 V65 H620 V74 H652 V86 H682 V95 H714 V109 H752 V118 H790 V130 "
        "H824 V139 H856 L856,157 H824 V148 H790 V139 H752 V127 H714 V118 H682 V104 "
        "H652 V95 H620 V83 H596 V71 H560 Z")
TICKS = [(636, 83), (698, 104), (770, 127), (840, 148)]


def header(p):
    ticks = "".join(
        f'<line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}" stroke="{p["accent"]}" '
        f'stroke-width="1.4" stroke-linecap="round"/>' for x, y in TICKS)
    lines = [
        (f'<text x="44" y="70" font-family="{MONO}" font-size="11.5" letter-spacing="2.4" '
         f'fill="{p["accent"]}">DATA SCIENTIST / ING&#201;NIEUR IA</text>', 0.05),
        (f'<text x="44" y="119" font-size="38" font-weight="700" fill="{p["ink"]}">'
         f'Maxime Gourguechon</text>', 0.14),
        (f'<text x="44" y="149" font-size="15" fill="{p["muted"]}">Vision par ordinateur, '
         f'NLP, inf&#233;rence causale.</text>', 0.24),
        (f'<text x="44" y="180" font-size="13.5" fill="{p["muted"]}">M2 &#201;conom&#233;trie '
         f'&amp; Statistiques (Lille) &#183; stage data science chez Aubay</text>', 0.32),
        (f'<circle cx="48" cy="205" r="3.5" fill="{p["accent"]}"/>'
         f'<text x="60" y="209" font-size="13.5" fill="{p["muted"]}">CDI &#224; partir de '
         f'septembre 2026, Paris ou remote</text>', 0.4),
    ]
    txt = "".join(f'<g class="rise"{delay(d)}>{el}</g>' for el, d in lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="250" viewBox="0 0 900 250" role="img" aria-label="Maxime Gourguechon, data scientist, vision par ordinateur, NLP, inference causale">
  {STYLE}
  <rect x="0.5" y="0.5" width="899" height="249" rx="14" fill="{p['bg']}" stroke="{p['border']}"/>
  <g font-family="{SANS}">{txt}</g>
  <g>
    <line x1="560" y1="52" x2="560" y2="186" stroke="{p['grid']}" stroke-width="1.2"/>
    <line x1="560" y1="186" x2="860" y2="186" stroke="{p['grid']}" stroke-width="1.2"/>
    <g class="wipe" style="animation-delay:.25s">
      <path d="{BAND}" fill="{p['accent']}" fill-opacity="{p['band']}"/>
      <line x1="560" y1="124" x2="752" y2="124" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.75"/>
      <line x1="752" y1="124" x2="752" y2="186" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.75"/>
      <path d="{CURVE}" fill="none" stroke="{p['accent']}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
      {ticks}
    </g>
    {marker(856, 148, p['accent'])}
    <g font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">
      <text x="551" y="66">1.0</text>
      <text x="551" y="128">0.5</text>
      <text x="551" y="190">0</text>
    </g>
    <text x="744" y="181" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">m&#233;diane</text>
    <text x="860" y="204" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">temps depuis le 1er commit</text>
    <text x="560" y="228" font-family="{MONO}" font-size="10.5" fill="{p['muted']}">part des contributeurs encore actifs, au fil du temps</text>
  </g>
</svg>
'''


# --------------------------------------------------------------------------- #
# 2. Schema du pipeline
# --------------------------------------------------------------------------- #
NODES = [
    (44, 186, "8 000 images", "r&#233;cifs coralliens", False),
    (270, 160, "YOLO", "d&#233;tection", False),
    (470, 160, "SAM 3", "masques", False),
    (670, 186, "92 %", "de pr&#233;cision", True),
]


def pipeline(p):
    boxes = []
    for k, (x, w, title, sub, hi) in enumerate(NODES):
        stroke = p["accent"] if hi else p["border"]
        ink = p["accent"] if hi else p["ink"]
        boxes.append(
            f'<g class="rise"{delay(0.12 + 0.16 * k)}>'
            f'<rect x="{x}" y="78" width="{w}" height="60" rx="10" fill="{p["chip"]}" '
            f'stroke="{stroke}" stroke-width="{1.6 if hi else 1}"/>'
            f'<text x="{x + w / 2}" y="{108 if hi else 106}" font-family="{SANS}" '
            f'font-size="{22 if hi else 15}" font-weight="600" fill="{ink}" '
            f'text-anchor="middle">{title}</text>'
            f'<text x="{x + w / 2}" y="124" font-family="{MONO}" font-size="10" '
            f'fill="{p["muted"]}" text-anchor="middle">{sub}</text></g>')
    arrows = "".join(
        f'<line x1="{x}" y1="108" x2="{x + 30}" y2="108" stroke="{p["muted"]}" '
        f'stroke-width="1.4"/>'
        f'<path d="M{x + 30},108 L{x + 24},104.5 L{x + 24},111.5 Z" fill="{p["muted"]}"/>'
        for x in (230, 430, 630))
    brackets = "".join(
        f'<path d="M{a},150 V157 H{b} V150" fill="none" stroke="{p["grid"]}" '
        f'stroke-width="1.4"/>' for a, b in ((44, 230), (270, 630)))
    notes = "".join(
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="10" fill="{p["muted"]}" '
        f'text-anchor="middle">{t}</text>'
        for x, y, t in (
            (137, 174, "pr&#233;paration des donn&#233;es"),
            (137, 188, "automatis&#233;e : 6 h de moins par cycle"),
            (450, 174, "d&#233;fauts ajout&#233;s pendant l&#8217;entra&#238;nement :"),
            (450, 188, "flou et dominante bleu-vert de l&#8217;eau")))
    # point qui circule le long de la chaine, masque par les boites
    # opacite de base nulle : sans animation, pas de point orphelin sur la 1re boite
    packet = (f'<circle class="travel" cx="44" cy="108" r="3.2" fill="{p["accent"]}" '
              f'opacity="0"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="212" viewBox="0 0 900 212" role="img" aria-label="Pipeline de segmentation : 8000 images de recifs, YOLO, SAM 3, 92 pour cent de precision">
  {STYLE}
  <rect x="0.5" y="0.5" width="899" height="211" rx="14" fill="{p['bg']}" stroke="{p['border']}"/>
  <text x="44" y="46" font-family="{MONO}" font-size="11" letter-spacing="1.8" fill="{p['accent']}">STAGE AUBAY &#183; SEGMENTATION DE R&#201;CIFS CORALLIENS</text>
  {packet}{arrows}{"".join(boxes)}{brackets}{notes}
</svg>
'''


# --------------------------------------------------------------------------- #
# 3. Effet estime (donnees reelles de causal-impact-lab)
# --------------------------------------------------------------------------- #
def load_irf():
    rows = []
    with open(IRF_CSV, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((int(float(r["horizon"])), float(r["beta"]),
                         float(r["ci_low"]), float(r["ci_high"])))
    return sorted(rows)


def irf(p):
    rows = load_irf()
    x0, x1, ytop, ybot = 92, 858, 76, 252
    vmin, vmax = -0.19, 0.125

    def X(h):
        return round(x0 + (h + 6) / 30 * (x1 - x0), 1)

    def Y(v):
        return round(ybot - (v - vmin) / (vmax - vmin) * (ybot - ytop), 1)

    pre = [r for r in rows if r[0] < 0]
    post = [r for r in rows if r[0] >= 0]

    def band(seg):
        up = " L ".join(f"{X(h)},{Y(hi)}" for h, _, _, hi in seg)
        lo = " L ".join(f"{X(h)},{Y(low)}" for h, _, low, _ in reversed(seg))
        return f"M {up} L {lo} Z"

    def line(seg):
        return "M " + " L ".join(f"{X(h)},{Y(b)}" for h, b, _, _ in seg)

    grid = "".join(
        f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{p["grid"]}" '
        f'stroke-width="1"/>'
        f'<text x="{x0 - 10}" y="{Y(v) + 3.5}" font-family="{MONO}" font-size="10" '
        f'fill="{p["muted"]}" text-anchor="end">{v:+.2f}</text>'
        for v in (0.10, 0.05, -0.05, -0.10, -0.15))
    xticks = "".join(
        f'<text x="{X(h)}" y="{ybot + 20}" font-family="{MONO}" font-size="10" '
        f'fill="{p["muted"]}" text-anchor="middle">{h:+d}</text>'
        for h in (-6, 0, 6, 12, 18, 24))

    def fr(v):
        return f"{v:.3f}".replace(".", ",")

    b12 = next(r for r in rows if r[0] == 12)
    ax, ay = X(12), Y(b12[1])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340" viewBox="0 0 900 340" role="img" aria-label="Effet estime d'une hausse des taux sur l'emploi, avec une marge d'erreur qui contient zero">
  {STYLE}
  <rect x="0.5" y="0.5" width="899" height="339" rx="14" fill="{p['bg']}" stroke="{p['border']}"/>
  <text x="44" y="34" font-family="{SANS}" font-size="15" font-weight="600" fill="{p['ink']}">Effet d&#8217;une hausse des taux d&#8217;int&#233;r&#234;t sur l&#8217;emploi</text>
  <text x="44" y="52" font-family="{SANS}" font-size="12" fill="{p['muted']}">Emploi am&#233;ricain, 1994-2020. L&#8217;effet va dans le sens attendu, mais la marge d&#8217;erreur contient toujours z&#233;ro.</text>
  {grid}
  <line x1="{x0}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{p['muted']}" stroke-width="1.2" opacity="0.55"/>
  <text x="{x0 - 10}" y="{Y(0) + 3.5}" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">0</text>
  <line x1="{X(0)}" y1="{ytop - 6}" x2="{X(0)}" y2="{ybot + 4}" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>
  <text x="{X(0) + 6}" y="{ytop + 2}" font-family="{MONO}" font-size="10" fill="{p['muted']}">hausse des taux</text>
  <g class="wipe" style="animation-delay:.2s">
    <path d="{band(pre)}" fill="{p['ghost']}" fill-opacity="0.20"/>
    <path d="{line(pre)}" fill="none" stroke="{p['ghost']}" stroke-width="1.8" stroke-dasharray="4 3"/>
    <path d="{band(post)}" fill="{p['accent']}" fill-opacity="{p['band2']}"/>
    <path d="{line(post)}" fill="none" stroke="{p['accent']}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
  </g>
  <g class="rise" style="animation-delay:1.35s">
    {marker(ax, ay, p['accent'])}
    <line x1="{ax}" y1="{ay - 8}" x2="{ax}" y2="{ay - 38}" stroke="{p['muted']}" stroke-width="1"/>
    <text x="{ax - 6}" y="{ay - 44}" font-family="{MONO}" font-size="10.5" fill="{p['ink']}" text-anchor="middle">12 mois : {fr(b12[1])}</text>
    <text x="{ax - 6}" y="{ay - 31}" font-family="{MONO}" font-size="9.5" fill="{p['muted']}" text-anchor="middle">marge d&#8217;erreur : {fr(b12[2])} &#224; {fr(b12[3])}</text>
  </g>
  {xticks}
  <text x="{(x0 + x1) // 2}" y="{ybot + 38}" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="middle">mois apr&#232;s la hausse des taux</text>
  <g font-family="{MONO}" font-size="10" fill="{p['muted']}">
    <line x1="44" y1="{ybot + 62}" x2="70" y2="{ybot + 62}" stroke="{p['accent']}" stroke-width="2.4"/>
    <text x="76" y="{ybot + 65.5}">effet estim&#233;</text>
    <rect x="216" y="{ybot + 57}" width="26" height="10" fill="{p['accent']}" fill-opacity="{p['band2']}"/>
    <text x="248" y="{ybot + 65.5}">marge d&#8217;erreur (95 %)</text>
    <line x1="470" y1="{ybot + 62}" x2="496" y2="{ybot + 62}" stroke="{p['ghost']}" stroke-width="1.8" stroke-dasharray="4 3"/>
    <text x="502" y="{ybot + 65.5}">avant la hausse</text>
    <text x="{x1}" y="{ybot + 65.5}" text-anchor="end">source : causal-impact-lab</text>
  </g>
</svg>
'''


# --------------------------------------------------------------------------- #
# 4. Carte des methodes
# --------------------------------------------------------------------------- #
COLUMNS = [
    ("LIVR&#201; ET EN SERVICE",
     "d&#233;ploy&#233; publiquement, ou tourn&#233; dans le",
     "pipeline du stage",
     [("Python", "python"), ("PyTorch", "pytorch"),
      ("scikit-learn", "scikitlearn"),
      ("YOLO + SAM 3", "ultralytics"), ("OpenCV + MediaPipe", "opencv"),
      ("XGBoost", None), ("SHAP", None), ("lifelines", None),
      ("statsmodels", None), ("DuckDB", "duckdb"), ("Streamlit", "streamlit"),
      ("Docker", "docker"), ("GitHub Actions", "githubactions"),
      ("pytest", "pytest")]),
    ("UTILIS&#201; EN PROJET",
     "travail s&#233;rieux, m&#233;moire ou projet public,",
     "jamais mis en service",
     [("R", "r"), ("SQL", None), ("MLflow", "mlflow"),
      ("double machine learning", None), ("LP bay&#233;sienne", None),
      ("bootstrap, DEA, Simar-Wilson", None)]),
    ("LU, PAS ENCORE LIVR&#201;",
     "je sais de quoi il s&#8217;agit et ce que &#231;a co&#251;te,",
     "je ne l&#8217;ai pas encore fait tourner",
     [("d&#233;ploiement AWS", "amazonwebservices"),
      ("monitoring en production", None), ("agents LLM en production", None)]),
]

ICON_PX = 13.5


def glyph(name, x, y, color):
    """Logo de l'outil, ou petite courbe quand la ligne designe une methode."""
    if name:
        k = ICON_PX / 24
        return (f'<g transform="translate({x},{y}) scale({k:.4f})" fill="{color}" '
                f'opacity="0.9"><path d="{ICONS[name]}"/></g>')
    return (f'<path d="M{x},{y + 10.5} C{x + 3},{y + 10.5} {x + 4},{y + 3} '
            f'{x + 7},{y + 3} C{x + 9.5},{y + 3} {x + 10.5},{y + 7} '
            f'{x + 13.5},{y + 7}" fill="none" stroke="{color}" stroke-width="1.5" '
            f'stroke-linecap="round" opacity="0.5"/>')


def methods(p):
    xs = (44, 326, 608)
    top = 46
    body, i = [], 0
    rows_max = max(len(c[3]) for c in COLUMNS)
    for ci, (title, crit1, crit2, items) in enumerate(COLUMNS):
        x = xs[ci]
        col = p["accent"] if ci == 0 else (p["ink"] if ci == 1 else p["muted"])
        body.append(
            f'<text x="{x}" y="{top}" font-family="{MONO}" font-size="10.5" '
            f'letter-spacing="1.5" fill="{col}">{title}</text>'
            f'<text x="{x}" y="{top + 18}" font-family="{SANS}" font-size="10.5" '
            f'fill="{p["muted"]}">{crit1}</text>'
            f'<text x="{x}" y="{top + 31}" font-family="{SANS}" font-size="10.5" '
            f'fill="{p["muted"]}">{crit2}</text>'
            f'<line x1="{x}" y1="{top + 46}" x2="{x + 248}" y2="{top + 46}" '
            f'stroke="{p["border"]}" stroke-width="1"/>')
        y = top + 64
        for label, icon in items:
            plain = re.sub(r"&#?\w+;", "x", label)
            w = round(6.65 * len(plain)) + 46
            fill = p["chip"] if ci < 2 else p["bg"]
            dash = ' stroke-dasharray="4 3"' if ci == 2 else ""
            ink = p["ink"] if ci < 2 else p["muted"]
            body.append(
                f'<g class="rise"{delay(0.15 + i * 0.035)}>'
                f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="7" fill="{fill}" '
                f'stroke="{p["border"]}"{dash}/>'
                f'{glyph(icon, x + 11, y + 6, ink)}'
                f'<text x="{x + 32}" y="{y + 17.5}" font-family="{MONO}" font-size="11" '
                f'fill="{ink}">{label}</text></g>')
            y += 30
            i += 1
    h = top + 64 + rows_max * 30 + 44
    body.append(
        f'<text x="44" y="{h - 18}" font-family="{MONO}" font-size="9.5" '
        f'fill="{p["muted"]}">classement fait sur pi&#232;ces : d&#233;p&#244;ts publics, '
        f'applications en ligne, pipeline du stage</text>'
        f'<text x="856" y="{h - 18}" font-family="{MONO}" font-size="9" '
        f'fill="{p["muted"]}" text-anchor="end" opacity="0.75">logos : Simple Icons '
        f'(CC0)</text>')
    seps = "".join(
        f'<line x1="{x}" y1="{top - 16}" x2="{x}" y2="{h - 20}" stroke="{p["border"]}" '
        f'stroke-width="1" opacity="0.6"/>' for x in (302, 584))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" '
            f'viewBox="0 0 900 {h}" role="img" aria-label="Carte des methodes : livre et en '
            f'service, utilise en projet, lu pas encore livre">{STYLE}'
            f'<rect x="0.5" y="0.5" width="899" height="{h - 1}" rx="14" fill="{p["bg"]}" '
            f'stroke="{p["border"]}"/>{seps}{"".join(body)}</svg>\n')


for mode, pal in PALETTES.items():
    (OUT / f"header-{mode}.svg").write_text(header(pal), encoding="utf-8")
    (OUT / f"pipeline-{mode}.svg").write_text(pipeline(pal), encoding="utf-8")
    (OUT / f"irf-{mode}.svg").write_text(irf(pal), encoding="utf-8")
    (OUT / f"methods-{mode}.svg").write_text(methods(pal), encoding="utf-8")

print("ok", len(sorted(OUT.iterdir())), "fichiers dans assets/")
