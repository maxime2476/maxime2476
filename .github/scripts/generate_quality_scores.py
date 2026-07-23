#!/usr/bin/env python3
"""
Génère un SVG de scores de qualité logicielle auto-générés.
Analyse les dépôts réels via l'API GitHub pour calculer des métriques
de linting, tests, typage, CI/CD, documentation et reproductibilité.
"""

import json
import os
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────
GITHUB_USER = "maxime2476"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Projets à analyser
REPOS = [
    "causal-impact-lab",
    "bmw-sales-analytics",
    "sentiment-powell-nlp",
    "ml-from-scratch-R",
]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "quality-scores.svg")

# ── Couleurs ───────────────────────────────────────────────────────────────
COLORS = {
    "bg":         "#0d1117",
    "card_bg":    "#161b22",
    "border":     "#30363d",
    "text":       "#e6edf3",
    "text_dim":   "#8b949e",
    "excellent":  "#3fb950",
    "good":       "#d29922",
    "fair":       "#db6d28",
    "poor":       "#f85149",
    "bar_bg":     "#21262d",
    "accent":     "#1F6FEB",
    "accent_light": "#58A6FF",
}

# Métriques et leurs poids
METRICS = [
    ("Linting",          "lint",   0.15),
    ("Tests",            "test",   0.25),
    ("Typage",           "type",   0.15),
    ("CI/CD",            "ci",     0.15),
    ("Documentation",    "doc",    0.15),
    ("Reproductibilité", "repro",  0.15),
]

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
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return None
    except Exception:
        return None


def check_file_exists(repo, path):
    """Vérifie si un fichier existe dans le dépôt."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}"
    result = api_get(url)
    return result is not None


def get_file_content(repo, path):
    """Récupère le contenu d'un fichier (décodé base64)."""
    import base64
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}"
    result = api_get(url)
    if result and "content" in result:
        try:
            return base64.b64decode(result["content"]).decode("utf-8", errors="replace")
        except Exception:
            return ""
    return ""


def get_tree(repo, recursive=True):
    """Récupère l'arbre complet du dépôt."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/git/trees/HEAD?recursive=1"
    result = api_get(url)
    if result and "tree" in result:
        return [item["path"] for item in result["tree"] if item["type"] == "blob"]
    return []


def list_workflows(repo):
    """Liste les fichiers de workflow GitHub Actions."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/.github/workflows"
    result = api_get(url)
    if isinstance(result, list):
        return [f["name"] for f in result]
    return []


# ── Calcul des scores ─────────────────────────────────────────────────────

