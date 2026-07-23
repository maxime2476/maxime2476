#!/usr/bin/env python3
"""
Génère un SVG dynamique de suivi de progression des projets.
Utilise l'API GitHub pour récupérer les données réelles de chaque dépôt.
Exécuté quotidiennement par GitHub Actions.
"""

import json
import os
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# ── Configuration ──────────────────────────────────────────────────────────
GITHUB_USER = "maxime2476"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Projets à suivre : (nom_repo, catégorie)
# Catégories : "active", "maintained", "planned", "archived"
PROJECTS = [
    ("causal-impact-lab",    "active"),
    ("ml-from-scratch-R",    "active"),
    ("bmw-sales-analytics",  "active"),
    ("sentiment-powell-nlp",  "maintained"),
    ("panel-project",        "maintained"),
    ("rag-eval-lab",         "planned"),
    ("agent-econ-analyst",   "planned"),
    ("llm-fine-tuning",      "planned"),
]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "project-tracker.svg")

# ── Couleurs du thème ──────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0d1117",
    "card_bg":      "#161b22",
    "header_bg":    "#1F6FEB",
    "row_even":     "#161b22",
    "row_odd":      "#1c2129",
    "text":         "#e6edf3",
    "text_dim":     "#8b949e",
    "border":       "#30363d",
    "active":       "#3fb950",
    "maintained":   "#d29922",
    "planned":      "#8b949e",
    "archived":     "#f85149",
    "bar_start":    "#1F6FEB",
    "bar_end":      "#58A6FF",
    "ci_pass":      "#3fb950",
    "ci_fail":      "#f85149",
    "ci_none":      "#8b949e",
}

# ── Fonctions utilitaires API ──────────────────────────────────────────────

def api_get(url):
    """Requête GET vers l'API GitHub avec authentification."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"⚠ Erreur API {e.code} pour {url}")
        return None
    except Exception as e:
        print(f"⚠ Erreur réseau pour {url}: {e}")
        return None


def get_repo_data(repo_name):
    """Récupère les métadonnées d'un dépôt."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}"
    return api_get(url)


def get_commit_count(repo_name):
    """Compte le nombre total de commits (via l'en-tête Link de pagination)."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits?per_page=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            link = resp.headers.get("Link", "")
            if 'rel="last"' in link:
                # Extraire le numéro de la dernière page
                for part in link.split(","):
                    if 'rel="last"' in part:
                        page = part.split("page=")[-1].split(">")[0]
                        return int(page)
            # Si pas de pagination, il y a 0 ou 1 commit
            data = json.loads(resp.read().decode())
            return len(data)
    except Exception:
        return 0


def get_recent_commits(repo_name, days=30):
    """Compte les commits des N derniers jours."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits?since={since}&per_page=100"
    data = api_get(url)
    return len(data) if isinstance(data, list) else 0


def get_last_commit_date(repo_name):
    """Récupère la date du dernier commit."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits?per_page=1"
    data = api_get(url)
    if data and isinstance(data, list) and len(data) > 0:
        date_str = data[0].get("commit", {}).get("committer", {}).get("date", "")
        if date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return None


def get_ci_status(repo_name):
    """Vérifie le statut du dernier workflow run."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/actions/runs?per_page=1&status=completed"
    data = api_get(url)
    if data and "workflow_runs" in data and len(data["workflow_runs"]) > 0:
        conclusion = data["workflow_runs"][0].get("conclusion", "")
        return conclusion  # "success", "failure", "cancelled", etc.
    return None


def relative_date_fr(dt):
    """Convertit une date en texte relatif en français."""
    if dt is None:
        return "—"
    now = datetime.now(timezone.utc)
    diff = now - dt
    days = diff.days
    if days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            return "à l'instant"
        return f"il y a {hours}h"
    elif days == 1:
        return "hier"
    elif days < 7:
        return f"il y a {days}j"
    elif days < 30:
        weeks = days // 7
        return f"il y a {weeks} sem."
    elif days < 365:
        months = days // 30
        return f"il y a {months} mois"
    else:
        years = days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"


# ── Génération SVG ─────────────────────────────────────────────────────────

