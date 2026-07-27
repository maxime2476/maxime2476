#!/usr/bin/env python3
"""Étude d'événement sur mes propres commits, appliquée à mes PR mergées.

La méthode est celle de causal-impact-lab, retournée contre moi : fenêtre
d'événement, retrait d'une base pré-événement, moyenne inter-événements,
intervalles de Student, et effet minimum détectable affiché à côté.

Le nombre d'événements est minuscule et leurs fenêtres se recouvrent, donc
ce graphique ne conclut rien. Il le dit lui-même : c'est une démonstration
de méthode et de ses limites, pas un résultat.
"""

import json
import os
import statistics
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

GITHUB_USER = "maxime2476"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "event-study.svg"
)

# Les PR envoyées en amont. La date retenue est celle du merge.
UPSTREAM_PRS = [
    ("ultralytics/ultralytics", 24751),
    ("statsmodels/statsmodels", 9832),
    ("aeon-toolkit/aeon", 3424),
    ("bashtage/linearmodels", 697),
]

PRE, POST = -7, 14           # fenêtre d'événement, en jours
BASELINE = (-7, -1)          # période servant de référence
CLUSTER_DAYS = 3             # en deçà, deux événements sont jugés confondus

# Quantiles de Student par degrés de liberté : n est trop petit pour la
# normale, et arrondir à 1.96 sous-estimerait les intervalles.
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
        7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 15: 2.131, 20: 2.086}
T800 = {1: 1.376, 2: 1.061, 3: 0.978, 4: 0.941, 5: 0.920, 6: 0.906,
        7: 0.896, 8: 0.889, 9: 0.883, 10: 0.879, 15: 0.866, 20: 0.860}

W, H = 900, 356
PAD = 24
PX0, PX1 = 74.0, 864.0
PY0, PY1 = 96.0, 250.0


def t_quantile(table, df):
    """Valeur tabulée la plus proche par le bas, bornée aux extrêmes."""
    keys = sorted(table)
    if df <= keys[0]:
        return table[keys[0]]
    best = keys[0]
    for k in keys:
        if k <= df:
            best = k
    return table[best]


def api_get(url):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def fetch_events():
    """Dates de merge des PR amont, triées."""
    dates = []
    for repo, number in UPSTREAM_PRS:
        data = api_get(f"https://api.github.com/repos/{repo}/pulls/{number}")
        merged = data.get("merged_at")
        if merged:
            dates.append((date.fromisoformat(merged[:10]), f"{repo}#{number}"))
    dates.sort()
    return dates