def compute_scores(repo):
    """Calcule les 6 scores de qualité pour un dépôt."""
    print(f"  🔍 Analyse de {repo}...")
    
    all_files = get_tree(repo)
    if not all_files:
        return None
    
    is_r = any(f.endswith(".R") or f.endswith(".r") for f in all_files)
    is_python = any(f.endswith(".py") for f in all_files)
    
    scores = {}
    
    # ── Linting ──
    lint_score = 0
    lint_configs = [
        "ruff.toml", ".ruff.toml", ".flake8", ".pylintrc",
        "setup.cfg", ".lintr", ".styler.R"
    ]
    for cfg in lint_configs:
        if cfg in all_files:
            lint_score += 30
            break
    
    # Vérifier pyproject.toml pour [tool.ruff] ou [tool.pylint]
    if "pyproject.toml" in all_files:
        content = get_file_content(repo, "pyproject.toml")
        if "tool.ruff" in content or "tool.pylint" in content or "tool.flake8" in content:
            lint_score += 30
    
    # Vérifier la CI pour le linting
    workflows = list_workflows(repo)
    for wf in workflows:
        wf_content = get_file_content(repo, f".github/workflows/{wf}")
        if any(kw in wf_content.lower() for kw in ["ruff", "flake8", "pylint", "lint", "lintr"]):
            lint_score += 40
            break
    
    # pre-commit
    if ".pre-commit-config.yaml" in all_files:
        lint_score += 20
    
    scores["lint"] = min(100, lint_score)
    
    # ── Tests ──
    test_score = 0
    test_files = [f for f in all_files if
                  f.startswith("tests/") or f.startswith("test/") or
                  "test_" in os.path.basename(f) or "_test." in f or
                  f.startswith("testthat/") or "/testthat/" in f or
                  f.endswith("_test.R") or f.endswith("_test.r")]
    
    n_test_files = len(test_files)
    if n_test_files > 0:
        test_score += min(40, n_test_files * 8)
    
    # Vérifier la CI pour les tests
    for wf in workflows:
        wf_content = get_file_content(repo, f".github/workflows/{wf}")
        if any(kw in wf_content.lower() for kw in ["pytest", "testthat", "test", "unittest"]):
            test_score += 30
            break
    
    # Fichier conftest.py ou helper de test
    if any("conftest" in f for f in all_files):
        test_score += 15
    
    # coverage
    if any("coverage" in f.lower() or ".coveragerc" in f for f in all_files):
        test_score += 15
    
    scores["test"] = min(100, test_score)
    
    # ── Typage ──
    type_score = 0
    if is_python:
        # mypy config
        mypy_configs = ["mypy.ini", ".mypy.ini"]
        for cfg in mypy_configs:
            if cfg in all_files:
                type_score += 30
                break
        
        if "pyproject.toml" in all_files:
            content = get_file_content(repo, "pyproject.toml")
            if "tool.mypy" in content:
                type_score += 30
            if "strict" in content and "mypy" in content:
                type_score += 20
        
        # py.typed marker
        if any("py.typed" in f for f in all_files):
            type_score += 20
        
        # Compter les fichiers .pyi
        pyi_files = [f for f in all_files if f.endswith(".pyi")]
        if pyi_files:
            type_score += 15
        
        # Annotations dans le code (heuristique : vérifier quelques fichiers)
        py_files = [f for f in all_files if f.endswith(".py")][:5]
        has_annotations = False
        for pf in py_files:
            content = get_file_content(repo, pf)
            if ": " in content and ("-> " in content or "-> None" in content):
                has_annotations = True
                break
        if has_annotations:
            type_score += 20
    elif is_r:
        # R n'a pas de typage statique natif, mais on peut vérifier roxygen
        if any("roxygen" in f.lower() or f.endswith(".Rd") for f in all_files):
            type_score += 50
        if any("NAMESPACE" in f for f in all_files):
            type_score += 30
    
    scores["type"] = min(100, type_score)
    
    # ── CI/CD ──
    ci_score = 0
    if workflows:
        ci_score += min(40, len(workflows) * 20)
    
    if any("Dockerfile" in f or "dockerfile" in f.lower() for f in all_files):
        ci_score += 20
    
    if any("docker-compose" in f.lower() for f in all_files):
        ci_score += 15
    
    if any("Makefile" in f for f in all_files):
        ci_score += 10
    
    # Vérifier les badges dans le README
    if "README.md" in all_files:
        readme = get_file_content(repo, "README.md")
        if "actions/workflows" in readme or "github.com" in readme:
            ci_score += 15
    
    scores["ci"] = min(100, ci_score)
    
    # ── Documentation ──
    doc_score = 0
    if "README.md" in all_files:
        readme = get_file_content(repo, "README.md")
        readme_len = len(readme)
        if readme_len > 2000:
            doc_score += 30
        elif readme_len > 500:
            doc_score += 20
        elif readme_len > 0:
            doc_score += 10
    
    # Quarto / Sphinx / docs
    if any(f.endswith(".qmd") for f in all_files):
        doc_score += 25
    if any("docs/" in f or "doc/" in f for f in all_files):
        doc_score += 20
    if any(f.endswith(".Rd") for f in all_files):
        doc_score += 20
    
    # Docstrings (heuristique)
    if is_python:
        py_files = [f for f in all_files if f.endswith(".py")][:5]
        has_docstrings = False
        for pf in py_files:
            content = get_file_content(repo, pf)
            if '"""' in content or "'''" in content:
                has_docstrings = True
                break
        if has_docstrings:
            doc_score += 25
    
    # CHANGELOG
    if any("CHANGELOG" in f.upper() for f in all_files):
        doc_score += 10
    
    scores["doc"] = min(100, doc_score)
    
    # ── Reproductibilité ──
    repro_score = 0
    
    dep_files = ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg",
                 "Pipfile", "poetry.lock", "renv.lock", "DESCRIPTION"]
    for dep in dep_files:
        if dep in all_files:
            repro_score += 20
            break
    
    if "renv.lock" in all_files or "poetry.lock" in all_files or "Pipfile.lock" in all_files:
        repro_score += 20
    
    if "pyproject.toml" in all_files:
        repro_score += 15
    
    # Seeds / reproductibilité
    py_files = [f for f in all_files if f.endswith(".py") or f.endswith(".R")][:8]
    has_seed = False
    for pf in py_files:
        content = get_file_content(repo, pf)
        if "seed" in content.lower() or "random_state" in content.lower() or "set.seed" in content:
            has_seed = True
            break
    if has_seed:
        repro_score += 20
    
    # .gitignore
    if ".gitignore" in all_files:
        repro_score += 10
    
    # LICENSE
    if any("LICENSE" in f.upper() for f in all_files):
        repro_score += 15
    
    scores["repro"] = min(100, repro_score)
    
    return scores


