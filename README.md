# Projet Robotique – Treasure Hunter autonome avec LiDAR

## Objectif du projet

Ce projet simule un robot mobile autonome dans un environnement 2D.

Le robot doit :
- se déplacer dans un environnement avec obstacles
- percevoir son environnement avec un capteur LiDAR
- collecter des trésors de différentes valeurs
- revenir dans une maison avant la fin du temps
- survivre à des vagues de difficulté croissante

---

## Principe du jeu

Le projet fonctionne comme un **jeu par vagues** :

- chaque vague génère :
  - des obstacles
  - des trésors
- le robot démarre dans une maison
- il doit sortir, collecter des trésors puis revenir
- si le robot ne revient pas à temps → fin de partie
- si le robot revient → vague suivante

La difficulté augmente :
- plus d’obstacles
- placement plus complexe
- trésors plus éloignés
- temps réduit progressivement

---

## Structure du projet

```

project/
│
├── main_pygame.py
├── main_terminal.py
├── wave_report.csv
│
└── robot/
├── robot_mobile.py
├── moteur.py
├── controleur.py
├── environnement.py
├── obstacles.py
├── game.py
├── vue.py
├── wave_csv.py
│
├── navigation/
│   ├── autopilot.py
│   ├── go_to_goal.py
│   ├── path_utils.py
│   ├── reactive.py
│   └── selector.py
│
└── sensors/
├── capteur.py
└── lidar.py

````

---

## Description des fichiers

### Fichiers principaux

#### `main_pygame.py`
Point d’entrée principal.

Gère :
- le menu (mode IA / joueur)
- le choix du temps
- la création de l’environnement
- la génération des vagues
- la boucle du jeu
- la fin de partie

---

#### `main_terminal.py`
Version simple du projet en terminal.

Permet :
- de tester le robot sans interface graphique
- de contrôler le robot via le clavier

---

## Dossier `robot/`

#### `robot_mobile.py`
Représente le robot.

Contient :
- position (x, y)
- orientation
- rayon
- moteur
- capteurs

---

#### `moteur.py`
Implémente les moteurs.

Contient :
- moteur différentiel (principal)
- mise à jour du mouvement
- bruit moteur (réalisme)

---

#### `controleur.py`
Gestion du contrôle du robot.

- contrôle clavier
- contrôle terminal

---

#### `environnement.py`
Gère le monde.

- obstacles
- trésors
- collisions
- mise à jour globale

---

#### `obstacles.py`
Définit les obstacles (principalement circulaires).

---

#### `game.py`
Logique du jeu.

Contient :
- `Treasure`
- `House`
- `GameState`

Gère :
- score
- vagues
- timer
- retour maison

---

#### `vue.py`
Affichage Pygame.

Affiche :
- robot
- obstacles
- trésors (avec valeur)
- maison
- LiDAR
- score
- temps
- vague
- boutons (pause, fin)

---

#### `wave_csv.py`
Génère le fichier CSV de suivi.

Permet :
- analyser les distances
- suivre les vagues
- comparer théorie vs réalité

---

## Navigation

#### `autopilot.py`
IA principale du robot.

- choix de cible
- décision (trésor ou maison)
- stratégie globale

---

#### `go_to_goal.py`
Déplacement vers une cible.

- calcul angle
- vitesse
- orientation

---

#### `path_utils.py`
Fonctions utilitaires :

- test de ligne libre
- calcul de points intermédiaires

---

#### `reactive.py`
Ancienne navigation réactive.

- basée uniquement sur le LiDAR
- conservée pour comparaison

---

#### `selector.py`
Choix du trésor cible.

---

## Capteurs

#### `capteur.py`
Classe abstraite de capteur.

---

#### `lidar.py`
Capteur principal.

- envoie des rayons
- mesure distances
- détecte obstacles

---

## Fichier CSV

### `wave_report.csv`

Contient :
- données sur les vagues
- distances aux trésors
- estimations de temps
- données d’analyse

Utile pour :
- démonstration
- analyse du comportement du robot

---

## Fonctionnement global

1. Choix du mode (IA / joueur)
2. Choix du temps
3. Génération de la vague
4. Le robot agit :
   - IA → autonome
   - joueur → clavier
5. Collecte des trésors
6. Retour à la maison
7. Nouvelle vague ou fin de partie

---

## Modes disponibles

### Mode IA
- robot autonome
- possibilité d’afficher :
  - capteurs
  - chemins

---

### Mode joueur
Contrôle clavier :

- ↑ avancer
- ↓ reculer
- ← tourner gauche
- → tourner droite
- espace → stop

---

## Lancer le projet

### Installer les dépendances

```bash
pip install pygame
````

---

### Lancer le jeu (mode graphique)

```bash
python main_pygame.py
```

---

### Lancer en mode terminal

```bash
python main_terminal.py
```

---

## Interface

Affiche :

* score
* temps restant
* vague
* mode
* valeur des trésors
* maison (rouge → vert)
* bouton pause
* bouton fin de partie

---

## Fonctionnalités principales

* robot mobile 2D
* LiDAR
* navigation autonome
* mode joueur
* système de vagues
* difficulté progressive
* bruit moteur réaliste
* interface complète
* export CSV

---

## Améliorations possibles

* A* (pathfinding)
* carte d’occupation
* stratégie plus avancée
* multi-robots
* obstacles dynamiques

---

## Conclusion

Le projet met en œuvre :

* capteurs
* navigation
* simulation
* IA simple

La principale difficulté a été de passer d’une navigation réactive à une navigation plus robuste et autonome.