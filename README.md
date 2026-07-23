<div align="center">

  <img src="./assets/header.svg" alt="Maxime Gourguechon, Data Scientist, Économétrie × Machine Learning" width="100%" />

  <a href="https://github.com/maxime2476">
    <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=19&duration=3500&pause=900&color=1F6FEB&center=true&vCenter=true&width=820&lines=corr(X%2C+Y)+%E2%89%A0+X+%E2%89%A0+Y;identification+causale+via+les+chocs;ML+en+production+%3D+éval.+explicabilité" alt="Typing animation" />
  </a>

  <br/><br/>

  <a href="https://www.linkedin.com/in/maxime-gourguechon76/"><img src="https://img.shields.io/badge/LinkedIn-maxime--gourguechon76-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="mailto:maxime.gourguechon76@gmail.com"><img src="https://img.shields.io/badge/Email-Me_contacter-0969DA?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
  <a href="https://huggingface.co/maxime2476"><img src="https://img.shields.io/badge/🤗_Hugging_Face-Démos_live-24292F?style=for-the-badge" alt="Hugging Face" /></a>

</div>

<br/>

## Qui je suis

<img align="right" src="./assets/pulse.svg" width="290" alt="Processus AR(1) simulé, animé" />

Je suis data scientist chez Aubay et diplômé d'un MSc en économétrie et statistiques. Ce qui m'intéresse, c'est de comprendre pourquoi un résultat est vrai : dérivation d'une identification causale, simulation de DGP, interrogation des hypothèses avant de livrer en production.

Sur ce profil, j'ai préféré indiquer des niveaux honnêtes plutôt que d'écrire « expert » partout, et j'ai ajouté une section sur ce que je ne sais pas encore faire.

<br clear="both"/>

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## La méthode

<table>
  <tr>
    <td width="50%" valign="top">
      <h3 align="center">Le Pourquoi, l'économétrie</h3>
      <p align="center"><em>Isoler la causalité de la simple corrélation</em></p>
      <ul>
        <li>Identification causale : effets fixes, hétérogénéité transversale, chocs identifiés, <em>impulse responses</em></li>
        <li>Économétrie de panel, séries temporelles (ARIMA, GARCH), microéconométrie (scoring logistique)</li>
        <li>Hypothèses explicites, stress-tests d'identification, corrections de comparaisons multiples</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3 align="center">Le Comment, le machine learning</h3>
      <p align="center"><em>Prédire juste, expliquer pourquoi, livrer en production</em></p>
      <ul>
        <li>Gradient boosting, deep learning tabulaire, NLP (fine-tuning BERT, embeddings + BiLSTM/CNN)</li>
        <li>IA générative : RAG, agents, LangChain/LangGraph, avec un harnais d'évaluation pour chaque système</li>
        <li>Explicabilité SHAP, décision sous incertitude, Streamlit, Docker, CI/CD</li>
      </ul>
    </td>
  </tr>
</table>

<div align="center">

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#0969DA', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1F6FEB', 'lineColor': '#1F6FEB', 'fontFamily': 'monospace'}}}%%
graph LR
    A[(Données réelles<br/>FRED · BLS · Eurostat · SQL)] --> B[EDA &<br/>Feature Engineering]
    B --> C{Question}
    C -->|Pourquoi ?| D[Identification<br/>causale]
    C -->|Comment ?| E[Entraînement<br/>ML / DL]
    D --> F[Inférence honnête<br/>+ stress-tests]
    E --> G[Validation ·<br/>Explicabilité SHAP]
    F --> H((Livraison<br/>Streamlit · Docker · CI/CD))
    G --> H
