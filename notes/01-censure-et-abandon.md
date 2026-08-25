# Ce que la censure change quand on mesure un abandon

Un contributeur qui n'a rien poussé depuis trois semaines a-t-il quitté le projet ? La question
paraît anodine, elle décide pourtant de tout ce qui suit. La réponse naïve consiste à fixer un
délai, disons trois mois sans commit, et à compter les partants. Elle produit un chiffre. Elle
produit surtout un biais dont personne ne parle dans le tableau de bord final.

## Le problème vient des gens encore là

Prenez un dépôt observé jusqu'à aujourd'hui. Deux profils y coexistent. Le premier a commité
pendant deux ans puis a disparu il y a huit mois : on sait qu'il est parti, et on sait quand.
Le second est arrivé il y a six semaines, il a commité trois fois, et depuis, rien. Il est peut
être parti. Il est peut-être en vacances, en examens, sur une autre branche du projet.

La différence entre les deux n'est pas une nuance. Le premier fournit une durée de vie complète.
Le second fournit une information partielle : sa durée de vie est **au moins** de six semaines,
et on ignore la suite. En analyse de survie, on appelle ça une observation censurée à droite, et
on ne la jette pas.

Les deux traitements naïfs échouent symétriquement. Si on supprime les observations censurées,
il ne reste que les gens partis, et la rétention estimée s'effondre : on a construit un
échantillon de morts et on en déduit une espérance de vie. Si à l'inverse on compte tous les
inactifs récents comme des partants, on transforme la fin de la fenêtre d'observation en épidémie
d'abandons, et le dernier trimestre paraît toujours catastrophique.

## Ce que ça donne en code

Dans [git-survival](https://github.com/maxime2476/git-survival), chaque contributeur ayant au
moins deux commits devient une ligne avec une durée `T` et un indicateur d'événement `E`. La
fenêtre d'inactivité par défaut est de 90 jours. Si le dernier commit remonte à plus de 90 jours,
l'abandon est considéré comme observé, `E = 1`, et la durée court du premier au dernier commit.
Sinon `E = 0`, et la durée court du premier commit jusqu'à la fin de la période d'observation.
Cette seconde ligne dit alors quelque chose de vrai et d'incomplet : cette personne a tenu au
moins ce temps-là.

Kaplan-Meier sait quoi faire de cette information partielle. Chaque observation censurée reste
dans le dénominateur jusqu'à sa date de sortie, puis cesse de compter sans jamais être comptée
comme un abandon. C'est ce qui permet d'annoncer une probabilité de rétention à 100 jours sur un
dépôt encore vivant, ce qu'aucune moyenne d'ancienneté ne sait faire.

## Le détail qui fausse tout avant même le modèle

Une même personne, deux adresses e-mail, et l'outil voit deux contributeurs : le premier
« abandonne » le jour où l'autre commence. Le faux abandon est gratuit et il est fréquent. Le
résolveur d'identités de l'outil existe pour cette seule raison, et il n'est pas théorique : mon
propre historique public porte 128 commits signés « Maxime GOURGUECHON » et 65 signés
« Maxime Gourguechon », deux machines configurées à deux époques différentes. Sur mes dépôts,
un outil naïf compterait un départ qui n'a jamais eu lieu.

## Une limite que je n'ai pas encore corrigée

Le modèle de Cox permet ensuite de conditionner le risque sur des habitudes de travail : part de
commits nocturnes, part de week-end, concentration sur des fichiers que personne d'autre ne
touche, tonalité des messages de commit, et contagion, c'est-à-dire la proportion de
collaborateurs proches ayant déjà décroché.

Cette dernière variable est calculée en fin de fenêtre d'observation, alors qu'elle doit prédire
un événement qui, pour certains contributeurs, a eu lieu avant. La covariable regarde donc un
peu vers le futur. Tant que ce n'est pas repris en formulation à temps variable, le rapport de
risque associé à la contagion se lit comme une corrélation intéressante, pas comme un effet.
C'est écrit ici parce que ça se verra tôt ou tard dans le code, et qu'il vaut mieux que ce soit
moi qui le dise.