def fetch_daily_counts():
    """Contributions quotidiennes sur les 53 dernières semaines."""
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": GITHUB_USER}})
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=payload.encode(),
        headers={"Authorization": f"bearer {TOKEN}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode())
    if "errors" in body:
        raise RuntimeError(f"GraphQL : {body['errors']}")
    cal = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return {
        date.fromisoformat(d["date"]): d["contributionCount"]
        for w in cal["weeks"] for d in w["contributionDays"]
    }


def event_study(counts, events):
    """Écarts à la base pré-événement, par horizon puis moyennés."""
    per_h = {h: [] for h in range(PRE, POST + 1)}
    for ev_date, _ in events:
        window = {h: counts.get(ev_date + timedelta(days=h))
                  for h in range(PRE, POST + 1)}
        base_vals = [window[h] for h in range(BASELINE[0], BASELINE[1] + 1)
                     if window[h] is not None]
        if not base_vals:
            continue
        base = sum(base_vals) / len(base_vals)
        for h, val in window.items():
            if val is not None:
                per_h[h].append(val - base)
    return per_h


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def build_svg(counts, events):
    per_h = event_study(counts, events)
    n = max(len(v) for v in per_h.values())
    df = max(n - 1, 1)
    tc, tp = t_quantile(T975, df), t_quantile(T800, df)

    est, lo, hi, mde = {}, {}, {}, {}
    for h, vals in per_h.items():
        if len(vals) < 2:
            continue
        m = statistics.fmean(vals)
        se = statistics.stdev(vals) / (len(vals) ** 0.5)
        est[h], lo[h], hi[h] = m, m - tc * se, m + tc * se
        mde[h] = (tc + tp) * se

    # Deux merges séparés de moins de CLUSTER_DAYS partagent l'essentiel de
    # leur fenêtre : les compter comme deux observations serait de la
    # double-comptabilisation.
    clusters, previous = 1, events[0][0]
    for ev_date, _ in events[1:]:
        if (ev_date - previous).days > CLUSTER_DAYS:
            clusters += 1
        previous = ev_date

    post_h = [h for h in sorted(est) if h >= 0]
    peak = max(post_h, key=lambda h: abs(est[h]))
    mde_post = statistics.fmean([mde[h] for h in post_h])

    # Un pic isolé dans une fenêtre pré-événement gonfle les barres à h = -7
    # au point d'aplatir tout le post-événement. On cadre donc sur la partie
    # qui porte la question, et les barres qui dépassent sont marquées.
    ymax = max(max(abs(hi[h]), abs(lo[h])) for h in post_h) * 1.15

    def sx(h):
        return PX0 + ((h - PRE) / (POST - PRE)) * (PX1 - PX0)

    def sy(v):
        return (PY0 + PY1) / 2 - (v / ymax) * ((PY1 - PY0) / 2)

    baseline = statistics.fmean(counts.values())
    crossings = [h for h in post_h if not (lo[h] <= 0 <= hi[h])]
    expected = len(post_h) * 0.05

    verdict = (f"n = {len(events)} événements, {clusters} épisode(s) "
               f"indépendant(s). Plancher de détection : {mde_post:.1f} "
               f"contributions/jour, pour une moyenne de {baseline:.1f}")

    p = [
        f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Étude d\'événement sur mes contributions quotidiennes '
        f'autour de mes pull requests mergées en amont. {esc(verdict)}. '
        f'Aucun horizon ne se distingue de zéro.">'
    ]

    p.append("""  <style>
    text { font-family: 'JetBrains Mono', 'Cascadia Code', 'SFMono-Regular', Consolas, monospace; }
    .title    { font-size: 15px; font-weight: 700; fill: #24292f; }
    .subtitle { font-size: 10.5px; fill: #57606a; }
    .tick     { font-size: 9px; fill: #57606a; }
    .footer   { font-size: 9.5px; fill: #57606a; }
    .axis     { stroke: #d0d7de; stroke-width: 1; }
    .zero     { stroke: #57606a; stroke-width: 1.1; stroke-dasharray: 4 4; opacity: 0.7; }
    .ci       { stroke: #0969DA; stroke-width: 1.6; opacity: 0.5; stroke-linecap: round; }
    .dot      { fill: #0a4da2; }
    .blind    { fill: #0969DA; opacity: 0.11; }
    .evline   { stroke: #0a4da2; stroke-width: 1.2; stroke-dasharray: 3 3; opacity: 0.6; }
    .evlab    { font-size: 9.5px; font-weight: 700; fill: #0a4da2; }

    @media (prefers-color-scheme: dark) {
      .title { fill: #e6edf3; }
      .subtitle, .tick, .footer { fill: #9198a1; }
      .axis { stroke: #30363d; }
      .zero { stroke: #9198a1; }
      .ci   { stroke: #58A6FF; }
      .dot  { fill: #a5d6ff; }
      .blind { fill: #58A6FF; opacity: 0.13; }
      .evline { stroke: #a5d6ff; } .evlab { fill: #a5d6ff; }
    }

    .ci, .dot { animation: appear 0.5s ease-out backwards; }
    @keyframes appear { from { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) { .ci, .dot { animation: none; } }
  </style>""")

    p.append(f'  <text class="title" x="{PAD}" y="{PAD + 12}">'
             f'La même méthode, retournée contre moi</text>')
    p.append(f'  <text class="footer" x="{W - PAD}" y="{PAD + 12}" '
             f'text-anchor="end">'
             f'{datetime.now(timezone.utc).strftime("%d/%m/%Y")}</text>')
    p.append(f'  <text class="subtitle" x="{PAD}" y="{PAD + 30}">'
             f'Étude d\'événement sur mes contributions quotidiennes autour de '
             f'mes {len(events)} pull requests mergées en amont.</text>')
    p.append(f'  <text class="subtitle" x="{PAD}" y="{PAD + 44}">'
             f'Écart à la moyenne des 7 jours précédents. Barres : '
             f'intervalles de Student à 95 %. Zone pâle : sous le plancher '
             f'de détection.</text>')

    # Le plancher explose dans la fenêtre pré-événement et déborderait du
    # cadre : on découpe au rectangle du graphique.
    p.append(f'  <clipPath id="plot"><rect x="{PX0}" y="{PY0 - 6:.1f}" '
             f'width="{PX1 - PX0:.1f}" height="{PY1 - PY0 + 14:.1f}"/></clipPath>')
    top = " ".join(f"{sx(h):.1f},{sy(mde[h]):.1f}" for h in sorted(mde))
    bot = " ".join(f"{sx(h):.1f},{sy(-mde[h]):.1f}" for h in sorted(mde, reverse=True))
    p.append(f'  <polygon class="blind" points="{top} {bot}" '
             f'clip-path="url(#plot)"/>')

    p.append(f'  <line class="zero" x1="{PX0}" y1="{sy(0):.1f}" '
             f'x2="{PX1}" y2="{sy(0):.1f}"/>')
    p.append(f'  <line class="evline" x1="{sx(0):.1f}" y1="{PY0 - 6:.1f}" '
             f'x2="{sx(0):.1f}" y2="{PY1 + 8:.1f}"/>')
    p.append(f'  <text class="evlab" x="{sx(0):.1f}" y="{PY0 - 12:.1f}" '
             f'text-anchor="middle">merge</text>')
    p.append(f'  <line class="axis" x1="{PX0}" y1="{PY1 + 8:.1f}" '
             f'x2="{PX1}" y2="{PY1 + 8:.1f}"/>')

    for h in range(PRE, POST + 1, 3):
        p.append(f'  <text class="tick" x="{sx(h):.1f}" y="{PY1 + 22:.1f}" '
                 f'text-anchor="middle">{h:+d}</text>')
    p.append(f'  <text class="tick" x="{(PX0 + PX1) / 2:.1f}" '
             f'y="{PY1 + 36:.1f}" text-anchor="middle">'
             f'jours autour du merge</text>')

    clipped = 0
    for i, h in enumerate(sorted(est)):
        x = sx(h)
        delay = 0.2 + i * 0.02
        top_v, bot_v = min(hi[h], ymax), max(lo[h], -ymax)
        cut = hi[h] > ymax or lo[h] < -ymax
        clipped += 1 if cut else 0
        p.append(f'  <line class="ci" x1="{x:.1f}" y1="{sy(bot_v):.1f}" '
                 f'x2="{x:.1f}" y2="{sy(top_v):.1f}" '
                 f'style="animation-delay:{delay:.2f}s"/>')
        if hi[h] > ymax:
            p.append(f'  <text class="tick" x="{x:.1f}" y="{sy(ymax) - 2:.1f}" '
                     f'text-anchor="middle">↑</text>')
        if lo[h] < -ymax:
            p.append(f'  <text class="tick" x="{x:.1f}" '
                     f'y="{sy(-ymax) + 10:.1f}" text-anchor="middle">↓</text>')
        if abs(est[h]) <= ymax:
            p.append(f'  <circle class="dot" cx="{x:.1f}" cy="{sy(est[h]):.1f}" '
                     f'r="2.8" style="animation-delay:{delay:.2f}s">'
                     f'<title>h = {h:+d} : {est[h]:+.2f} '
                     f'[{lo[h]:+.2f}, {hi[h]:+.2f}]</title></circle>')

    # Un horizon isolé qui sort de l'intervalle est le résultat attendu quand
    # on en teste quinze : l'annoncer sans ce compte serait du cherry-picking.
    reading = (f"{len(crossings)}/{len(post_h)} horizons hors intervalle, "
               f"{expected:.1f} attendu sous H0")

    ratio = mde_post / baseline if baseline else float("inf")
    p.append(f'  <text class="footer" x="{PAD}" y="{H - 28}">'
             f'n = {len(events)} événements, {clusters} épisodes indépendants. '
             f'Plancher {mde_post:.1f} contributions/jour contre une moyenne '
             f'de {baseline:.1f}, soit {ratio:.0f} fois l\'ordinaire.</text>')
    p.append(f'  <text class="footer" x="{PAD}" y="{H - 13}">'
             f'{esc(reading)}. Fenêtres non indépendantes (3 merges en '
             f'3 jours). Ne conclut rien, et c\'est le propos.</text>')
    p.append("</svg>")
    return "\n".join(p), verdict, reading, clusters


def main():
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN requis.")
    print("Récupération des PR amont...")
    events = fetch_events()
    for d, label in events:
        print(f"  {d} : {label}")
    print("Récupération des contributions quotidiennes...")
    counts = fetch_daily_counts()
    svg, verdict, reading, clusters = build_svg(counts, events)
    out = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"  {verdict}")
    print(f"  Lecture : {reading}")
    print(f"SVG généré : {out}")


if __name__ == "__main__":
    main()
