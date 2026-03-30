import math
import random

from robot import game
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire
from robot.game import Treasure, GameState
from robot.sensors import Lidar
from robot.navigation import AutoPilot


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def point_is_valid_for_circle(env, x, y, radius):
    """
    Vérifie qu'un cercle (x, y, radius) reste dans la map
    et ne touche aucun obstacle existant.
    """
    if x - radius < 0.0 or x + radius > env.largeur:
        return False
    if y - radius < 0.0 or y + radius > env.hauteur:
        return False

    for obs in env.obstacles:
        if distance(x, y, obs.x, obs.y) < (radius + obs.rayon + 0.20):
            return False

    return True


def treasure_is_valid(env, x, y, radius, robot, treasures):
    """
    Vérifie qu'un trésor :
    - reste dans la map
    - ne touche pas un obstacle
    - n'est pas collé au robot
    - n'est pas collé à un autre trésor
    """
    if x - radius < 0.0 or x + radius > env.largeur:
        return False
    if y - radius < 0.0 or y + radius > env.hauteur:
        return False

    # pas collé au robot
    if distance(x, y, robot.x, robot.y) < (radius + robot.rayon + 0.60):
        return False

    # pas collé aux obstacles
    for obs in env.obstacles:
        if distance(x, y, obs.x, obs.y) < (radius + obs.rayon + 0.35):
            return False

    # pas collé aux autres trésors
    for t in treasures:
        if distance(x, y, t.x, t.y) < (radius + t.radius + 0.35):
            return False

    return True


def generate_random_obstacles(env, n_obstacles=4, seed=42):
    """
    Génère quelques obstacles circulaires aléatoires, plutôt petits,
    adaptés à la taille de la fenêtre.
    """
    random.seed(seed)

    for _ in range(n_obstacles):
        placed = False

        for _attempt in range(200):
            # obstacles plus petits que les anciens
            rayon = random.uniform(0.28, 0.47)
            x = random.uniform(rayon + 0.3, env.largeur - rayon - 0.3)
            y = random.uniform(rayon + 0.3, env.hauteur - rayon - 0.3)

            # éviter la zone de départ du robot
            if distance(x, y, 2.0, 2.0) < (rayon + 1.0):
                continue

            if point_is_valid_for_circle(env, x, y, rayon):
                env.ajouter_obstacle(ObstacleCirculaire(x=x, y=y, rayon=rayon))
                placed = True
                break

        if not placed:
            print("Attention : un obstacle n'a pas pu être placé.")


def generate_random_treasures(env, robot, n_treasures=10, seed=123):
    """
    Génère 10 trésors aléatoires non collés aux obstacles ni au robot.
    """
    random.seed(seed)

    possible_values = [5, 10, 15, 20]

    for _ in range(n_treasures):
        placed = False

        for _attempt in range(300):
            radius = 0.16
            x = random.uniform(radius + 0.3, env.largeur - radius - 0.3)
            y = random.uniform(radius + 0.3, env.hauteur - radius - 0.3)
            value = random.choice(possible_values)

            if treasure_is_valid(env, x, y, radius, robot, env.treasures):
                env.ajouter_treasure(Treasure(x=x, y=y, radius=radius, value=value))
                placed = True
                break

        if not placed:
            print("Attention : un trésor n'a pas pu être placé.")


def main():
    # Monde : 10 x 7 (unités)
    env = Environnement(largeur=10.0, hauteur=7.0)

    game = GameState(time_limit=200.0)
    env.set_game(game)

    robot = RobotMobile(x=2.0, y=2.0, moteur=MoteurDifferentiel(), rayon=0.2)
    lidar = Lidar(n_rays=36, max_range=3.0)
    robot.add_capteur(lidar)
    env.ajouter_robot(robot)

    # Génération aléatoire
    generate_random_obstacles(env, n_obstacles=8, seed=42)
    generate_random_treasures(env, robot, n_treasures=10, seed=123)

    controleur = ControleurClavierPygame(v_max=2.5, omega_max=2.5)
    vue = VuePygame(largeur_px=900, hauteur_px=650, scale=90)

    mode = "auto"   # "manual" ou "auto"
    autopilot = AutoPilot()

    running = True
    while running:
        dt = vue.tick(fps=60)
        game.step(dt)

        if game.is_time_up:
            running = False
            continue

        # lecture capteurs avant décision
        robot.read_sensors(env)

        if mode == "manual":
            cmd = controleur.lire_commande()
            if cmd is None:
                running = False
                continue
        else:
            cmd = autopilot.compute_command(robot, env, dt)

        robot.commander(**cmd)
        env.mettre_a_jour(dt)

        # lecture après mouvement pour affichage mis à jour
        robot.read_sensors(env)
        vue.dessiner_environnement(env)

    print(
        f"Fin du programme pygame. "
        f"Score final = {game.score} "
        f"| Trésors = {game.treasures_collected}/{len(env.treasures)}"
    )


if __name__ == "__main__":
    main()