<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img alt="Maxime Gourguechon, data scientist. Vision par ordinateur, NLP, inférence causale." src="assets/header-light.svg" width="900">
</picture>

Je construis des modèles. Du deep learning quand la donnée est riche (images, texte),
de l'économétrie quand la question est causale et qu'une erreur d'interprétation coûte
plus cher qu'un point de F1.

## En ce moment

Stage de fin d'études chez Aubay, en vision par ordinateur, sur la segmentation d'images
de récifs coralliens. Le pipeline se fait en deux temps, YOLO pour la détection puis SAM3
pour le masque, sur 8 000 images, et il tient 92 % de précision. Le vrai travail n'a pas
été le modèle : il a été l'écart entre des photos propres et de vraies plongées. J'ai donc
passé beaucoup de temps sur les augmentations (flou, dérive colorimétrique de l'eau, avec
Albumentations) et sur l'automatisation de la préparation du dataset, ce qui a retiré six
heures par cycle d'entraînement.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-dark.svg">
  <img alt="Pipeline de segmentation : 8 000 images de récifs coralliens, détection YOLO, masques SAM 3, 92 % de précision, avec préparation automatisée du dataset et augmentations ciblées." src="assets/pipeline-light.svg" width="900">
</picture>

À côté, je termine un M2 Économétrie et Statistiques à l'Université de Lille. Je cherche
un CDI à partir de septembre 2026, à Paris ou en remote, sur la partie modèle : data
scientist, ML engineer, AI engineer.

## Une décision, écrite comme j'écris mes ADR

Mes dépôts consignent leurs choix d'architecture dans des ADR datés, parce que dans six mois
j'aurai oublié pourquoi j'ai écarté l'autre option. Autant appliquer le format à la décision
qu'on me demande d'expliquer à chaque entretien.

> **ADR-0000 : quitter la finance pour la data science**
>
> - Statut : accepté
> - Date : septembre 2024
>
> **Contexte.** Licence d'économie à Rouen, puis un M1 de finance et ingénierie financière à
> l'IAE Saint-Étienne. Bonne formation au risque et à la modélisation, mais la partie du travail
> que je voulais faire était l'estimation elle-même, pas la salle de marché.
>
> **Décision.** Basculer sur le master Économétrie et Statistiques de Lille, et rattraper la
> programmation par les projets plutôt que par les cours : un dépôt public à chaque nouvelle
> famille de méthodes, mis en production jusqu'au bout.
>
> **Conséquences.**
> - Je code depuis moins longtemps qu'un profil sorti d'école d'ingénieur, et ça se voit sur les sujets d'infrastructure.
> - En échange je lis un papier d'économétrie appliquée sans traducteur, je repère un biais de sélection avant de lancer le modèle, et je sais reconnaître un résultat qui ne vaut rien.
> - Décision non révisée depuis. Le stage de vision par ordinateur chez Aubay a confirmé le point : ce qui m'intéresse est la construction du modèle.

## Quatre projets qui disent comment je travaille

