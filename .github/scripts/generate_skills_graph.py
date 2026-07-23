#!/usr/bin/env python3
"""
Génère un graphique radar SVG dynamique des compétences,
calculées depuis les dépôts réels via l'API GitHub.
Remplace les barres statiques par une visualisation vivante.
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "skills-dynamic.svg")

# ── Couleurs du thème ──────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0d1117",
    "card_bg":      "#161b22",
    "border":       "#30363d",
    "grid":         "#21262d",
    "grid_accent":  "#30363d",
    "text":         "#e6edf3",
    "text_dim":     "#8b949e",
    "accent":       "#1F6FEB",
    "accent_light": "#58A6FF",
    "fill":         "#1F6FEB",
    "fill_alpha":   "0.15",
    "dot":          "#58A6FF",
    "bar_start":    "#1F6FEB",
    "bar_end":      "#58A6FF",
    "bar_bg":       "#21262d",
    "trend_up":     "#3fb950",
    "trend_stable": "#d29922",
    "trend_down":   "#8b949e",
}

# ── Catégories de compétences et patterns associés ──────────────────────────

SKILL_CATEGORIES = {
    "Économétrie & Stats": {
        "languages": ["R"],
        "imports": [
            "statsmodels", "linearmodels", "scipy.stats", "patsy",
            "arch",  # GARCH
            "causalimpact", "dowhy",
        ],
        "files": ["*.R", "*.r", "*.Rmd", "*.qmd"],
        "config_patterns": ["renv.lock", "DESCRIPTION", ".lintr"],
        "label_short": "Écon.",
    },
    "Python Data Science": {
        "languages": ["Python"],
        "imports": [
            "pandas", "numpy", "scikit-learn", "sklearn",
            "matplotlib", "seaborn", "plotly", "streamlit",
        ],
        "files": ["*.py"],
        "config_patterns": ["pyproject.toml", "requirements.txt"],
        "label_short": "Python DS",
    },
    "ML / Deep Learning": {
        "languages": [],
        "imports": [
            "torch", "pytorch", "tensorflow", "keras",
            "xgboost", "lightgbm", "catboost",
            "sklearn.ensemble", "sklearn.neural_network",
        ],
        "files": [],
        "config_patterns": [],
        "label_short": "ML/DL",
    },
    "NLP & GenAI": {
        "languages": [],
        "imports": [
            "transformers", "langchain", "langgraph", "openai",
            "anthropic", "ollama", "sentence_transformers",
            "huggingface", "tokenizers", "nltk", "spacy",
        ],
        "files": [],
        "config_patterns": [],
        "label_short": "NLP/GenAI",
    },
    "DevOps & CI/CD": {
        "languages": ["Shell", "Dockerfile"],
        "imports": ["docker", "pytest", "pre_commit"],
        "files": ["Dockerfile", "docker-compose.yml", "Makefile", ".pre-commit-config.yaml"],
        "config_patterns": [".github/workflows"],
        "label_short": "DevOps",
    },
    "SQL & Bases de données": {
        "languages": ["PLSQL", "PLpgSQL"],
        "imports": [
            "psycopg2", "sqlalchemy", "duckdb", "sqlite3",
            "pymongo", "redis",
        ],
        "files": ["*.sql"],
        "config_patterns": [],
        "label_short": "SQL/DB",
    },
}

# ── API GitHub ─────────────────────────────────────────────────────────────

def api_get(url):
    """Requête GET vers l'API GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def get_all_repos():
    """Récupère tous les dépôts publics de l'utilisateur."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&page={page}&type=owner"
        data = api_get(url)
        if not data or not isinstance(data, list) or len(data) == 0:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def get_repo_languages(repo_name):
    """Récupère les statistiques de langages d'un dépôt (en bytes)."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/languages"
    return api_get(url) or {}


def get_repo_tree(repo_name):
    """Récupère l'arbre des fichiers du dépôt."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/git/trees/HEAD?recursive=1"
    result = api_get(url)
    if result and "tree" in result:
        return [item["path"] for item in result["tree"] if item["type"] == "blob"]
    return []


def get_last_commit_date(repo_name):
    """Récupère la date du dernier commit."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits?per_page=1"
    data = api_get(url)
    if data and isinstance(data, list) and len(data) > 0:
        date_str = data[0].get("commit", {}).get("committer", {}).get("date", "")
        if date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return None


def search_code_imports(repo_name, keyword):
    """Recherche un mot-clé dans le code d'un dépôt via l'API search."""
    url = f"https://api.github.com/search/code?q={keyword}+repo:{GITHUB_USER}/{repo_name}&per_page=1"
    result = api_get(url)
    if result and "total_count" in result:
        return result["total_count"]
    return 0


# ── Calcul des compétences ─────────────────────────────────────────────────

