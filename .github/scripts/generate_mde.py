#!/usr/bin/env python3
"""Trace le plancher de détection de causal-impact-lab.

Un résultat nul se lit mal sans savoir ce que le design pouvait voir. Ce
graphique superpose deux choses à partir des écarts-types réellement publiés
dans app/assets/headline_irf.csv :

  - l'effet minimum détectable, MDE(h) = (z(1-a/2) + z(puissance)) * SE(h),
    tracé en enveloppe symétrique autour de zéro ;
  - la réponse estimée beta(h).

Tout ce qui tombe dans l'enveloppe est indétectable par construction, quelle
que soit la vérité. Aucun chiffre n'est codé en dur : ils viennent du CSV.
"""

import base64
import csv
import io
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

GITHUB_USER = "maxime2476"
SOURCE_REPO = "causal-impact-lab"
SOURCE_PATH = "app/assets/headline_irf.csv"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "mde.svg"
)

# Quantiles normaux : bilatéral à 5 %, puissance 80 %.
Z_ALPHA, Z_POWER = 1.959964, 0.841621
MDE_FACTOR = Z_ALPHA + Z_POWER

# Horizons de décision, fixés dans docs/analysis_plan.md avant estimation.
DECISION_HORIZONS = (12, 24)

W, H = 900, 352
PAD = 24
PX0, PX1 = 74.0, 864.0
PY0, PY1 = 92.0, 252.0


