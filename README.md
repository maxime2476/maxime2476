<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img alt="Maxime Gourguechon, data scientist. Vision par ordinateur, NLP, inférence causale." src="assets/header-light.svg" width="900">
</picture>

**Data scientist et ingénieur IA. Disponible en CDI à partir de septembre 2026, à Paris ou en remote.**

Je cherche une équipe qui met des modèles en production, pas seulement des tableaux de bord.
Écrivez-moi, je réponds sous 24 heures.

[CV en PDF](https://github.com/maxime2476/cv/releases/latest/download/CV_Maxime_Gourguechon.pdf) · [LinkedIn](https://www.linkedin.com/in/maximegourguechon/) · [maximeg2408@gmail.com](mailto:maximeg2408@gmail.com) · [English version](README.en.md)

Salut, moi c'est Maxime. Je termine un master d'économétrie à Lille et je suis en stage de fin
d'études chez Aubay, en vision par ordinateur. Je viens de l'économie, pas de l'informatique :
j'y ai appris à me méfier des corrélations et à vérifier qu'un résultat tient debout avant d'y
croire. Le code, je l'ai appris sur mes projets, et ils sont tous ici.

## Ce que je fais en ce moment

Chez Aubay, je segmente des images de récifs coralliens : un premier modèle repère les coraux,
un second détoure leur contour au pixel près, sur 8 000 images. Le faire marcher sur des photos
propres n'a pas été le plus dur. Le vrai problème est venu des images de plongée réelles, floues
et vidées de leur rouge par l'eau. J'ai fabriqué ces défauts à la main pendant l'entraînement,
pour que le modèle les rencontre avant de les subir : 92 % de précision. J'ai aussi automatisé la
préparation des données, six heures gagnées par cycle, donc deux fois plus d'essais par semaine.

## Le projet qui me représente le mieux

### [causal-impact-lab](https://github.com/maxime2476/causal-impact-lab) · est-ce que remonter les taux d'intérêt détruit vraiment des emplois ?

J'ai écrit la question, et ce qui me ferait répondre non, avant de lancer le moindre calcul. Puis
j'ai mesuré, sur l'emploi américain, État par État et secteur par secteur, de 1994 à 2020.
L'effet va dans le sens attendu partout, mais il reste trop imprécis pour qu'on puisse affirmer
qu'il existe. J'aurais pu ranger ce résultat dans un tiroir et montrer autre chose ; il est en
première page du dépôt, avec sa raison.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/irf-dark.svg">
  <img alt="Effet estimé d'une hausse des taux sur l'emploi, avec une marge d'erreur à 95 % qui contient zéro à tous les horizons." src="assets/irf-light.svg" width="900">
</picture>

<sub>Comment la lire : la ligne orange est l'effet estimé, mois après mois, et la zone claire
autour est la marge d'erreur. Tant qu'elle contient zéro, on ne peut pas affirmer que l'effet
existe. C'est le cas ici, et c'est la conclusion.</sub>

## Les autres

- **[git-survival](https://github.com/maxime2476/git-survival)** : quand un développeur arrête-t-il de contribuer à un projet ? J'applique aux historiques Git les méthodes de survie utilisées en médecine, parce que quelqu'un d'inactif depuis trois semaines n'est pas forcément parti.
- **[bmw-sales-analytics](https://github.com/maxime2476/bmw-sales-analytics)** : 50 000 ventes de voitures, un jeu de données impeccable, et rien à prédire. J'ai prouvé l'absence de signal au lieu de forcer un modèle, puis livré à la place un [simulateur de scénarios](https://maxime2476-bmw-sales-analytics.hf.space) que vous pouvez manipuler en ligne.
- **[heron](https://github.com/maxime2476/heron)** : un moniteur de posture par webcam qui tourne entièrement en local. Écrit parce que je passais mes journées avachi devant l'écran.
- Et [sentiment-powell-nlp](https://github.com/maxime2476/sentiment-powell-nlp), mon premier vrai projet de NLP, sur le ton des conférences de presse de la Fed.

## Pour vérifier par vous-même

- **En 3 minutes**, les deux applications tournent en ligne : [le simulateur BMW](https://maxime2476-bmw-sales-analytics.hf.space) et [causal-impact-lab](https://huggingface.co/spaces/maxime2476/causal-impact-lab).
- **En 20 minutes**, [les résultats de causal-impact-lab](https://github.com/maxime2476/causal-impact-lab/blob/main/docs/results.md) donnent le verdict et ses limites, dans cet ordre.
- **En 1 heure**, clonez le dépôt et lancez `uv sync --all-extras` puis `uv run pytest`, les contrôles qui tournent à chaque modification.

## Trois notes

- [Ce que la censure change quand on mesure un abandon](notes/01-censure-et-abandon.md)
- [Un dataset peut être impeccable et ne rien contenir](notes/02-un-dataset-propre-et-vide.md)
- [Ce qui casse quand on segmente sous l'eau](notes/03-segmenter-sous-l-eau.md)

## Ce que je sais faire

Livré et en service, c'est-à-dire déployé publiquement ou tourné dans le pipeline du stage :
Python, PyTorch, scikit-learn, YOLO, SAM 3, OpenCV, MediaPipe, XGBoost, SHAP, lifelines,
statsmodels, Streamlit, Docker, GitHub Actions.

Utilisé sérieusement en projet ou en mémoire, sans être mis en service : R, MLflow, double
machine learning, projection locale bayésienne, bootstrap non gaussien, DEA et régression de
Simar-Wilson.

Lu, pas encore livré : déploiement managé AWS, monitoring de modèles en production, agents LLM en
production. J'y travaille, en commençant par la certification AWS Machine Learning Engineer.

<sub>Master 1 de finance à l'IAE Saint-Étienne avant Lille, licence d'économie à Rouen,
certifications DataCamp et Voltaire, anglais B2 : le détail est dans le CV, recompilé
automatiquement depuis <a href="https://github.com/maxime2476/cv">son source LaTeX</a> à chaque
modification. Les figures de cette page sont tracées depuis les résultats réels des dépôts et se
régénèrent avec <code>python tools/render_assets.py</code>.</sub>