def compute_skills(repos):
    """Calcule les scores de compétences depuis les données réelles."""
    print(f"📊 Analyse de {len(repos)} dépôts...")
    
    # Accumulateurs par catégorie
    skill_scores = {cat: 0.0 for cat in SKILL_CATEGORIES}
    skill_repos = {cat: set() for cat in SKILL_CATEGORIES}
    skill_recent = {cat: None for cat in SKILL_CATEGORIES}  # date du commit le plus récent
    
    total_bytes = 0
    total_files = 0
    total_commits = 0
    
    for repo in repos:
        repo_name = repo["name"]
        if repo.get("fork", False):
            continue
        
        print(f"  → {repo_name}")
        
        # Langages du dépôt
        languages = get_repo_languages(repo_name)
        repo_bytes = sum(languages.values())
        total_bytes += repo_bytes
        
        # Arbre des fichiers
        files = get_repo_tree(repo_name)
        total_files += len(files)
        
        # Date du dernier commit
        last_commit = get_last_commit_date(repo_name)
        
        # Compter les commits (approximation depuis repo data)
        total_commits += repo.get("size", 0)  # Approximation
        
        # Analyser chaque catégorie
        for cat, config in SKILL_CATEGORIES.items():
            score_contribution = 0
            
            # Score basé sur les langages
            for lang in config["languages"]:
                if lang in languages:
                    # Normaliser par la taille du dépôt
                    score_contribution += languages[lang]
                    skill_repos[cat].add(repo_name)
            
            # Score basé sur les fichiers trouvés
            for pattern in config.get("files", []):
                if pattern.startswith("*"):
                    ext = pattern[1:]
                    matching = [f for f in files if f.endswith(ext)]
                    if matching:
                        score_contribution += len(matching) * 500
                        skill_repos[cat].add(repo_name)
                else:
                    if any(pattern in f for f in files):
                        score_contribution += 2000
                        skill_repos[cat].add(repo_name)
            
            # Score basé sur les configs
            for cfg in config.get("config_patterns", []):
                if any(cfg in f for f in files):
                    score_contribution += 3000
                    skill_repos[cat].add(repo_name)
            
            # Recherche d'imports (limité pour éviter rate limiting)
            for imp in config.get("imports", [])[:3]:
                count = search_code_imports(repo_name, imp)
                if count > 0:
                    score_contribution += count * 200
                    skill_repos[cat].add(repo_name)
            
            skill_scores[cat] += score_contribution
            
            # Mettre à jour la date la plus récente
            if repo_name in skill_repos[cat] and last_commit:
                if skill_recent[cat] is None or last_commit > skill_recent[cat]:
                    skill_recent[cat] = last_commit
    
    # Normaliser les scores (échelle logarithmique pour étaler les valeurs)
    max_raw = max(skill_scores.values()) if skill_scores else 1
    if max_raw == 0:
        max_raw = 1
    
    normalized = {}
    for cat in SKILL_CATEGORIES:
        raw = skill_scores[cat]
        if raw == 0:
            normalized[cat] = 5  # Minimum visible
        else:
            # Log scaling : log(1 + raw) / log(1 + max) * 95 + 5
            log_score = math.log1p(raw) / math.log1p(max_raw)
            normalized[cat] = round(log_score * 90 + 10)  # Entre 10 et 100
    
    # Calculer les tendances
    now = datetime.now(timezone.utc)
    trends = {}
    for cat in SKILL_CATEGORIES:
        dt = skill_recent[cat]
        if dt is None:
            trends[cat] = "none"
        else:
            days_ago = (now - dt).days
            if days_ago <= 14:
                trends[cat] = "up"
            elif days_ago <= 90:
                trends[cat] = "stable"
            else:
                trends[cat] = "down"
    
    return normalized, skill_repos, trends, total_files, total_commits


# ── Génération SVG ─────────────────────────────────────────────────────────

def polar_to_cartesian(cx, cy, r, angle_deg):
    """Convertit des coordonnées polaires en cartésiennes."""
    angle_rad = math.radians(angle_deg - 90)  # -90° pour commencer en haut
    return (cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad))