def compute_overall(scores):
    """Calcule le score global pondéré."""
    total = 0
    for _, key, weight in METRICS:
        total += scores.get(key, 0) * weight
    return round(total)


# ── Génération SVG ─────────────────────────────────────────────────────────

def score_color(score):
    """Retourne la couleur selon le score."""
    if score >= 80:
        return COLORS["excellent"]
    elif score >= 60:
        return COLORS["good"]
    elif score >= 40:
        return COLORS["fair"]
    else:
        return COLORS["poor"]


def generate_donut(cx, cy, radius, score, color):
    """Génère un donut chart SVG."""
    circumference = 2 * math.pi * radius
    filled = (score / 100) * circumference
    gap = circumference - filled
    
    parts = []
    # Fond du donut
    parts.append(f'    <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
                 f'stroke="{COLORS["bar_bg"]}" stroke-width="8" />')
    # Arc rempli (rotation -90° pour commencer en haut)
    parts.append(f'    <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
                 f'stroke="{color}" stroke-width="8" '
                 f'stroke-dasharray="{filled:.1f} {gap:.1f}" '
                 f'stroke-dashoffset="0" '
                 f'transform="rotate(-90 {cx} {cy})" '
                 f'stroke-linecap="round" />')
    # Texte du score au centre
    parts.append(f'    <text x="{cx}" y="{cy + 2}" text-anchor="middle" '
                 f'dominant-baseline="middle" class="score-text" fill="{color}">{score}</text>')
    parts.append(f'    <text x="{cx}" y="{cy + 16}" text-anchor="middle" '
                 f'class="score-label" fill="{COLORS["text_dim"]}">/ 100</text>')
    return "\n".join(parts)


def generate_metric_bars(x, y, scores, bar_width=140):
    """Génère les barres de métriques individuelles."""
    parts = []
    bar_h = 6
    spacing = 22
    
    for i, (label, key, _) in enumerate(METRICS):
        my = y + i * spacing
        score = scores.get(key, 0)
        color = score_color(score)
        filled_w = (score / 100) * bar_width
        
        # Label
        parts.append(f'    <text x="{x}" y="{my}" class="metric-label">{label}</text>')
        # Score value
        parts.append(f'    <text x="{x + bar_width + 30}" y="{my}" class="metric-value" fill="{color}">{score}</text>')
        # Bar background
        bar_y = my + 4
        parts.append(f'    <rect x="{x}" y="{bar_y}" width="{bar_width}" height="{bar_h}" rx="3" fill="{COLORS["bar_bg"]}" />')
        # Bar filled
        if filled_w > 0:
            parts.append(f'    <rect x="{x}" y="{bar_y}" width="{filled_w:.1f}" height="{bar_h}" rx="3" fill="{color}" opacity="0.85" />')
    
    return "\n".join(parts)