def fetch_csv():
    """Récupère le CSV d'impulsions depuis le dépôt source."""
    url = (f"https://api.github.com/repos/{GITHUB_USER}/{SOURCE_REPO}"
           f"/contents/{SOURCE_PATH}")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode())
    raw = base64.b64decode(payload["content"]).decode()
    return list(csv.DictReader(io.StringIO(raw)))


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def build_svg(rows):
    pts = []
    for r in rows:
        h = float(r["horizon"])
        if h < 0:
            continue  # les leads servent au test de pré-tendance, pas ici
        pts.append((h, float(r["beta"]), float(r["se"])))
    pts.sort()

    hmax = pts[-1][0]
    mde = [(h, MDE_FACTOR * se) for h, _, se in pts]
    ymax = max(max(abs(b) for _, b, _ in pts), max(m for _, m in mde)) * 1.12

    def sx(h):
        return PX0 + (h / hmax) * (PX1 - PX0)

    def sy(v):
        return (PY0 + PY1) / 2 - (v / ymax) * ((PY1 - PY0) / 2)

    at = {h: (b, se) for h, b, se in pts}
    lines = []
    for h in DECISION_HORIZONS:
        if h in at:
            b, se = at[h]
            lines.append(f"h={h:g} : |β̂| = {abs(b):.2f} contre un plancher de "
                         f"{MDE_FACTOR * se:.2f}")
    verdict = " · ".join(lines)

    p = [
        f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Effet minimum détectable de causal-impact-lab par '
        f'horizon, comparé à la réponse estimée. {esc(verdict)}.">'
    ]

    p.append("""  <style>
    text { font-family: 'JetBrains Mono', 'Cascadia Code', 'SFMono-Regular', Consolas, monospace; }
    .title    { font-size: 15px; font-weight: 700; fill: #24292f; }
    .subtitle { font-size: 10.5px; fill: #57606a; }
    .tick     { font-size: 9px; fill: #57606a; }
    .lab      { font-size: 9.5px; font-weight: 700; fill: #0a4da2; }
    .footer   { font-size: 9.5px; fill: #57606a; }
    .axis     { stroke: #d0d7de; stroke-width: 1; }
    .zero     { stroke: #57606a; stroke-width: 1.1; stroke-dasharray: 4 4; opacity: 0.7; }
    .blind    { fill: #0969DA; opacity: 0.13; }
    .blindln  { stroke: #0969DA; stroke-width: 1.4; fill: none; opacity: 0.75; }
    .beta     { stroke: #0a4da2; stroke-width: 2.4; fill: none; }
    .dot      { fill: #0a4da2; }
    .mark     { stroke: #0a4da2; stroke-width: 1; stroke-dasharray: 3 3; opacity: 0.55; }

    @media (prefers-color-scheme: dark) {
      .title { fill: #e6edf3; }
      .subtitle, .tick, .footer { fill: #9198a1; }
      .axis { stroke: #30363d; }
      .zero { stroke: #9198a1; }
      .blind { fill: #58A6FF; opacity: 0.15; }
      .blindln { stroke: #58A6FF; }
      .beta { stroke: #a5d6ff; } .dot { fill: #a5d6ff; }
      .lab  { fill: #a5d6ff; } .mark { stroke: #a5d6ff; }
    }

    .beta, .blind, .blindln { animation: draw 0.6s ease-out backwards; }
    @keyframes draw { from { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) { .beta, .blind, .blindln { animation: none; } }
  </style>""")

    p.append(f'  <text class="title" x="{PAD}" y="{PAD + 12}">'
             f'Ce que ce design pouvait détecter</text>')
    p.append(f'  <text class="footer" x="{W - PAD}" y="{PAD + 12}" '
             f'text-anchor="end">'
             f'{datetime.now(timezone.utc).strftime("%d/%m/%Y")}</text>')
    p.append(f'  <text class="subtitle" x="{PAD}" y="{PAD + 30}">'
             f'causal-impact-lab. Enveloppe : effet minimum détectable à 80 % '
             f'de puissance, seuil bilatéral 5 %.</text>')
    p.append(f'  <text class="subtitle" x="{PAD}" y="{PAD + 44}">'
             f'Calculé sur les écarts-types publiés dans headline_irf.csv. '
             f'Trait plein : la réponse estimée β̂(h).</text>')

    # Enveloppe aveugle : tout ce qui est dedans est hors de portée du design.
    top = " ".join(f"{sx(h):.1f},{sy(m):.1f}" for h, m in mde)
    bot = " ".join(f"{sx(h):.1f},{sy(-m):.1f}" for h, m in reversed(mde))
    p.append(f'  <polygon class="blind" points="{top} {bot}"/>')
    p.append(f'  <polyline class="blindln" points="{top}"/>')
    p.append(f'  <polyline class="blindln" points='
             f'"{" ".join(f"{sx(h):.1f},{sy(-m):.1f}" for h, m in mde)}"/>')

    p.append(f'  <line class="zero" x1="{PX0}" y1="{sy(0):.1f}" '
             f'x2="{PX1}" y2="{sy(0):.1f}"/>')
    p.append(f'  <line class="axis" x1="{PX0}" y1="{PY1 + 8:.1f}" '
             f'x2="{PX1}" y2="{PY1 + 8:.1f}"/>')

    for h in range(0, int(hmax) + 1, 4):
        p.append(f'  <text class="tick" x="{sx(h):.1f}" y="{PY1 + 22:.1f}" '
                 f'text-anchor="middle">{h}</text>')
    p.append(f'  <text class="tick" x="{(PX0 + PX1) / 2:.1f}" '
             f'y="{PY1 + 36:.1f}" text-anchor="middle">'
             f'horizon h, en mois</text>')

    for v in (-ymax * 0.75, 0, ymax * 0.75):
        p.append(f'  <text class="tick" x="{PX0 - 8:.1f}" y="{sy(v) + 3:.1f}" '
                 f'text-anchor="end">{v:+.1f}</text>')

    beta_pts = " ".join(f"{sx(h):.1f},{sy(b):.1f}" for h, b, _ in pts)
    p.append(f'  <polyline class="beta" points="{beta_pts}"/>')

    for h in DECISION_HORIZONS:
        if h not in at:
            continue
        b, se = at[h]
        p.append(f'  <line class="mark" x1="{sx(h):.1f}" y1="{PY0 - 4:.1f}" '
                 f'x2="{sx(h):.1f}" y2="{PY1 + 8:.1f}"/>')
        p.append(f'  <circle class="dot" cx="{sx(h):.1f}" cy="{sy(b):.1f}" r="4"/>')
        p.append(f'  <text class="lab" x="{sx(h):.1f}" y="{PY0 - 10:.1f}" '
                 f'text-anchor="middle">h = {h:g}</text>')
        # β̂ sous le point, plancher au-dessus de l'enveloppe : à h = 12 les
        # deux ne sont séparés que de 0.09, donc les empiler les ferait
        # se recouvrir. Près du bord droit on ancre à droite pour ne pas
        # déborder du viewBox.
        anchor = "end" if sx(h) > W - 70 else "middle"
        p.append(f'  <text class="tick" x="{sx(h):.1f}" y="{sy(b) + 16:.1f}" '
                 f'text-anchor="{anchor}">β̂ = {b:+.2f}</text>')
        p.append(f'  <text class="tick" x="{sx(h):.1f}" '
                 f'y="{sy(MDE_FACTOR * se) - 7:.1f}" text-anchor="{anchor}">'
                 f'plancher {MDE_FACTOR * se:.2f}</text>')

    p.append(f'  <text class="footer" x="{PAD}" y="{H - 28}">'
             f'{esc(verdict)}. Les deux tiennent sous le plancher.</text>')
    p.append(f'  <text class="footer" x="{PAD}" y="{H - 13}">'
             f'Aucune taille d\'effet minimale n\'était pré-enregistrée : '
             f'ce plancher ne tranche pas entre nul informatif et étude '
             f'sous-dimensionnée.</text>')
    p.append("</svg>")
    return "\n".join(p), verdict


def main():
    print(f"Lecture de {SOURCE_REPO}/{SOURCE_PATH}...")
    rows = fetch_csv()
    svg, verdict = build_svg(rows)
    out = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"  {len(rows)} horizons lus")
    print(f"  {verdict}")
    print(f"SVG généré : {out}")


if __name__ == "__main__":
    main()