def generate_radar_chart(cx, cy, radius, scores, categories):
    """Génère le radar chart SVG."""
    n = len(categories)
    angle_step = 360 / n
    parts = []
    
    # Grilles concentriques (20%, 40%, 60%, 80%, 100%)
    for pct in [20, 40, 60, 80, 100]:
        r = radius * pct / 100
        points = []
        for i in range(n):
            angle = i * angle_step
            x, y = polar_to_cartesian(cx, cy, r, angle)
            points.append(f"{x:.1f},{y:.1f}")
        polygon = " ".join(points)
        opacity = "0.6" if pct == 100 else "0.3"
        parts.append(f'    <polygon points="{polygon}" fill="none" '
                     f'stroke="{COLORS["grid"]}" stroke-width="1" opacity="{opacity}" />')
        
        # Label de pourcentage sur le premier axe
        if pct in [20, 60, 100]:
            lx, ly = polar_to_cartesian(cx, cy, r + 2, 0)
            parts.append(f'    <text x="{lx + 4}" y="{ly + 3}" '
                         f'font-size="8" fill="{COLORS["text_dim"]}" opacity="0.5">{pct}%</text>')
    
    # Axes
    for i in range(n):
        angle = i * angle_step
        x, y = polar_to_cartesian(cx, cy, radius, angle)
        parts.append(f'    <line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
                     f'stroke="{COLORS["grid"]}" stroke-width="1" opacity="0.4" />')
    
    # Polygone des données
    cat_names = list(categories.keys())
    data_points = []
    for i, cat in enumerate(cat_names):
        score = scores.get(cat, 0)
        r = radius * score / 100
        angle = i * angle_step
        x, y = polar_to_cartesian(cx, cy, r, angle)
        data_points.append((x, y, score))
    
    # Zone remplie
    fill_polygon = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in data_points)
    parts.append(f'    <polygon points="{fill_polygon}" '
                 f'fill="{COLORS["fill"]}" fill-opacity="{COLORS["fill_alpha"]}" '
                 f'stroke="{COLORS["accent"]}" stroke-width="2" />')
    
    # Points sur les sommets + labels
    for i, (x, y, score) in enumerate(data_points):
        cat = cat_names[i]
        short_label = SKILL_CATEGORIES[cat]["label_short"]
        
        # Point
        parts.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                     f'fill="{COLORS["dot"]}" stroke="{COLORS["bg"]}" stroke-width="2">'
                     f'<animate attributeName="r" values="4;6;4" dur="3s" repeatCount="indefinite" />'
                     f'</circle>')
        
        # Label de l'axe (positionné à l'extérieur)
        angle = i * angle_step
        lx, ly = polar_to_cartesian(cx, cy, radius + 22, angle)
        anchor = "middle"
        if angle > 30 and angle < 150:
            anchor = "start"
        elif angle > 210 and angle < 330:
            anchor = "end"
        
        parts.append(f'    <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
                     f'dominant-baseline="middle" class="axis-label">{short_label}</text>')
    
    return "\n".join(parts)


def generate_progress_bars(x, y, scores, repos_count, trends, categories):
    """Génère les barres de progression avec tendances."""
    parts = []
    bar_width = 320
    bar_h = 10
    spacing = 38
    
    trend_symbols = {
        "up": ("↑", COLORS["trend_up"]),
        "stable": ("→", COLORS["trend_stable"]),
        "down": ("↓", COLORS["trend_down"]),
        "none": ("—", COLORS["text_dim"]),
    }
    
    for i, cat in enumerate(categories):
        my = y + i * spacing
        score = scores.get(cat, 0)
        n_repos = len(repos_count.get(cat, set()))
        trend = trends.get(cat, "none")
        trend_sym, trend_color = trend_symbols.get(trend, ("—", COLORS["text_dim"]))
        
        # Label
        parts.append(f'    <text x="{x}" y="{my}" class="bar-label">{cat}</text>')
        
        # Infos à droite (repos + tendance)
        info_x = x + bar_width + 10
        parts.append(f'    <text x="{info_x}" y="{my + 16}" class="bar-info">{n_repos} repo{"s" if n_repos > 1 else ""}</text>')
        parts.append(f'    <text x="{info_x + 65}" y="{my + 16}" font-size="14" fill="{trend_color}">{trend_sym}</text>')
        
        # Score
        parts.append(f'    <text x="{x + bar_width}" y="{my}" text-anchor="end" class="bar-score">{score}%</text>')
        
        # Barre
        bar_y = my + 6
        filled_w = (score / 100) * bar_width
        
        parts.append(f'    <rect x="{x}" y="{bar_y}" width="{bar_width}" height="{bar_h}" rx="5" fill="{COLORS["bar_bg"]}" />')
        if filled_w > 0:
            parts.append(f'    <rect x="{x}" y="{bar_y}" width="{filled_w:.1f}" height="{bar_h}" rx="5">')
            parts.append(f'      <animate attributeName="width" from="0" to="{filled_w:.1f}" dur="1s" fill="freeze" />')
            parts.append(f'    </rect>')
            # Gradient overlay
            grad_id = f"barGrad_{i}"
            parts.insert(0, f'    <linearGradient id="{grad_id}" x1="0%" x2="100%">'
                            f'<stop offset="0%" stop-color="{COLORS["bar_start"]}"/>'
                            f'<stop offset="100%" stop-color="{COLORS["bar_end"]}"/>'
                            f'</linearGradient>')
            # Replace the last rect to use gradient
            parts[-3] = f'    <rect x="{x}" y="{bar_y}" width="{filled_w:.1f}" height="{bar_h}" rx="5" fill="url(#{grad_id})">'
    
    return "\n".join(parts)