def escape_xml(s):
    """Échappe les caractères spéciaux XML."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_svg(projects_data):
    """Génère le SVG complet du tableau de progression."""
    width = 840
    row_height = 44
    header_height = 48
    padding = 20
    title_height = 60
    footer_height = 40
    
    n_rows = len(projects_data)
    total_height = title_height + header_height + (n_rows * row_height) + footer_height + padding * 2
    
    # Trouver le max de commits récents pour normaliser les barres
    max_recent = max((p.get("recent_commits", 0) for p in projects_data), default=1)
    if max_recent == 0:
        max_recent = 1

    svg_parts = []
    
    # En-tête SVG
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">
  <defs>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{COLORS['bar_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{COLORS['bar_end']};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{COLORS['header_bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#58A6FF;stop-opacity:0.8" />
    </linearGradient>
    <filter id="shadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.3"/>
    </filter>
    <clipPath id="roundClip">
      <rect x="0" y="0" width="{width}" height="{total_height}" rx="12" ry="12"/>
    </clipPath>
  </defs>
  
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&amp;display=swap');
    text {{ font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace; }}
    .title {{ font-size: 16px; font-weight: 700; fill: {COLORS['text']}; }}
    .subtitle {{ font-size: 11px; fill: {COLORS['text_dim']}; }}
    .header-text {{ font-size: 11px; font-weight: 600; fill: #ffffff; text-transform: uppercase; letter-spacing: 0.5px; }}
    .cell-text {{ font-size: 12px; fill: {COLORS['text']}; }}
    .cell-dim {{ font-size: 11px; fill: {COLORS['text_dim']}; }}
    .cell-link {{ font-size: 12px; fill: {COLORS['bar_end']}; font-weight: 600; }}
    .footer {{ font-size: 10px; fill: {COLORS['text_dim']}; }}
    .ci-pass {{ fill: {COLORS['ci_pass']}; font-weight: 600; }}
    .ci-fail {{ fill: {COLORS['ci_fail']}; font-weight: 600; }}
    .ci-none {{ fill: {COLORS['ci_none']}; }}
    
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .data-row {{
      animation: fadeIn 0.3s ease-out forwards;
    }}
  </style>
  
  <!-- Fond principal -->
  <rect width="{width}" height="{total_height}" rx="12" ry="12" fill="{COLORS['bg']}" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{total_height - 1}" rx="12" ry="12" fill="none" stroke="{COLORS['border']}" stroke-width="1"/>
''')
    
    # Titre
    y = padding + 20
    svg_parts.append(f'  <text x="{padding + 4}" y="{y}" class="title">📊 Progression des projets</text>')
    svg_parts.append(f'  <text x="{padding + 4}" y="{y + 18}" class="subtitle">Données issues de l\'API GitHub — mise à jour automatique</text>')
    
    # En-tête du tableau
    y = title_height + padding
    cols = [
        (padding + 10, "Projet", 200),
        (padding + 220, "Statut", 80),
        (padding + 310, "Dernier commit", 120),
        (padding + 440, "Commits", 70),
        (padding + 520, "Activité (30j)", 200),
        (padding + 740, "CI", 60),
    ]
    
    svg_parts.append(f'  <rect x="{padding}" y="{y}" width="{width - padding * 2}" height="{header_height}" rx="8" ry="8" fill="url(#headerGrad)" />')
    for cx, label, _ in cols:
        svg_parts.append(f'  <text x="{cx}" y="{y + header_height // 2 + 4}" class="header-text">{label}</text>')
    
    # Lignes de données
    for i, proj in enumerate(projects_data):
        row_y = title_height + padding + header_height + (i * row_height)
        bg_color = COLORS["row_even"] if i % 2 == 0 else COLORS["row_odd"]
        
        # Coins arrondis pour la dernière ligne
        if i == n_rows - 1:
            svg_parts.append(f'  <rect x="{padding}" y="{row_y}" width="{width - padding * 2}" height="{row_height}" rx="0" ry="0" fill="{bg_color}" />')
        else:
            svg_parts.append(f'  <rect x="{padding}" y="{row_y}" width="{width - padding * 2}" height="{row_height}" fill="{bg_color}" />')
        
        text_y = row_y + row_height // 2 + 4
        
        # Nom du projet
        name = proj["name"]
        svg_parts.append(f'  <text x="{cols[0][0]}" y="{text_y}" class="cell-link">{escape_xml(name)}</text>')
        
        # Point de statut
        status = proj["status"]
        dot_color = COLORS.get(status, COLORS["planned"])
        status_labels = {"active": "Actif", "maintained": "Maintenu", "planned": "Planifié", "archived": "Archivé"}
        dot_x = cols[1][0] + 6
        svg_parts.append(f'  <circle cx="{dot_x}" cy="{text_y - 4}" r="5" fill="{dot_color}" />')
        svg_parts.append(f'  <text x="{dot_x + 14}" y="{text_y}" class="cell-dim">{status_labels.get(status, status)}</text>')
        
        # Dernier commit
        last_commit = proj.get("last_commit_text", "—")
        svg_parts.append(f'  <text x="{cols[2][0]}" y="{text_y}" class="cell-dim">{escape_xml(last_commit)}</text>')
        
        # Nombre de commits
        commit_count = proj.get("commit_count", 0)
        svg_parts.append(f'  <text x="{cols[3][0]}" y="{text_y}" class="cell-text">{commit_count}</text>')
        
        # Barre d'activité
        bar_x = cols[4][0]
        bar_y = row_y + row_height // 2 - 6
        bar_max_w = 160
        bar_h = 12
        recent = proj.get("recent_commits", 0)
        bar_w = max(0, (recent / max_recent) * bar_max_w) if max_recent > 0 else 0
        
        # Fond de la barre
        svg_parts.append(f'  <rect x="{bar_x}" y="{bar_y}" width="{bar_max_w}" height="{bar_h}" rx="6" ry="6" fill="{COLORS["border"]}" opacity="0.5" />')
        if bar_w > 0:
            svg_parts.append(f'  <rect x="{bar_x}" y="{bar_y}" width="{bar_w:.1f}" height="{bar_h}" rx="6" ry="6" fill="url(#barGrad)" />')
        # Nombre à droite de la barre
        svg_parts.append(f'  <text x="{bar_x + bar_max_w + 8}" y="{text_y}" class="cell-dim">{recent}</text>')
        
        # CI Status
        ci = proj.get("ci_status")
        ci_x = cols[5][0] + 10
        if ci == "success":
            svg_parts.append(f'  <text x="{ci_x}" y="{text_y}" class="ci-pass">✓</text>')
        elif ci == "failure":
            svg_parts.append(f'  <text x="{ci_x}" y="{text_y}" class="ci-fail">✗</text>')
        else:
            svg_parts.append(f'  <text x="{ci_x}" y="{text_y}" class="ci-none">—</text>')
    
    # Pied de page
    footer_y = total_height - footer_height + 15
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")
    total_commits = sum(p.get("commit_count", 0) for p in projects_data)
    active_count = sum(1 for p in projects_data if p.get("exists", False))
    svg_parts.append(f'  <text x="{padding + 4}" y="{footer_y}" class="footer">{active_count} dépôts actifs · {total_commits} commits au total</text>')
    svg_parts.append(f'  <text x="{width - padding - 4}" y="{footer_y}" class="footer" text-anchor="end">Dernière mise à jour : {now_str}</text>')
    
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"🔍 Analyse des projets de {GITHUB_USER}...")
    projects_data = []
    
    for repo_name, status in PROJECTS:
        print(f"  → {repo_name} ({status})")
        repo = get_repo_data(repo_name)
        
        if repo is None:
            # Le dépôt n'existe pas encore (projet planifié)
            projects_data.append({
                "name": repo_name,
                "status": status,
                "exists": False,
                "last_commit_text": "—",
                "commit_count": 0,
                "recent_commits": 0,
                "ci_status": None,
                "stars": 0,
                "issues": 0,
            })
            print(f"    ⚠ Dépôt introuvable (planifié ?)")
            continue
        
        # Récupérer les données réelles
        commit_count = get_commit_count(repo_name)
        recent_commits = get_recent_commits(repo_name, days=30)
        last_commit_dt = get_last_commit_date(repo_name)
        ci_status = get_ci_status(repo_name)
        
        projects_data.append({
            "name": repo_name,
            "status": status,
            "exists": True,
            "last_commit_text": relative_date_fr(last_commit_dt),
            "commit_count": commit_count,
            "recent_commits": recent_commits,
            "ci_status": ci_status,
            "stars": repo.get("stargazers_count", 0),
            "issues": repo.get("open_issues_count", 0),
        })
        print(f"    ✓ {commit_count} commits, {recent_commits} récents, CI={ci_status}")
    
    # Générer le SVG
    svg_content = generate_svg(projects_data)
    
    # Écrire le fichier
    output_path = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"\n✅ SVG généré : {output_path}")


if __name__ == "__main__":
    main()
