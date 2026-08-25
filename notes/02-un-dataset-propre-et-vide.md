# Un dataset peut être impeccable et ne rien contenir

50 000 lignes, 11 colonnes, zéro valeur manquante, zéro doublon, quinze ans de ventes
automobiles. Tous les voyants de qualité au vert. Et aucune des variables n'explique quoi que ce
soit de la variable cible. Le cas est plus courant qu'on ne l'admet, et il est piégeux parce que
les contrôles habituels ne le détectent pas : ils vérifient la propreté, pas le contenu.

## Le premier réflexe est le mauvais

Devant un R² proche de zéro, la tentation est de croire au problème de modélisation. On change
d'algorithme, on empile du gradient boosting, on cherche des interactions, on finit par toucher
au découpage train/test jusqu'à ce qu'un chiffre acceptable apparaisse. À la fin il y a un
modèle, il a une métrique, et personne ne sait s'il a appris quelque chose.

Le seul moyen de sortir de cette boucle est de rendre la question falsifiable : avant de
conclure que la donnée est vide, il faut prouver que le pipeline, lui, fonctionne.

## Le contrôle positif

Dans [bmw-sales-analytics](https://github.com/maxime2476/bmw-sales-analytics), le pipeline
identique tourne sur deux cibles. Sur une cible synthétique construite comme une fonction connue
des variables, il obtient un R² de 0,856 sur données non vues. Sur la vraie cible, il obtient
-0,044. La courbe d'apprentissage monte de façon monotone avec la taille de l'échantillon
d'entraînement, et SHAP place en tête exactement les variables qui ont servi à fabriquer la
cible synthétique. Le pipeline sait donc récupérer un signal quand il y en a un, et la validation
croisée à cinq blocs le confirme, 0,849 avec un écart-type de 0,003.

Ce contrôle change la nature de la conclusion. Sans lui, « il n'y a pas de signal » et « je
modélise mal » sont indiscernables, et un jury a raison de préférer la seconde hypothèse.

## Les tests qui tranchent

Trois familles suffisent, et aucune ne dépend du jeu de données particulier.

Le test de permutation compare le score réel à la distribution obtenue en mélangeant les
étiquettes. En régression, le score observé est de -0,111 contre -0,093 pour le nul sur trente
tirages, p = 0,903. En classification, ROC-AUC de 0,482 contre 0,499, p = 0,806. Autrement dit,
le modèle entraîné sur les vraies étiquettes ne fait pas mieux que le même modèle entraîné sur
des étiquettes tirées au hasard.

Le test de Kolmogorov-Smirnov cherche la signature d'une génération synthétique : le kilométrage,
le prix et le volume de ventes ne se distinguent pas d'une loi uniforme (p = 0,259, 0,992 et
0,157). Un prix de voiture uniformément distribué n'existe pas dans la nature.

Le test du khi-deux, enfin, ne rejette l'indépendance d'aucune paire de variables catégorielles :
modèle et région, carburant et transmission, région et couleur, toutes indépendantes. Dans un
vrai marché, la couleur dépend de la région, et le carburant dépend du modèle.

## Le piège qui reste

Une colonne prédisait la cible parfaitement : la classe de ventes valait « High » si et seulement
si le volume dépassait 7 000. Séparabilité totale, R² magnifique, et un modèle qui apprend une
règle de seuil déjà connue. Une fuite de cible est toujours la première explication à écarter
quand un score paraît trop beau, et il faut la chercher avant de se réjouir, pas après.

## Ce que j'en ai fait

Le modèle prédictif n'a pas été livré, parce qu'il n'y avait rien à prédire. Ce qui a été livré à
sa place est un simulateur de scénarios avec intervalles de crédibilité, alimenté par des API
macroéconomiques externes, où l'utilisateur manipule des hypothèses explicites au lieu de
consommer une prédiction sans fondement.

La conclusion utile n'est pas « ce jeu de données est mauvais ». C'est qu'un audit de signal
coûte une journée, qu'il se transfère tel quel d'un projet à l'autre, et qu'il vaut mieux le
payer au début que d'expliquer six mois plus tard pourquoi un modèle en production produit du
bruit bien formaté.