def generate_svg(scores, skill_repos, trends, total_files, total_commits, n_repos):
    """Génère le SVG complet du graphique de compétences."""
    width = 840
    padding = 24
    title_height = 65
    radar_size = 300
    radar_section_h = radar_size + 60
    bars_section_h = len(SKILL_CATEGORIES) * 38 + 20
    footer_height = 45
    
    total_height = title_height + radar_section_h + bars_section_h + footer_height + padding * 2
    
    categories = SKILL_CATEGORIES
    
    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">
  <defs>
    <linearGradient id="mainBarGrad" x1="0%" x2="100%">
      <stop offset="0%" stop-color="{COLORS['bar_start']}"/>
      <stop offset="100%" stop-color="{COLORS['bar_end']}"/>
    </linearGradient>
    <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{COLORS['accent']}" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="{COLORS['accent']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&amp;display=swap');
    text {{ font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace; }}
    .title {{ font-size: 16px; font-weight: 700; fill: {COLORS['text']}; }}
    .subtitle {{ font-size: 11px; fill: {COLORS['text_dim']}; }}
    .axis-label {{ font-size: 11px; font-weight: 600; fill: {COLORS['text']}; }}
    .bar-label {{ font-size: 12px; font-weight: 600; fill: {COLORS['text']}; }}
    .bar-score {{ font-size: 11px; font-weight: 600; fill: {COLORS['accent_light']}; }}
    .bar-info {{ font-size: 9px; fill: {COLORS['text_dim']}; }}
    .footer {{ font-size: 10px; fill: {COLORS['text_dim']}; }}
    
    @keyframes radarPulse {{
      0%, 100% {{ fill-opacity: {COLORS['fill_alpha']}; }}
      50% {{ fill-opacity: 0.25; }}
    }}
  </style>
  
  <!-- Fond -->
  <rect width="{width}" height="{total_height}" rx="12" fill="{COLORS['bg']}" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{total_height - 1}" rx="12" fill="none" stroke="{COLORS['border']}" stroke-width="1"/>
''')
    
    # Titre
    svg.append(f'  <text x="{padding + 4}" y="{padding + 20}" class="title">🎯 Compétences — calculées depuis mes dépôts</text>')
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    svg.append(f'  <text x="{padding + 4}" y="{padding + 38}" class="subtitle">Dernière analyse : {now_str} · Basé sur les langages, imports et configurations réels</text>')
    
    # Radar chart
    radar_cx = width // 2
    radar_cy = title_height + padding + radar_size // 2 + 10
    radar_r = radar_size // 2 - 30
    
    # Glow background
    svg.append(f'  <circle cx="{radar_cx}" cy="{radar_cy}" r="{radar_r + 20}" fill="url(#radarGlow)" />')
    
    svg.append(generate_radar_chart(radar_cx, radar_cy, radar_r, scores, categories))
    
    # Barres de progression (sous le radar)
    bars_y = title_height + radar_section_h + padding
    bars_x = padding + 40
    svg.append(generate_progress_bars(bars_x, bars_y, scores, skill_repos, trends, categories))
    
    # Footer
    footer_y = total_height - footer_height + 20
    n_repos_used = sum(len(s) for s in skill_repos.values())
    svg.append(f'  <text x="{padding + 4}" y="{footer_y}" class="footer">'
               f'Basé sur {n_repos} dépôts · {total_files} fichiers analysés</text>')
    svg.append(f'  <text x="{width - padding - 4}" y="{footer_y}" text-anchor="end" class="footer">'
               f'Mis à jour automatiquement par GitHub Actions</text>')
    
    svg.append("</svg>")
    return "\n".join(svg)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"🎯 Analyse des compétences de {GITHUB_USER}...")
    
    repos = get_all_repos()
    print(f"  📦 {len(repos)} dépôts trouvés")
    
    if not repos:
        print("❌ Aucun dépôt trouvé.")
        return
    
    scores, skill_repos, trends, total_files, total_commits = compute_skills(repos)
    
    print("\n📊 Scores normalisés :")
    for cat, score in scores.items():
        n = len(skill_repos[cat])
        trend = trends[cat]
        print(f"  {cat}: {score}% ({n} repos, tendance: {trend})")
    
    svg_content = generate_svg(scores, skill_repos, trends, total_files, total_commits, len(repos))
    
    output_path = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"\n✅ SVG généré : {output_path}")


if __name__ == "__main__":
    main()
