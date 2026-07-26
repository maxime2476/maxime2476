#!/usr/bin/env python3
"""Rend le calendrier de contributions comme la série temporelle qu'il est.

Trois panneaux à partir d'une seule source (l'API GraphQL de GitHub) :

  1. le calendrier jour par jour sur les 53 dernières semaines ;
  2. le profil hebdomadaire, c'est-à-dire la moyenne par jour de la semaine ;
  3. l'autocorrélogramme de la série quotidienne, avec ses bandes à 95 %.

Le troisième panneau est le seul qui apprenne quelque chose : si un pic dépasse
la bande de confiance au retard 7, l'activité a une saisonnalité hebdomadaire.
Le libellé sous le graphique est calculé, jamais écrit à l'avance.
"""

import json
import math
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

GITHUB_USER = "maxime2476"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "commit-calendar.svg"
)

# ── Géométrie ──────────────────────────────────────────────────────────────
W, H = 900, 384
PAD = 24
CELL, GAP = 11.5, 2.5
PITCH = CELL + GAP
GRID_X, GRID_Y = 58.0, 88.0
PANEL_Y = 214.0
PLOT_TOP, PLOT_BOT = 240.0, 330.0
L_X, L_W = 58.0, 330.0
R_X, R_W = 452.0, 390.0

MONTHS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
             "juil.", "août", "sept.", "oct.", "nov.", "déc."]
DAYS_FR = ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."]

MAX_LAG = 21


# ── Données ────────────────────────────────────────────────────────────────

def fetch_calendar():
    """Récupère le calendrier de contributions via l'API GraphQL."""
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount weekday } }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": GITHUB_USER}})
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload.encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode())
    if "errors" in body:
        raise RuntimeError(f"GraphQL : {body['errors']}")
    return body["data"]["user"]["contributionsCollection"]["contributionCalendar"]


# ── Statistiques ───────────────────────────────────────────────────────────

def autocorrelation(series, max_lag):
    """ACF de l'échantillon, estimateur biaisé (dénominateur constant)."""
    n = len(series)
    mean = sum(series) / n
    dev = [x - mean for x in series]
    denom = sum(d * d for d in dev)
    if denom == 0:
        return [0.0] * max_lag
    return [
        sum(dev[t] * dev[t + k] for t in range(n - k)) / denom
        for k in range(1, max_lag + 1)
    ]


def weekday_profile(days):
    """Moyenne de contributions par jour de la semaine (0 = dimanche)."""
    buckets = [[] for _ in range(7)]
    for d in days:
        buckets[d["weekday"]].append(d["contributionCount"])
    return [sum(b) / len(b) if b else 0.0 for b in buckets]


# ── Rendu ──────────────────────────────────────────────────────────────────

def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def level_of(count, thresholds):
    """Indice de palier 0-4 pour la couleur d'une case."""
    if count == 0:
        return 0
    for i, t in enumerate(thresholds):
        if count <= t:
            return i + 1
    return 4