**[causal-impact-lab](https://github.com/maxime2476/causal-impact-lab)** &nbsp;·&nbsp; l'effet
causal d'un choc de politique monétaire restrictive sur l'emploi américain. La question, le
signe attendu et les conditions de falsification ont été figés avant la première estimation.
Quatre estimateurs plus tard (projection locale sur panel avec interaction, LP-DiD, double
machine learning, LP hiérarchique bayésienne), sur un panel QCEW étendu à 1994-2020 et
descendu au NAICS 3 chiffres, la réponse est un nul propre : le signe attendu sur les 25
horizons, des leads d'event study sans pré-tendance, des magnitudes petites et non
significatives. Le projet le dit comme ça, en
première page. C'est le résultat dont je suis le plus fier, et c'est celui qui n'a pas
« marché ».
<br><sub>`statsmodels` · `double ML` · `inférence bayésienne` · `pytest` · `mypy --strict` · `Docker` · [démo](https://huggingface.co/spaces/maxime2476/causal-impact-lab)</sub>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/irf-dark.svg">
  <img alt="Fonction de réponse estimée : effet relatif d'un choc monétaire restrictif sur l'emploi, panel QCEW 1994-2020, intervalle de confiance à 95 % couvrant zéro à tous les horizons de décision." src="assets/irf-light.svg" width="900">
</picture>

<sub>La figure est tracée depuis `app/assets/headline_irf.csv` du dépôt, sans retouche. C'est
exactement ce que la bande de confiance doit montrer quand un résultat est nul : le signe est
là, la précision ne suit pas.</sub>

**[git-survival](https://github.com/maxime2476/git-survival)** &nbsp;·&nbsp; de l'analyse de
survie appliquée aux historiques Git, pour estimer quand un contributeur décroche. Les mêmes
outils qu'en épidémiologie, sauf que le « décès » est un dernier commit, et que la censure
(le nouveau venu qui n'a simplement pas encore recommité) est traitée pour ce qu'elle est.
Kaplan-Meier pour la courbe globale, Cox pour isoler les facteurs de risque (ratio de commits
nocturnes, bus factor, sentiment des messages de commit, contagion des départs dans l'entourage
direct), un modèle AFT qui choisit sa loi parmi plusieurs. Le rapport sort en HTML autonome.
<br><sub>`lifelines` · `PyDriller` · `TextBlob` · `Plotly` · `Streamlit`</sub>

**[bmw-sales-analytics](https://github.com/maxime2476/bmw-sales-analytics)** &nbsp;·&nbsp; 50 000
transactions BMW sur quinze ans, enrichies par des API macro, carburant, CO₂ et change. Le
pipeline atteint un R² validé croisé d'environ 0,85 sur de la donnée porteuse de signal, mais
ce jeu-là est structurellement propre et vide : aucune variable n'explique le prix. Plutôt que
de livrer un modèle décoratif, j'ai documenté l'absence de signal et réorienté le produit vers
un simulateur de scénarios avec intervalles de crédibilité. Le reste est de la plomberie
assumée : tests, couverture, images multi-étapes, CI, docs publiées.
<br><sub>`XGBoost` · `SHAP` · `DuckDB` · `MLflow` · `Docker` · `GitHub Actions` · [démo](https://maxime2476-bmw-sales-analytics.hf.space)</sub>

<a href="https://maxime2476-bmw-sales-analytics.hf.space"><img alt="Aperçu animé du tableau de bord BMW Sales Analytics : vue exécutive, intégrité des données, économétrie, benchmark ML, explicabilité SHAP, simulateur de scénarios." src="assets/bmw-demo.gif" width="900"></a>

<sub>Le tableau de bord en conditions réelles, de la vue exécutive au simulateur de scénarios.
Cliquer ouvre la démo en ligne.</sub>

**[heron](https://github.com/maxime2476/heron)** &nbsp;·&nbsp; « nommé d'après l'oiseau qui a une
meilleure posture que toi ». Un moniteur de posture par webcam qui tourne en local, sans rien
envoyer nulle part. Un Isolation Forest apprend ma posture de référence pendant un court
calibrage puis signale les dérives, le Face Mesh de MediaPipe compte les clignements pour la
fatigue oculaire, et la capture tourne dans un thread séparé de l'analyse pour que l'affichage
ne lague pas. Écrit d'abord parce que j'en avais besoin.
<br><sub>`MediaPipe` · `OpenCV` · `scikit-learn` · `SQLite` · `Streamlit`</sub>

Il y a aussi [sentiment-powell-nlp](https://github.com/maxime2476/sentiment-powell-nlp), un
pipeline TF-IDF et K-Means sur 40 conférences de presse du FOMC, qui relie le ton hawkish ou
dovish de la Fed aux rendements boursiers à trente jours. C'est plus ancien, mais c'est là que
j'ai commencé à faire du NLP sérieusement.

## Trois façons de vérifier ce que je raconte

Plutôt que d'être cru sur parole, voici comment ouvrir le capot, selon le temps disponible.

`3 min` &nbsp; Les deux applications tournent en ligne, rien à installer :
[le simulateur BMW](https://maxime2476-bmw-sales-analytics.hf.space) et
[causal-impact-lab](https://huggingface.co/spaces/maxime2476/causal-impact-lab).

`20 min` &nbsp; Lire deux fichiers. [Les résultats de causal-impact-lab](https://github.com/maxime2476/causal-impact-lab/blob/main/docs/results.md)
annoncent le verdict, ses caveats et la limite de couverture des données, dans cet ordre.
[Le rapport de capacité prédictive de BMW](https://github.com/maxime2476/bmw-sales-analytics/blob/main/reports/predictive_capability.md)
explique pourquoi le modèle n'était pas déployable et ce que j'ai livré à la place.

`1 h` &nbsp; Cloner `causal-impact-lab`, puis `uv sync --all-extras`, `uv run pytest`,
`uv run ruff check .` et `uv run mypy`. Ce sont exactement les portes de qualité qui tournent en
CI à chaque push, elles doivent passer sur votre machine aussi.

## Trois notes

Un modèle se défend à l'écrit autant qu'au tableau blanc. Trois textes courts, tirés de choses
que j'ai réellement eues à trancher.

- [Ce que la censure change quand on mesure un abandon](notes/01-censure-et-abandon.md) &nbsp;·&nbsp; pourquoi compter les inactifs récents comme des partants fabrique une épidémie d'abandons à la fin de chaque fenêtre d'observation, et ce que ça donne en code.
- [Un dataset peut être impeccable et ne rien contenir](notes/02-un-dataset-propre-et-vide.md) &nbsp;·&nbsp; comment prouver l'absence de signal au lieu de la soupçonner : contrôle positif, test de permutation, uniformité, fuite de cible.
- [Ce qui casse quand on segmente sous l'eau](notes/03-segmenter-sous-l-eau.md) &nbsp;·&nbsp; l'eau absorbe le rouge, la rotation et la symétrie ne protègent de rien, et le gain le plus rentable n'était pas dans le modèle.

## Ma façon de faire, en quatre lignes

- J'écris la question et ce qui la ferait échouer avant de lancer la première régression, sinon on finit toujours par trouver ce qu'on cherchait.
- Un résultat nul se publie comme un autre. Deux de mes projets se terminent sur un nul ou sur un dataset sans signal, et c'est écrit en haut du README, pas dans une note de bas de page.
- Un modèle qui ne tourne que dans mon notebook ne compte pas. Docker, tests, CI et suivi d'expériences font partie du travail, pas de la finition.
- Les choix d'architecture sont datés et justifiés dans des ADR, parce que dans six mois j'aurai oublié pourquoi j'ai écarté l'autre option.

## Les méthodes, rangées par ce que j'en ai vraiment fait

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/methods-dark.svg">
  <img alt="Carte des méthodes en trois colonnes. Livré et en service : YOLO et SAM 3, Albumentations, XGBoost, SHAP, lifelines, statsmodels, projections locales, MediaPipe et OpenCV, DuckDB, Streamlit, Docker, GitHub Actions, pytest et mypy. Utilisé en projet : PyTorch, double machine learning, LP bayésienne, TF-IDF et K-Means, DEA et Simar-Wilson, bootstrap non gaussien, MLflow, R, SAS, SQL, Power BI. Lu, pas encore livré : déploiement managé AWS, monitoring en production, agents LLM en production." src="assets/methods-light.svg" width="900">
</picture>

Une barre de compétence à 90 % ne veut rien dire, alors voici les trois seuls niveaux que je sais
défendre en entretien. La troisième colonne est courte et elle est exacte : ce sont les sujets où
je peux tenir une conversation et pas encore une mise en production.

## Ce que je ne sais pas encore

Je n'ai pas déployé sur une infra cloud de production : mes modèles vivent en Docker et sur
Hugging Face Spaces. Je prépare la certification AWS Machine Learning Engineer Associate pour
combler ça, en visant le déploiement et le monitoring plutôt que le trivia de service. Côté
LLM et agents, je lis et je bricole, mais je n'ai pas encore mis un système à base d'agents
en production. Autant le dire ici plutôt qu'en entretien.

## Le reste

Master 1 Finance et ingénierie financière à l'IAE Saint-Étienne avant Lille, licence d'économie
à Rouen. Mémoire de M1 sur la correction de biais non gaussiens par bootstrap, panel de 15 pays
sur 55 ans, DEA et régression de Simar-Wilson. Certification Data Analyst (DataCamp), Voltaire niveau
professionnel. Anglais B2. En dehors : les marchés, les cryptos, et des parties d'échecs
autour de 1200 ELO.

## Me joindre

[LinkedIn](https://www.linkedin.com/in/maximegourguechon/) ·
[maximeg2408@gmail.com](mailto:maximeg2408@gmail.com) ·
[CV en PDF](https://github.com/maxime2476/cv/releases/latest/download/CV_Maxime_Gourguechon.pdf)

<sub>Le CV est compilé par GitHub Actions depuis [son source LaTeX](https://github.com/maxime2476/cv)
à chaque modification, donc ce lien pointe toujours vers la version courante.</sub>

<sub>Les illustrations de cette page sont des SVG animés écrits pour ce profil, pas des badges
générés : la courbe du haut est une vraie courbe de survie (bande de confiance, marques de
censure, médiane), et la fonction de réponse plus haut est tracée depuis les résultats réels de
<a href="https://github.com/maxime2476/causal-impact-lab">causal-impact-lab</a>, recopiés dans
<code>data/headline_irf.csv</code>. Le GIF est un enregistrement du tableau de bord, pas une
maquette. Tout se régénère avec <code>python tools/render_assets.py</code> : si un chiffre bouge,
l'image bouge avec lui.</sub>
