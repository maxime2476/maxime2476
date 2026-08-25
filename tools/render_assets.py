# -*- coding: utf-8 -*-
"""Genere les SVG animes du README (variantes claire et sombre).

Usage : python tools/render_assets.py

Regle: chaque element a comme attribut de base son etat FINAL, les animations
partent d'un `from`. Un rendu qui ignore SMIL affiche donc la figure terminee.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
IRF_CSV = ROOT / "data" / "headline_irf.csv"

PALETTES = {
    "light": dict(bg="#FDFCFB", border="#E5E1DA", ink="#17181A", muted="#6B655E",
                  accent="#C2410C", grid="#E9E4DC", chip="#FFFFFF", band="0.13", band2="0.18",
                  ghost="#B9B2A9"),
    "dark":  dict(bg="#0E1116", border="#222A33", ink="#E9EDF2", muted="#8B949E",
                  accent="#F97316", grid="#1B222B", chip="#141A21", band="0.13", band2="0.14",
                  ghost="#4C5561"),
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"


def fade(begin, dur=0.5, frm="0"):
    return (f'<animate attributeName="opacity" from="{frm}" to="1" '
            f'begin="{begin}s" dur="{dur}s" fill="freeze"/>')


def rise(begin, dy=10, dur=0.6):
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 {dy}" to="0 0" begin="{begin}s" dur="{dur}s" fill="freeze"/>')


def pulse(cx, cy, color):
    """Halo qui bat en boucle autour du dernier point."""
    return (f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{color}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="none" stroke="{color}" '
            f'stroke-width="1.4" opacity="0">'
            f'<animate attributeName="r" from="3.6" to="12" dur="2.4s" '
            f'begin="1.6s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.55;0" dur="2.4s" '
            f'begin="1.6s" repeatCount="indefinite"/></circle>')


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
        f'<line x1="{x}" y1="{y-5}" x2="{x}" y2="{y+5}" stroke="{p["accent"]}" '
        f'stroke-width="1.4" stroke-linecap="round"/>' for x, y in TICKS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="250" viewBox="0 0 900 250" role="img" aria-label="Maxime Gourguechon, data scientist, vision par ordinateur, NLP, inference causale">
  <defs>
    <clipPath id="wipetxt">
      <rect x="36" y="46" width="520" height="180">
        <animate attributeName="width" from="0" to="520" begin="0.1s" dur="1.1s" fill="freeze"/>
      </rect>
    </clipPath>
    <clipPath id="wipe">
      <rect x="556" y="40" width="308" height="200">
        <animate attributeName="width" from="0" to="308" begin="0.35s" dur="1.5s" fill="freeze" calcMode="spline" keySplines="0.22 0.61 0.36 1" keyTimes="0;1" values="0;308"/>
      </rect>
    </clipPath>
  </defs>
  <rect x="0.5" y="0.5" width="899" height="249" rx="14" fill="{p['bg']}" stroke="{p['border']}"/>
  <g font-family="{SANS}" clip-path="url(#wipetxt)">
    <text x="44" y="70" font-family="{MONO}" font-size="11.5" letter-spacing="2.4" fill="{p['accent']}">DATA SCIENTIST / ING&#201;NIEUR IA</text>
    <text x="44" y="119" font-size="38" font-weight="700" fill="{p['ink']}">Maxime Gourguechon</text>
    <text x="44" y="149" font-size="15" fill="{p['muted']}">Vision par ordinateur, NLP, inf&#233;rence causale.</text>
    <text x="44" y="180" font-size="13.5" fill="{p['muted']}">M2 &#201;conom&#233;trie &amp; Statistiques (Lille) &#183; stage data science chez Aubay</text>
    <circle cx="48" cy="205" r="3.5" fill="{p['accent']}"/><text x="60" y="209" font-size="13.5" fill="{p['muted']}">CDI &#224; partir de septembre 2026, Paris ou remote</text>
  </g>
  <g>
    <line x1="560" y1="52" x2="560" y2="186" stroke="{p['grid']}" stroke-width="1.2"/>
    <line x1="560" y1="186" x2="860" y2="186" stroke="{p['grid']}" stroke-width="1.2"/>
    <g clip-path="url(#wipe)">
      <path d="{BAND}" fill="{p['accent']}" fill-opacity="{p['band']}"/>
      <line x1="560" y1="124" x2="752" y2="124" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.75"/>
      <line x1="752" y1="124" x2="752" y2="186" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.75"/>
      <path d="{CURVE}" fill="none" stroke="{p['accent']}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
      {ticks}
    </g>
    {pulse(856, 148, p['accent'])}
    <g font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">
      <text x="551" y="66">1.0</text>
      <text x="551" y="128">0.5</text>
      <text x="551" y="190">0</text>
    </g>
    <text x="744" y="181" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">m&#233;diane</text>
    <text x="860" y="204" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">temps depuis le 1er commit</text>
    <text x="560" y="228" font-family="{MONO}" font-size="10.5" fill="{p['muted']}">S(t) &#183; survie des contributeurs (Kaplan-Meier)</text>
  </g>
</svg>
'''


# --------------------------------------------------------------------------- #
# 2. Outils
# --------------------------------------------------------------------------- #
GROUPS = [
    ("MOD&#200;LES", ["PyTorch", "scikit-learn", "XGBoost", "LightGBM", "YOLO", "SAM",
                      "MediaPipe", "lifelines", "statsmodels", "SHAP"]),
    ("DONN&#201;ES", ["Python", "SQL", "R", "pandas", "NumPy", "DuckDB", "Plotly",
                      "Bash", "SAS"]),
    ("MISE EN PROD", ["Docker", "GitHub Actions", "MLflow", "pytest", "ruff",
                      "mypy", "uv", "Streamlit", "Hugging Face Spaces", "Power BI"]),
]


def stack(p):
    x0, right, chip_h, gap = 176, 862, 27, 8
    y, i = 40, 0
    body = []
    for gi, (label, items) in enumerate(GROUPS):
        body.append(f'<text x="44" y="{y + 18}" font-family="{MONO}" font-size="11" '
                    f'letter-spacing="1.6" fill="{p["accent"]}">{label}</text>')
        x = x0
        for it in items:
            w = round(6.65 * len(it)) + 24
            if x + w > right:
                x, y = x0, y + chip_h + gap
            b = round(0.25 + i * 0.045, 2)
            body.append(
                f'<g transform="translate(0 0)">{rise(b, 7, 0.45)}'
                f'<rect x="{x}" y="{y}" width="{w}" height="{chip_h}" rx="7" '
                f'fill="{p["chip"]}" stroke="{p["border"]}"/>'
                f'<text x="{x + 12}" y="{y + 18}" font-family="{MONO}" font-size="11.5" '
                f'fill="{p["ink"]}">{it}</text></g>')
            x += w + gap
            i += 1
        y += chip_h + 26
    h = y + 8
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" '
            f'viewBox="0 0 900 {h}" role="img" aria-label="Outils utilis&#233;s">'
            f'<rect x="0.5" y="0.5" width="899" height="{h-1}" rx="14" '
            f'fill="{p["bg"]}" stroke="{p["border"]}"/>' + "".join(body) + "</svg>\n")


# --------------------------------------------------------------------------- #
# 3. Fonction de reponse (donnees reelles de causal-impact-lab)
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
        up = " ".join(f"{X(h)},{Y(hi)}" for h, _, _, hi in seg)
        lo = " ".join(f"{X(h)},{Y(lo_)}" for h, _, lo_, _ in reversed(seg))
        return f"M{up} L{lo} Z".replace("M", "M ").replace("L", "L ")

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
        f'fill="{p["muted"]}" text-anchor="middle">{h:+d}</text>' for h in (-6, 0, 6, 12, 18, 24))

    b12 = next(r for r in rows if r[0] == 12)
    ax, ay = X(12), Y(b12[1])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340" viewBox="0 0 900 340" role="img" aria-label="Fonction de reponse estimee de l'emploi relatif a un choc monetaire restrictif">
  <defs>
    <clipPath id="irfwipe">
      <rect x="{x0 - 2}" y="{ytop - 12}" width="{x1 - x0 + 6}" height="{ybot - ytop + 24}">
        <animate attributeName="width" from="0" to="{x1 - x0 + 6}" begin="0.3s" dur="1.7s" fill="freeze"/>
      </rect>
    </clipPath>
  </defs>
  <rect x="0.5" y="0.5" width="899" height="339" rx="14" fill="{p['bg']}" stroke="{p['border']}"/>
  <text x="44" y="34" font-family="{SANS}" font-size="15" font-weight="600" fill="{p['ink']}">R&#233;ponse relative de l'emploi &#224; un choc mon&#233;taire restrictif</text>
  <text x="44" y="52" font-family="{SANS}" font-size="12" fill="{p['muted']}">Panel QCEW 1994-2020, NAICS 3 chiffres &#183; les 25 horizons post-choc sont n&#233;gatifs, aucun n'est significatif apr&#232;s correction BH</text>
  {grid}
  <line x1="{x0}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{p['muted']}" stroke-width="1.2" opacity="0.55"/>
  <text x="{x0 - 10}" y="{Y(0) + 3.5}" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="end">0</text>
  <line x1="{X(0)}" y1="{ytop - 6}" x2="{X(0)}" y2="{ybot + 4}" stroke="{p['muted']}" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>
  <text x="{X(0) + 6}" y="{ytop + 2}" font-family="{MONO}" font-size="10" fill="{p['muted']}">choc</text>
  <g clip-path="url(#irfwipe)">
    <path d="{band(pre)}" fill="{p['ghost']}" fill-opacity="0.20"/>
    <path d="{line(pre)}" fill="none" stroke="{p['ghost']}" stroke-width="1.8" stroke-dasharray="4 3"/>
    <path d="{band(post)}" fill="{p['accent']}" fill-opacity="{p['band2']}"/>
    <path d="{line(post)}" fill="none" stroke="{p['accent']}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
  </g>
  <g>
    {pulse(ax, ay, p['accent'])}
    <line x1="{ax}" y1="{ay - 8}" x2="{ax}" y2="{ay - 26}" stroke="{p['muted']}" stroke-width="1"/>
    <text x="{ax - 6}" y="{ay - 32}" font-family="{MONO}" font-size="10.5" fill="{p['ink']}" text-anchor="middle">h = 12 &#183; &#946; = {b12[1]:.3f}</text>
    <text x="{ax - 6}" y="{ay - 19}" font-family="{MONO}" font-size="9.5" fill="{p['muted']}" text-anchor="middle">IC 95 % [{b12[2]:.3f} ; {b12[3]:.3f}]</text>
  </g>
  {xticks}
  <text x="{(x0 + x1) // 2}" y="{ybot + 38}" font-family="{MONO}" font-size="10" fill="{p['muted']}" text-anchor="middle">horizon h, en mois apr&#232;s le choc</text>
  <g font-family="{MONO}" font-size="10" fill="{p['muted']}">
    <line x1="44" y1="{ybot + 62}" x2="70" y2="{ybot + 62}" stroke="{p['accent']}" stroke-width="2.4"/>
    <text x="76" y="{ybot + 65.5}">estimation ponctuelle</text>
    <rect x="216" y="{ybot + 57}" width="26" height="10" fill="{p['accent']}" fill-opacity="{p['band2']}"/>
    <text x="248" y="{ybot + 65.5}">IC 95 %</text>
    <line x1="330" y1="{ybot + 62}" x2="356" y2="{ybot + 62}" stroke="{p['ghost']}" stroke-width="1.8" stroke-dasharray="4 3"/>
    <text x="362" y="{ybot + 65.5}">leads (test de pr&#233;-tendance)</text>
    <text x="{x1}" y="{ybot + 65.5}" text-anchor="end">source : causal-impact-lab, app/assets/headline_irf.csv</text>
  </g>
</svg>
'''


# --------------------------------------------------------------------------- #
# 4. Pipeline du stage (schema)
# --------------------------------------------------------------------------- #
NODES = [
    (44, 186, "8 000 images", "r&#233;cifs coralliens", False),
    (270, 160, "YOLO", "d&#233;tection", False),
    (470, 160, "SAM 3", "masques", False),
    (670, 186, "92 %", "pr&#233;cision de segmentation", True),
]


def arrow(x, p):
    return (f'<line x1="{x}" y1="108" x2="{x + 30}" y2="108" stroke="{p["muted"]}" '
            f'stroke-width="1.4"/>'
            f'<path d="M{x + 30},108 L{x + 24},104.5 L{x + 24},111.5 Z" fill="{p["muted"]}"/>')


def bracket(x1, x2, p):
    return (f'<path d="M{x1},150 V157 H{x2} V150" fill="none" stroke="{p["grid"]}" '
            f'stroke-width="1.4"/>')


def pipeline(p):
    boxes = []
    for k, (x, w, title, sub, hi) in enumerate(NODES):
        stroke = p["accent"] if hi else p["border"]
        ink = p["accent"] if hi else p["ink"]
        size = 22 if hi else 15
        boxes.append(
            f'<g transform="translate(0 0)">{rise(round(0.15 + 0.18 * k, 2), 9, 0.5)}'
            f'<rect x="{x}" y="78" width="{w}" height="60" rx="10" fill="{p["chip"]}" '
            f'stroke="{stroke}" stroke-width="{1.6 if hi else 1}"/>'
            f'<text x="{x + w / 2}" y="{108 if hi else 106}" font-family="{SANS}" '
            f'font-size="{size}" font-weight="600" fill="{ink}" text-anchor="middle">{title}</text>'
            f'<text x="{x + w / 2}" y="124" font-family="{MONO}" font-size="10" '
            f'fill="{p["muted"]}" text-anchor="middle">{sub}</text></g>')
    arrows = "".join(arrow(x, p) for x in (230, 430, 630))
    # opacite de base a 0 : sans SMIL, pas de point orphelin dans le coin
    packet = (f'<circle r="3.2" fill="{p["accent"]}" opacity="0">'
              f'<animate attributeName="opacity" values="0.9;0.9" dur="5s" repeatCount="indefinite"/>'
              f'<animateMotion path="M44,108 H856" dur="5s" repeatCount="indefinite"/>'
              f'</circle>')
    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="212" '
            'viewBox="0 0 900 212" role="img" aria-label="Pipeline de segmentation : '
            '8000 images de recifs, YOLO, SAM 3, 92 pour cent de precision">')
    return (head
            + f'<rect x="0.5" y="0.5" width="899" height="211" rx="14" fill="{p["bg"]}" '
              f'stroke="{p["border"]}"/>'
            + f'<text x="44" y="46" font-family="{MONO}" font-size="11" letter-spacing="1.8" '
              f'fill="{p["accent"]}">STAGE AUBAY &#183; SEGMENTATION DE R&#201;CIFS CORALLIENS</text>'
            + packet + arrows + "".join(boxes)
            + bracket(44, 230, p) + bracket(270, 630, p)
            + f'<text x="137" y="174" font-family="{MONO}" font-size="10" fill="{p["muted"]}" '
              f'text-anchor="middle">pr&#233;paration et validation du dataset</text>'
            + f'<text x="137" y="188" font-family="{MONO}" font-size="10" fill="{p["muted"]}" '
              f'text-anchor="middle">automatis&#233;es : 6 h de moins par cycle</text>'
            + f'<text x="450" y="174" font-family="{MONO}" font-size="10" fill="{p["muted"]}" '
              f'text-anchor="middle">augmentations cibl&#233;es (Albumentations) :</text>'
            + f'<text x="450" y="188" font-family="{MONO}" font-size="10" fill="{p["muted"]}" '
              f'text-anchor="middle">flou et d&#233;rive colorim&#233;trique sous-marine</text>'
            + "</svg>\n")


# --------------------------------------------------------------------------- #
# 5. Carte des methodes (trois colonnes assumees)
# --------------------------------------------------------------------------- #
COLUMNS = [
    ("LIVR&#201; ET EN SERVICE",
     "d&#233;ploy&#233; publiquement, ou tourn&#233; dans le",
     "pipeline du stage",
     ["YOLO + SAM 3", "Albumentations", "XGBoost", "SHAP", "lifelines",
      "statsmodels", "projections locales", "MediaPipe + OpenCV", "DuckDB",
      "Streamlit", "Docker", "GitHub Actions", "pytest + mypy"]),
    ("UTILIS&#201; EN PROJET",
     "travail s&#233;rieux, m&#233;moire ou projet public,",
     "jamais mis en service",
     ["PyTorch", "double machine learning", "LP bay&#233;sienne", "TF-IDF + K-Means",
      "DEA &amp; Simar-Wilson", "bootstrap non gaussien", "MLflow", "R", "SAS",
      "SQL", "Power BI"]),
    ("LU, PAS ENCORE LIVR&#201;",
     "je sais de quoi il s'agit et ce que &#231;a co&#251;te,",
     "je ne l'ai pas encore fait tourner",
     ["d&#233;ploiement manag&#233; AWS", "monitoring en production",
      "agents LLM en production"]),
]


def methods(p):
    xs = (44, 326, 608)
    colw = 248
    top = 46
    body = []
    rows_max = max(len(c[3]) for c in COLUMNS)
    i = 0
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
            f'<line x1="{x}" y1="{top + 46}" x2="{x + colw}" y2="{top + 46}" '
            f'stroke="{p["border"]}" stroke-width="1"/>')
        y = top + 64
        for it in items:
            plain = it.replace("&#201;", "E").replace("&#233;", "e").replace("&amp;", "&")
            plain = plain.replace("&#232;", "e").replace("&#231;", "c").replace("&#251;", "u")
            w = round(6.65 * len(plain)) + 22
            b = round(0.2 + i * 0.04, 2)
            fill = p["chip"] if ci < 2 else p["bg"]
            dash = ' stroke-dasharray="4 3"' if ci == 2 else ""
            body.append(
                f'<g transform="translate(0 0)">{rise(b, 7, 0.45)}'
                f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="7" fill="{fill}" '
                f'stroke="{p["border"]}"{dash}/>'
                f'<text x="{x + 11}" y="{y + 17.5}" font-family="{MONO}" font-size="11" '
                f'fill="{p["ink"] if ci < 2 else p["muted"]}">{it}</text></g>')
            y += 32
            i += 1
    h = top + 64 + rows_max * 32 + 42
    body.append(
        f'<text x="44" y="{h - 18}" font-family="{MONO}" font-size="9.5" '
        f'fill="{p["muted"]}">classement fait sur pi&#232;ces : d&#233;p&#244;ts publics, '
        f'applications en ligne, pipeline du stage</text>')
    seps = "".join(
        f'<line x1="{x}" y1="{top - 16}" x2="{x}" y2="{h - 20}" stroke="{p["border"]}" '
        f'stroke-width="1" opacity="0.6"/>' for x in (302, 584))
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" '
            f'viewBox="0 0 900 {h}" role="img" aria-label="Carte des methodes : livre et en '
            f'service, utilise en projet, lu pas encore livre">')
    return (head
            + f'<rect x="0.5" y="0.5" width="899" height="{h - 1}" rx="14" fill="{p["bg"]}" '
              f'stroke="{p["border"]}"/>'
            + seps + "".join(body) + "</svg>\n")


for mode, pal in PALETTES.items():
    (OUT / f"header-{mode}.svg").write_text(header(pal), encoding="utf-8")
    (OUT / f"methods-{mode}.svg").write_text(methods(pal), encoding="utf-8")
    (OUT / f"irf-{mode}.svg").write_text(irf(pal), encoding="utf-8")
    (OUT / f"pipeline-{mode}.svg").write_text(pipeline(pal), encoding="utf-8")
print("ok", sorted(f.name for f in OUT.iterdir()))
