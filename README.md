#  Projet Robotique – Treasure Hunter avec Lidar

##  Objectif du projet

Ce projet a pour objectif de simuler un robot mobile autonome dans un environnement 2D.

Le robot doit :
- se déplacer dans un environnement avec obstacles
- percevoir son environnement via un capteur Lidar
- collecter des trésors
- optimiser son comportement de navigation

Le projet met en œuvre des concepts de :
- programmation orientée objet (POO)
- robotique mobile
- perception (capteurs)
- navigation autonome

---

##  Architecture du projet

Le projet est organisé en plusieurs modules représentant les différentes briques d’un système robotique.

---

##  Structure des fichiers

###  `robot/`

Contient l’ensemble du code principal du robot et de la simulation.

---

###  `robot_mobile.py`
Classe principale représentant le robot.

Fonctionnalités :
- position (x, y)
- orientation
- rayon (collision)
- gestion du moteur
- gestion des capteurs

Ajouts récents :
- support des capteurs (`capteurs`)
- méthode `read_sensors()`

---

###  `moteur.py`
Implémentation des moteurs du robot.

- `MoteurDifferentiel`
- conversion des commandes (vitesse, rotation)

---

###  `controleur.py`
Permet de contrôler le robot :

- `ControleurTerminal` → commandes clavier en terminal
- `ControleurClavierPygame` → commandes clavier avec Pygame

---

###  `environnement.py`
Modélise le monde 2D.

Fonctionnalités :
- gestion des dimensions
- gestion du robot
- gestion des obstacles
- gestion des collisions
- gestion des trésors (ajout récent)

Ajouts récents :
- `treasures`
- `GameState`
- détection de ramassage

---

###  `obstacles.py`
Définition des obstacles.

- `ObstacleCirculaire`
- détection de collision avec le robot

---

###  `game.py`
Gestion de la logique du jeu.

Contient :
- `Treasure` → position, rayon, valeur
- `GameState` → score, timer, statistiques
- `check_treasure_pickup()` → ramassage des trésors

---

###  `vue.py`
Gestion de l’affichage.

#### Modes :
- terminal
- Pygame

Fonctionnalités Pygame :
- affichage du robot
- affichage des obstacles
- affichage des trésors
- affichage du HUD (score, temps, progression)
- affichage des rayons Lidar

---

##  `robot/sensors/`

Gestion des capteurs.

---

###  `capteur.py`
Classe abstraite de capteur.

---

###  `lidar.py`
Implémentation du capteur Lidar.

Fonctionnalités :
- lancer de rayons
- détection des obstacles
- calcul des distances
- stockage des points d’impact

---

##  `robot/navigation/`

Gestion de la navigation autonome.

---

###  `selector.py`
Sélection de la cible.

- sélection du trésor le plus proche

---

###  `go_to_goal.py`
Commande pour se diriger vers une cible.

- calcul de l’angle
- contrôle vitesse + rotation

---

###  `reactive.py`
Navigation basée sur le Lidar.

- analyse des rayons
- sélection des directions libres
- évitement des obstacles

 version avancée :
- choix de la direction la plus sûre
- guidage vers le trésor via espace libre

---

###  `autopilot.py`
Pilote autonome du robot.

Fonctionnalités :
- sélection de la cible
- navigation basée sur le Lidar
- comportement autonome complet

---

##  Fichiers principaux

---

###  `main_terminal.py`
Mode simple en terminal.

- déplacement manuel
- affichage texte

---

###  `main_pygame.py`
Mode principal du projet.

Fonctionnalités :
- simulation complète
- affichage graphique
- Lidar
- navigation autonome
- gestion du score et du temps

---

## Fonctionnement global

1. Initialisation du monde (environnement, obstacles, trésors)
2. Initialisation du robot et de ses capteurs
3. Boucle de simulation :
   - lecture des capteurs
   - prise de décision (autopilot)
   - mouvement du robot
   - gestion des collisions
   - collecte des trésors
   - affichage

---

##  Intelligence du robot

Le robot utilise une navigation en deux niveaux :

### 1. Navigation globale
- choix du trésor cible

### 2. Navigation locale (Lidar)
- analyse des directions libres
- évitement des obstacles
- suivi d’un chemin sûr

---

## Fonctionnalités actuelles

 Déplacement du robot  
 Gestion des collisions  
 Trésors avec score  
 Timer de jeu  
 Affichage Pygame  
 Capteur Lidar  
 Visualisation des rayons  
 Navigation autonome  
 Évitement intelligent des obstacles  

---

##  Améliorations possibles

- stratégie greedy (valeur / distance / temps)
- pathfinding (A*)
- cartes d’occupation
- obstacles dynamiques
- multi-robots

---

##  Lancement

```bash
python main_pygame.py