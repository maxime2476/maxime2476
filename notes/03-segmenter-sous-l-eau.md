# Ce qui casse quand on segmente sous l'eau

Un modèle de segmentation qui atteint un bon score sur un jeu de validation propre peut se
comporter très mal sur les images réellement produites en plongée. L'écart ne vient pas du
modèle, il vient de l'écart entre les deux distributions d'images. C'est le sujet principal de
mon stage de fin d'études chez Aubay, sur la segmentation de récifs coralliens.

## Deux étapes valent mieux qu'une

Le pipeline fonctionne en deux temps : un détecteur localise les objets, puis un modèle de
segmentation transforme chaque boîte en masque précis. YOLO d'abord, SAM 3 ensuite, sur environ
8 000 images.

Ce découpage a deux avantages concrets. Le premier est le coût d'annotation : une boîte se trace
en deux secondes, un masque au pixel près demande plusieurs minutes, et la seconde étape permet
de partir d'annotations grossières. Le second est le diagnostic : quand la sortie finale est
mauvaise, on sait immédiatement si le détecteur a raté l'objet ou si le masque a débordé. Un
modèle unique de bout en bout aurait donné un seul score, sans indication de l'endroit où ça
casse.

## L'augmentation générique ne protège de rien

La rotation, la symétrie et le recadrage sont gratuits et présents par défaut partout. Ils
apprennent au modèle qu'un corail vu de biais reste un corail, ce qui est utile et insuffisant.
Aucun de ces trois ne reproduit ce qui dégrade réellement une image sous-marine.

Ce qui la dégrade, c'est la perte de netteté due aux particules en suspension et au mouvement du
plongeur, et c'est la dérive colorimétrique : l'eau absorbe le rouge en premier, si bien que la
même scène vire au bleu-vert à mesure que la profondeur augmente. Un modèle entraîné sur des
images nettes et bien balancées apprend implicitement que le rouge existe, puis se retrouve à
dix mètres de fond où il n'existe plus.

Les augmentations ont donc été choisies pour couvrir précisément ces deux axes, avec
Albumentations : flou de différentes intensités, et déplacement de la balance des couleurs vers
le bleu et le vert. Le critère de succès n'est pas le score sur le jeu de validation d'origine,
qui a plutôt tendance à baisser légèrement, mais la robustesse du modèle sur des images
dégradées. Le pipeline atteint 92 % de précision.

## Le gain le plus rentable n'était pas dans le modèle

Sur la durée du stage, l'automatisation qui a le plus rapporté ne touche pas au réseau de
neurones. Elle porte sur la préparation et la validation du jeu de données : constitution des
découpages, détection des annotations incohérentes, contrôles avant lancement. Six heures de
moins par cycle d'entraînement.

Le chiffre paraît anecdotique jusqu'à ce qu'on le multiplie par le nombre d'expériences. Six
heures gagnées par cycle, c'est la différence entre tester deux hypothèses par semaine et en
tester une. Sur un sujet où le résultat dépend surtout de la qualité des données d'entrée, cette
cadence compte davantage que le choix d'une architecture.

## Ce que je retiens

Le premier réflexe devant un mauvais score en conditions réelles ne devrait pas être de changer
d'architecture, mais de décrire précisément en quoi les images de production diffèrent des images
d'entraînement, puis de fabriquer cette différence à la main pendant l'entraînement. C'est moins
gratifiant qu'un changement de modèle, et c'est ce qui déplace la métrique.