def generate_svg(all_scores):
    """Génère le SVG complet des scores de qualité."""
    width = 840
    card_width = 380
    card_height = 240
    padding = 20
    title_height = 65
    gap = 20
    
    # Calculer la hauteur : 2 colonnes
    n_rows = math.ceil(len(all_scores) / 2)
    cards_height = n_rows * (card_height + gap) - gap
    footer_height = 40
    total_height = title_height + padding + cards_height + footer_height + padding
    
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">
  <defs>
    <filter id="cardShadow">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&amp;display=swap');
    text {{ font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace; }}
    .title {{ font-size: 16px; font-weight: 700; fill: {COLORS['text']}; }}
    .subtitle {{ font-size: 11px; fill: {COLORS['text_dim']}; }}
    .card-title {{ font-size: 13px; font-weight: 700; fill: {COLORS['accent_light']}; }}
    .score-text {{ font-size: 22px; font-weight: 700; }}
    .score-label {{ font-size: 9px; }}
    .metric-label {{ font-size: 10px; fill: {COLORS['text_dim']}; }}
    .metric-value {{ font-size: 10px; font-weight: 600; }}
    .footer {{ font-size: 10px; fill: {COLORS['text_dim']}; }}
    
    @keyframes scoreReveal {{
      from {{ stroke-dashoffset: 200; }}
    }}
  </style>
  
  <!-- Fond -->
  <rect width="{width}" height="{total_height}" rx="12" fill="{COLORS['bg']}" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{total_height - 1}" rx="12" fill="none" stroke="{COLORS['border']}" stroke-width="1"/>
''')
    
    # Titre
    svg_parts.append(f'  <text x="{padding + 4}" y="{padding + 20}" class="title">🏗️ Qualité logicielle — scores auto-générés</text>')
    svg_parts.append(f'  <text x="{padding + 4}" y="{padding + 38}" class="subtitle">Analyse statique des dépôts via l\'API GitHub : linting, tests, typage, CI/CD, documentation, reproductibilité</text>')
    
    # Cartes
    for i, (repo_name, scores) in enumerate(all_scores.items()):
        col = i % 2
        row = i // 2
        
        cx = padding + col * (card_width + gap)
        cy = title_height + padding + row * (card_height + gap)
        
        overall = compute_overall(scores)
        color = score_color(overall)
        
        # Fond de la carte
        svg_parts.append(f'  <rect x="{cx}" y="{cy}" width="{card_width}" height="{card_height}" rx="10" fill="{COLORS["card_bg"]}" stroke="{COLORS["border"]}" stroke-width="1" />')
        
        # Nom du projet
        svg_parts.append(f'  <text x="{cx + 15}" y="{cy + 28}" class="card-title">{repo_name}</text>')
        
        # Donut chart
        donut_cx = cx + 65
        donut_cy = cy + 100
        svg_parts.append(generate_donut(donut_cx, donut_cy, 35, overall, color))
        
        # Indicateur textuel
        level_labels = {
            "excellent": "Excellent",
            "good": "Bon",
            "fair": "Correct",
            "poor": "À améliorer",
        }
        level_key = "excellent" if overall >= 80 else "good" if overall >= 60 else "fair" if overall >= 40 else "poor"
        svg_parts.append(f'  <text x="{donut_cx}" y="{donut_cy + 50}" text-anchor="middle" class="metric-label" fill="{color}">{level_labels[level_key]}</text>')
        
        # Barres de métriques
        bars_x = cx + 140
        bars_y = cy + 52
        svg_parts.append(generate_metric_bars(bars_x, bars_y, scores, bar_width=120))
    
    # Footer
    footer_y = total_height - footer_height + 15
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")
    avg_score = round(sum(compute_overall(s) for s in all_scores.values()) / max(len(all_scores), 1))
    svg_parts.append(f'  <text x="{padding + 4}" y="{footer_y}" class="footer">Score moyen : {avg_score}/100 · {len(all_scores)} dépôts analysés</text>')
    svg_parts.append(f'  <text x="{width - padding - 4}" y="{footer_y}" class="footer" text-anchor="end">Dernière analyse : {now_str}</text>')
    
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"🔍 Analyse de la qualité logicielle des dépôts de {GITHUB_USER}...")
    all_scores = {}
    
    for repo in REPOS:
        scores = compute_scores(repo)
        if scores:
            all_scores[repo] = scores
            overall = compute_overall(scores)
            print(f"  ✓ {repo} : {overall}/100")
            for label, key, _ in METRICS:
                print(f"    {label}: {scores[key]}/100")
        else:
            print(f"  ⚠ {repo} : introuvable ou vide")
    
    if not all_scores:
        print("❌ Aucun dépôt analysable trouvé.")
        return
    
    svg_content = generate_svg(all_scores)
    
    output_path = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"\n✅ SVG généré : {output_path}")


if __name__ == "__main__":
    main()
