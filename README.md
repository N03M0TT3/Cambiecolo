# Cambiecolo
Projet de PPC (3e année département Télécommunications à l'INSA Lyon) avec Christian Hajj

Le projet a pour objectif de mettre en oeuvre les techniques de parallélisation en Python afin de créer un jeu qui se base sur celui du Cambi.

Le principe est le suivant :
- 3 à 5 joueurs peuvent jouer en même temps
- Chacun des joueurs se voit ditribuer 5 cartes au début de la partie
- Ces cartes représentent des moyens de transport
- Il y a autant de moyen de transport que de joueurs
Ainsi, si 3 joueurs se connectent, il y aura 3 moyens de transport différents en cinq exemplaires (pour que chaque joueur ait 5 cartes)

- Une fois les cartes distribuées, les joueurs essayent d'échanger leurs cartes avec les autres afin de récupérer 5 cartes identiques
- Pour cela, un joueur peut proposer d'échanger X cartes
- Un joueur ne peut avoir qu'une seule proposition en cours
- Un autre joueur accepte et propose X de ces cartes
- Les cartes des autres joueurs sont inconnues, le joueur espère donc récupérer des cartes qui l'intéressent.
- Une fois qu'un joueur possède 5 cartes identiques, il peut sonner la cloche annoncant qu'il a gagné
- Si deux joueurs finissent en même temps, le premier à activer la cloche sera désigné vainqueur


# Comment lancer le jeu ?
Il faut d'abord faire tourner <code>Memory.py</code>
Puis lancer le <code>Game.py</code> puis entrer le nombre de joueur souhaité
Enfin, autant de joueurs qu'indiqué peuvent lancer le programme <code>Player.py</code> pour commencer à jouer