```

</div>

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## Les trois projets qui me résument

**[causal-impact-lab](https://github.com/maxime2476/causal-impact-lab)**, le projet le plus proche de ce que j'aime faire. J'y estime l'effet causal des chocs de politique monétaire américaine sur l'emploi sectoral : identification triangulée, local projections, DiD, hétérogénéité dynamique, robustesse exhaustive (specification curves, tests de placebo, chocs synthétiques). Démo Streamlit interactive.

**[ml-from-scratch-R](https://github.com/maxime2476/ml-from-scratch-R)**, mon projet de fin d'études. Je réimplémente chaque modèle de machine learning en R base à partir de sa dérivation mathématique, avec tests par propriété et validation sur des DGP connus. C'est long, c'est utile pour comprendre ce qu'on oublie dans scikit-learn.

**[bmw-sales-analytics](https://github.com/maxime2476/bmw-sales-analytics)**, le projet le plus proche de la production. 50 000 transactions sur quinze ans, de l'économétrie et du gradient boosting pour comprendre et prédire les marges. API externe (Fixer), Docker, CI/CD, déploiement Hugging Face Spaces, SHAP pour l'explicabilité client.

Pour le reste : [sentiment-powell-nlp](https://github.com/maxime2476/sentiment-powell-nlp), du NLP sur les conférences du FOMC (2020–2025), où les clusters *dovish* précèdent les baisses de taux de deux trimestres. Et [panel-project](https://github.com/maxime2476/panel-project), ma première vraie régression de panel sur les déterminants du PIB par habitant en Europe.

<div align="center">
  <img src="./assets/project-tracker.svg" alt="Tableau de progression des projets — mis à jour quotidiennement par GitHub Actions" width="100%" />
</div>

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## Contributions open-source

Je contribue régulièrement aux libs que j'utilise, en particulier quand je trouve des bugs subtils ou des inconsistances. Ici, les plus significatives :

| Projet | Type | Description | Statut |
| :--- | :--- | :--- | :---: |
| **[ultralytics#24751](https://github.com/ultralytics/ultralytics/pull/24751)** | Fix | 2D grayscale NumPy array prediction sur modèles couleur. PIL acceptait, NumPy crashait. Root cause : channel expansion manquante. | ✅ Merged |
| **[ultralytics#24750](https://github.com/ultralytics/ultralytics/issues/24750)** | Issue | Bug report + root cause analysis (LoadPilAndNumpy._single_check). Proposé fix précis avec MRE 4-liner. | 🎯 Fixed |
| **[statsmodels#9832](https://github.com/statsmodels/statsmodels/pull/9832)** | Maintenance | `scipy.interpolate.interp2d` supprimé de SciPy, TableDist devait adapter. Clean up. | ✅ Merged |
| **[statsmodels#9891](https://github.com/statsmodels/statsmodels/issues/9891)** | Issue | `describe()` crashe sur DataFrames vides (0 rows). Symptômes différents par dtype. Analysé root cause, proposé deux approches (fail fast vs graceful). | 🔍 Reviewed |
| **[aeon-toolkit#3424](https://github.com/aeon-toolkit/aeon/pull/3424)** | Bug fix | `TimeSeriesKernelKMeans` mutait le paramètre `kernel` en place. Regression test inclus. | ✅ Merged |
| **[linearmodels#697](https://github.com/bashtage/linearmodels/pull/697)** | Docs | Typos et clarifications dans docstrings. | ✅ Merged |

La plupart de mes issues sont des rapports détaillés : j'aime comprendre le *pourquoi* avant de proposer une fix, et j'essaie de rendre le diagnostic aussi clair que possible pour les mainteneurs.

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## GenAI Lab, la roadmap publique

Mon prochain chantier, c'est l'IA générative, que je veux aborder comme le reste : je ne livrerai pas un système que je ne sais pas évaluer. Beaucoup de démos RAG n'ont aucun harnais d'évaluation ; je veux l'inverse.

| Projet | Objectif | Stack visée | Statut |
| :--- | :--- | :--- | :---: |
| **rag-eval-lab** | Pipeline RAG sur corpus économique (rapports FOMC, Eurostat) avec harnais d'évaluation complet : Recall@k, MRR, nDCG, *faithfulness*, taux d'hallucination, comparaison LLM vs embeddings | LangChain, Ollama, Claude/GPT, DuckDB | 🔄 En cours |
| **agent-econ-analyst** | Agent d'analyse économétrique : orchestration multi-outils (SQL, statsmodels, recherche documentaire), traçabilité complète, garde-fous testés | LangGraph, tool-use, audit trail | 📋 Planifié |
| **llm-fine-tuning** | Prolongement de `sentiment-powell-nlp` : passer du fine-tuning BERT aux LLMs (LoRA/QLoRA), comparaison honnête *prompting* vs RAG vs fine-tuning à coût égal | HuggingFace, Unsloth, Claude API | 📋 Planifié |

Les statuts seront mis à jour au fil des livraisons, métriques comprises, même si elles sont décevantes.

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## Ce que je sais faire, et à quel point

<div align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,r,pytorch,tensorflow,sklearn,postgres,docker,bash,linux,git,githubactions,latex&perline=12" alt="Python, R, PyTorch, TensorFlow, scikit-learn, PostgreSQL, Docker, Bash, Linux, Git, GitHub Actions, LaTeX" />
  </a>
  <br/><br/>
  <img src="https://img.shields.io/badge/Stata-0969DA?style=flat-square" alt="Stata" />
  <img src="https://img.shields.io/badge/Quarto-0969DA?style=flat-square&logo=quarto&logoColor=white" alt="Quarto" />
  <img src="https://img.shields.io/badge/DuckDB-0969DA?style=flat-square&logo=duckdb&logoColor=white" alt="DuckDB" />
  <img src="https://img.shields.io/badge/HuggingFace-0969DA?style=flat-square&logo=huggingface&logoColor=white" alt="HuggingFace" />
  <img src="https://img.shields.io/badge/LangChain-0969DA?style=flat-square&logo=langchain&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Ollama-0969DA?style=flat-square&logo=ollama&logoColor=white" alt="Ollama" />
  <img src="https://img.shields.io/badge/Streamlit-0969DA?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
</div>

<!-- Graphique radar dynamique : calculé chaque nuit depuis les langages,
     imports et configurations de tous mes dépôts publics.
     Généré par .github/workflows/skills-graph.yml -->
<div align="center">
  <img src="./assets/skills-dynamic.svg" alt="Compétences — radar dynamique calculé depuis mes dépôts réels" width="100%" />
</div>

### Ce que je ne sais pas (encore) faire

Kubernetes et l'orchestration à grande échelle. Le deep learning au niveau recherche (je lis les papiers, je ne les écris pas). Le front-end au-delà de Streamlit. Et en GenAI, je débute : je vais comprendre ce qui marche vraiment en le construisant moi-même.

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## Standards

Ce que j'essaie de mettre dans chacun de mes projets sérieux, et qui se vérifie dans les dépôts : un typage strict, des tests à plusieurs niveaux (unitaires, par propriétés, golden, DGP synthétiques), documentation exécutable (Quarto), CI/CD (GitHub Actions), gestion des dépendances (pyproject.toml, renv), reproductibilité (seeds, versioning).

<!-- Scores de qualité auto-générés : analyse statique de chaque dépôt
     (linting, tests, typage, CI/CD, documentation, reproductibilité).
     Généré par .github/workflows/quality-scores.yml -->
<div align="center">
  <img src="./assets/quality-scores.svg" alt="Scores de qualité logicielle — auto-générés depuis les dépôts réels" width="100%" />
</div>

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

## Télémétrie

Mon temps de code réel de la semaine (WakaTime, mis à jour chaque nuit) :

<!--START_SECTION:waka-->
<!--END_SECTION:waka-->

<div align="center">

  <!-- Stats et langages générés par GitHub Action, committés dans le repo :
       aucune dépendance à l'instance publique Vercel (peu fiable, cf. issue #1471 du projet) -->
  <img src="./github-metrics.svg" alt="Statistiques du profil et langages les plus utilisés" width="100%" />

  <br/><br/>

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-activity-graph.vercel.app/graph?username=maxime2476&bg_color=transparent&color=9198a1&line=58A6FF&point=58A6FF&area=true&area_color=58A6FF&hide_border=true" />
    <img src="https://github-readme-activity-graph.vercel.app/graph?username=maxime2476&bg_color=transparent&color=57606a&line=0969DA&point=0969DA&area=true&area_color=1F6FEB&hide_border=true" alt="Activity graph" />
  </picture>

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/maxime2476/maxime2476/output/github-snake-dark.svg" />
    <img src="https://raw.githubusercontent.com/maxime2476/maxime2476/output/github-snake.svg" alt="Snake des contributions" width="100%" />
  </picture>

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-green.svg" />
    <img src="./profile-3d-contrib/profile-green-animate.svg" alt="Contributions sur un an, vue isométrique" width="100%" />
  </picture>

</div>

## En ce moment

Je finalise `ml-from-scratch-R` module par module, je monte `rag-eval-lab` (premiers résultats encourageants sur l'évaluation de faithfulness), et j'approfondis les stress-tests d'identification de `causal-impact-lab`. Je suis ouvert à toute proposition : embauche, collaboration, revue de code, objection sur une méthode.

<div align="center"><img src="./assets/divider.svg" width="100%" alt="" /></div>

Si quelque chose ici vous parle (un projet, une remarque, une proposition, ou même une objection sur un choix de méthode), écrivez-moi : [maxime.gourguechon76@gmail.com](mailto:maxime.gourguechon76@gmail.com)

<sub>Dernière mise à jour : juillet 2026. Ce profil évolue avec mes dépôts.</sub>

<div align="center">

  <br/>

  **Mes dépôts épinglés sont juste en dessous, c'est là que tout se vérifie.**

  <img src="./assets/scroll.svg" width="100%" alt="↓ Les dépôts épinglés se trouvent juste en dessous" />

</div>
