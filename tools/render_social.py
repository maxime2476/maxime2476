# -*- coding: utf-8 -*-
"""Genere les images de partage des depots (social preview GitHub).

Usage : python tools/render_social.py

Sortie : assets/social/<depot>.svg, a convertir en PNG 1280x640 puis a deposer
dans Settings > General > Social preview de chaque depot. GitHub n'expose aucune
API pour cet envoi, il est manuel.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social"
OUT.mkdir(parents=True, exist_ok=True)

BG, BORDER, INK, MUTED, ACCENT, GHOST = (
    "#0E1116", "#222A33", "#E9EDF2", "#8B949E", "#F97316", "#4C5561")
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

# Zone du motif : x de 700 a 1190, y de 190 a 470.
def motif_causal():
    return (f'<path d="M700,300 L770,288 L840,276 L910,300 L980,284 L1050,296 L1120,290 '
            f'L1190,286 L1190,392 L1120,404 L1050,398 L980,410 L910,392 L840,384 '
            f'L770,378 L700,372 Z" fill="{ACCENT}" fill-opacity="0.16"/>'
            f'<line x1="700" y1="336" x2="1190" y2="336" stroke="{MUTED}" '
            f'stroke-width="2" opacity="0.6"/>'
            f'<path d="M700,336 L770,332 L840,328 L910,352 L980,336 L1050,344 '
            f'L1120,332 L1190,330" fill="none" stroke="{ACCENT}" stroke-width="4" '
            f'stroke-linejoin="round"/>')


def motif_survival():
    ticks = "".join(
        f'<line x1="{x}" y1="{y - 12}" x2="{x}" y2="{y + 12}" stroke="{ACCENT}" '
        f'stroke-width="3"/>' for x, y in ((790, 250), (940, 320), (1090, 380)))
    return (f'<path d="M700,214 H760 V250 H840 V286 H920 V320 H1010 V350 H1080 V380 '
            f'H1190" fill="none" stroke="{ACCENT}" stroke-width="4" '
            f'stroke-linejoin="round"/>' + ticks)


def motif_bmw():
    pts = [(720, 260), (770, 400), (820, 300), (870, 420), (920, 250), (970, 380),
           (1020, 290), (1070, 410), (1120, 270), (1170, 370)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="{GHOST}"/>' for x, y in pts)
    return (dots + f'<line x1="700" y1="330" x2="1190" y2="330" stroke="{ACCENT}" '
                   f'stroke-width="4" stroke-dasharray="14 10"/>')


def motif_heron():
    return (f'<line x1="700" y1="380" x2="1190" y2="380" stroke="{MUTED}" '
            f'stroke-width="2" stroke-dasharray="8 10" opacity="0.7"/>'
            f'<path d="M700,262 L790,252 L880,276 L970,258 L1060,420 L1130,404 '
            f'L1190,272" fill="none" stroke="{ACCENT}" stroke-width="4" '
            f'stroke-linejoin="round"/>'
            f'<circle cx="1060" cy="420" r="9" fill="{ACCENT}"/>')


CARDS = [
    ("causal-impact-lab", "causal-impact-lab",
     ["Does raising interest rates", "actually destroy jobs?"],
     ["The expected sign everywhere, too imprecise to conclude.",
      "The null result is published as the finding."], motif_causal),
    ("git-survival", "git-survival",
     ["Quand un contributeur", "décroche-t-il ?"],
     ["L'analyse de survie de la médecine,",
      "appliquée aux historiques Git."], motif_survival),
    ("bmw-sales-analytics", "bmw-sales-analytics",
     ["50,000 car sales,", "nothing to predict."],
     ["Proving the absence of signal instead of forcing a model,",
      "then shipping a scenario simulator."], motif_bmw),
    ("heron", "heron",
     ["Une meilleure posture", "que la tienne."],
     ["Moniteur de posture par webcam.",
      "Tout reste sur votre machine."], motif_heron),
]


def card(slug, repo, title, sub, motif):
    tl = "".join(
        f'<text x="90" y="{270 + k * 66}" font-family="{SANS}" font-size="54" '
        f'font-weight="700" fill="{INK}">{t}</text>' for k, t in enumerate(title))
    sl = "".join(
        f'<text x="90" y="{430 + k * 34}" font-family="{SANS}" font-size="24" '
        f'fill="{MUTED}">{t}</text>' for k, t in enumerate(sub))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-label="{repo}">
  <rect width="1280" height="640" fill="{BG}"/>
  <rect x="40" y="40" width="1200" height="560" rx="20" fill="none" stroke="{BORDER}" stroke-width="2"/>
  <text x="90" y="150" font-family="{MONO}" font-size="22" letter-spacing="4" fill="{ACCENT}">{repo.upper()}</text>
  {tl}{sl}
  <line x1="90" y1="520" x2="1190" y2="520" stroke="{BORDER}" stroke-width="2"/>
  <text x="90" y="560" font-family="{MONO}" font-size="20" fill="{MUTED}">github.com/maxime2476</text>
  <text x="1190" y="560" font-family="{MONO}" font-size="20" fill="{MUTED}" text-anchor="end">Maxime Gourguechon</text>
  <g transform="translate(0,52)">{motif()}</g>
</svg>
'''


for slug, repo, title, sub, motif in CARDS:
    (OUT / f"{slug}.svg").write_text(card(slug, repo, title, sub, motif), encoding="utf-8")
print("ok", [f.name for f in sorted(OUT.iterdir())])