def build_svg(cal):
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    series = [d["contributionCount"] for d in days]
    n = len(series)

    active = sorted(c for c in series if c > 0)
    if active:
        q = [active[int(len(active) * f)] for f in (0.25, 0.5, 0.75)]
        thresholds = sorted(set(q)) or [1]
    else:
        thresholds = [1]

    acf = autocorrelation(series, MAX_LAG)
    band = 1.96 / math.sqrt(n)
    profile = weekday_profile(days)

    # Tester 21 retards à 5 % produit environ un dépassement par pur hasard.
    # Annoncer le pic le plus haut sans le dire serait exactement le travers
    # que ce dépôt reproche aux autres, donc le compte attendu est affiché.
    sig = [k for k, r in enumerate(acf, start=1) if r > band]
    expected = MAX_LAG * 0.05
    r7 = acf[6]

    verdict = (f"{len(sig)}/{MAX_LAG} retards franchissent la bande, "
               f"{expected:.1f} attendu sous H0. Retard 7 : r = {r7:.2f}")

    p = []
    p.append(
        f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Calendrier des contributions de {GITHUB_USER} sur un an, '
        f'accompagné du profil moyen par jour de la semaine et de '
        f'l\'autocorrélogramme de la série quotidienne. {esc(verdict)}.">'
    )

    p.append("""  <style>
    text { font-family: 'JetBrains Mono', 'Cascadia Code', 'SFMono-Regular', Consolas, monospace; }
    .title    { font-size: 15px; font-weight: 700; fill: #24292f; }
    .subtitle { font-size: 10.5px; fill: #57606a; }
    .panel    { font-size: 11px; font-weight: 700; fill: #24292f; }
    .tick     { font-size: 9px; fill: #57606a; }
    .footer   { font-size: 9.5px; fill: #57606a; }
    .axis     { stroke: #d0d7de; stroke-width: 1; }
    .band     { fill: #0969DA; opacity: 0.10; }
    .bandline { stroke: #0969DA; stroke-width: 1; stroke-dasharray: 3 3; opacity: 0.55; }
    .stem     { stroke: #0969DA; stroke-width: 2.5; stroke-linecap: round; }
    .stem-hi  { stroke: #0a4da2; stroke-width: 3.5; stroke-linecap: round; }
    .tip      { fill: #0a4da2; }
    .tiplab   { font-size: 8.5px; font-weight: 700; fill: #0a4da2; }
    .bar      { fill: #0969DA; }
    .cell     { rx: 2.5; ry: 2.5; }
    .l0 { fill: #ebedf0; } .l1 { fill: #b6d8fb; } .l2 { fill: #58A6FF; }
    .l3 { fill: #1F6FEB; } .l4 { fill: #0a4da2; }

    @media (prefers-color-scheme: dark) {
      .title, .panel { fill: #e6edf3; }
      .subtitle, .tick, .footer { fill: #9198a1; }
      .axis { stroke: #30363d; }
      .band { fill: #58A6FF; opacity: 0.12; }
      .bandline { stroke: #58A6FF; }
      .stem { stroke: #58A6FF; } .stem-hi { stroke: #a5d6ff; }
      .tip  { fill: #a5d6ff; } .tiplab { fill: #a5d6ff; }
      .bar  { fill: #58A6FF; }
      .l0 { fill: #161b22; } .l1 { fill: #0d3868; } .l2 { fill: #1f6feb; }
      .l3 { fill: #58A6FF; } .l4 { fill: #a5d6ff; }
    }

    /* L'état de repos est visible et l'animation part de l'invisible avec
       fill-mode backwards. Un client qui ignore les animations affiche donc
       le graphique complet au lieu d'une page blanche. */
    .cell, .bar, .stem, .stem-hi { animation: appear 0.4s ease-out backwards; }
    @keyframes appear { from { opacity: 0; } to { opacity: 1; } }

    @media (prefers-reduced-motion: reduce) {
      .cell, .bar, .stem, .stem-hi { animation: none; }
    }
  </style>""")

    p.append(f'  <text class="title" x="{PAD}" y="{PAD + 12}">'
             f'Un an de commits, lu comme une série temporelle</text>')
    p.append(f'  <text class="subtitle" x="{PAD}" y="{PAD + 30}">'
             f'{cal["totalContributions"]} contributions sur {n} jours. '
             f'Les commits des robots de ce dépôt sont attribués à '
             f'github-actions[bot] et n\'entrent pas dans ce décompte.</text>')

    # ── Panneau 1 : le calendrier ──
    seen_months = set()
    for wi, week in enumerate(weeks):
        first = week["contributionDays"][0]
        month = int(first["date"][5:7])
        if month not in seen_months and int(first["date"][8:10]) <= 7:
            seen_months.add(month)
            x = GRID_X + wi * PITCH
            p.append(f'  <text class="tick" x="{x:.1f}" y="{GRID_Y - 6:.1f}">'
                     f'{MONTHS_FR[month - 1]}</text>')

    for wd in (1, 3, 5):
        y = GRID_Y + wd * PITCH + CELL - 2
        p.append(f'  <text class="tick" x="{PAD + 2}" y="{y:.1f}">{DAYS_FR[wd]}</text>')

    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            lvl = level_of(day["contributionCount"], thresholds)
            x = GRID_X + wi * PITCH
            y = GRID_Y + day["weekday"] * PITCH
            delay = 0.15 + wi * 0.008
            p.append(
                f'  <rect class="cell l{lvl}" x="{x:.1f}" y="{y:.1f}" '
                f'width="{CELL}" height="{CELL}" style="animation-delay:{delay:.2f}s">'
                f'<title>{day["date"]} : {day["contributionCount"]} contribution(s)</title>'
                f'</rect>'
            )

    legend_x = GRID_X + 52 * PITCH - 96
    p.append(f'  <text class="tick" x="{legend_x - 30:.1f}" y="{GRID_Y + 7 * PITCH + 12:.1f}">moins</text>')
    for i in range(5):
        p.append(f'  <rect class="cell l{i}" x="{legend_x + i * 14:.1f}" '
                 f'y="{GRID_Y + 7 * PITCH + 3:.1f}" width="{CELL}" height="{CELL}" '
                 f'style="animation-delay:0.6s"/>')
    p.append(f'  <text class="tick" x="{legend_x + 5 * 14 + 4:.1f}" '
             f'y="{GRID_Y + 7 * PITCH + 12:.1f}">plus</text>')

    # ── Panneau 2 : profil hebdomadaire ──
    p.append(f'  <text class="panel" x="{L_X}" y="{PANEL_Y}">'
             f'Profil hebdomadaire</text>')
    p.append(f'  <text class="subtitle" x="{L_X}" y="{PANEL_Y + 14}">'
             f'contributions moyennes par jour</text>')

    pmax = max(profile) or 1.0
    bar_w = (L_W - 24) / 7
    p.append(f'  <line class="axis" x1="{L_X}" y1="{PLOT_BOT}" '
             f'x2="{L_X + L_W - 24:.1f}" y2="{PLOT_BOT}"/>')
    for i, val in enumerate(profile):
        h = (val / pmax) * (PLOT_BOT - PLOT_TOP)
        x = L_X + i * bar_w + 3
        p.append(
            f'  <rect class="bar" x="{x:.1f}" y="{PLOT_BOT - h:.1f}" '
            f'width="{bar_w - 6:.1f}" height="{h:.1f}" rx="2" '
            f'style="animation-delay:{0.7 + i * 0.05:.2f}s">'
            f'<title>{DAYS_FR[i]} : {val:.2f} par jour</title></rect>'
        )
        p.append(f'  <text class="tick" x="{x + (bar_w - 6) / 2:.1f}" '
                 f'y="{PLOT_BOT + 13:.1f}" text-anchor="middle">'
                 f'{DAYS_FR[i][0].upper()}</text>')

    # ── Panneau 3 : autocorrélogramme ──
    p.append(f'  <text class="panel" x="{R_X}" y="{PANEL_Y}">'
             f'Autocorrélogramme</text>')
    p.append(f'  <text class="subtitle" x="{R_X}" y="{PANEL_Y + 14}">'
             f'retards de 1 à {MAX_LAG} jours, bandes à 95 %</text>')

    amax = max(max(acf), band) * 1.25
    zero_y = PLOT_BOT - 14
    scale = (zero_y - PLOT_TOP) / amax
    band_h = band * scale

    p.append(f'  <rect class="band" x="{R_X}" y="{zero_y - band_h:.1f}" '
             f'width="{R_W - 24:.1f}" height="{band_h * 2:.1f}"/>')
    p.append(f'  <line class="bandline" x1="{R_X}" y1="{zero_y - band_h:.1f}" '
             f'x2="{R_X + R_W - 24:.1f}" y2="{zero_y - band_h:.1f}"/>')
    p.append(f'  <line class="axis" x1="{R_X}" y1="{zero_y:.1f}" '
             f'x2="{R_X + R_W - 24:.1f}" y2="{zero_y:.1f}"/>')

    step = (R_W - 34) / MAX_LAG
    for k, r in enumerate(acf, start=1):
        x = R_X + 8 + (k - 1) * step
        y = zero_y - r * scale
        # Le retard 7 est l'hypothèse posée d'avance : il est mis en valeur
        # qu'il ressorte ou non, pour ne pas ne montrer que ce qui arrange.
        cls = "stem-hi" if k == 7 else "stem"
        p.append(
            f'  <line class="{cls}" x1="{x:.1f}" y1="{zero_y:.1f}" '
            f'x2="{x:.1f}" y2="{y:.1f}" '
            f'style="animation-delay:{0.9 + k * 0.03:.2f}s">'
            f'<title>retard {k} : r = {r:.3f}</title></line>'
        )
        if k == 7:
            p.append(f'  <circle class="tip" cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>')
            p.append(f'  <text class="tiplab" x="{x:.1f}" y="{y - 8:.1f}" '
                     f'text-anchor="middle">semaine</text>')
        if k in (1, 7, 14, 21):
            p.append(f'  <text class="tick" x="{x:.1f}" y="{zero_y + 13:.1f}" '
                     f'text-anchor="middle">{k}</text>')

    p.append(f'  <text class="footer" x="{PAD}" y="{H - 14}">'
             f'ACF : {esc(verdict)}.</text>')
    p.append(f'  <text class="footer" x="{W - PAD}" y="{H - 14}" '
             f'text-anchor="end">calculé le '
             f'{datetime.now(timezone.utc).strftime("%d/%m/%Y")}</text>')

    p.append("</svg>")
    return "\n".join(p), verdict


def main():
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN requis pour l'API GraphQL.")
    print(f"Récupération du calendrier de {GITHUB_USER}...")
    cal = fetch_calendar()
    svg, verdict = build_svg(cal)
    out = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"  {cal['totalContributions']} contributions")
    print(f"  ACF : {verdict}")
    print(f"SVG généré : {out}")


if __name__ == "__main__":
    main()
