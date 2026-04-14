import math
import random

from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire
from robot.game import Treasure, GameState, House
from robot.sensors import Lidar
from robot.navigation import AutoPilot


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def point_is_valid_for_circle(env, x, y, radius, extra_margin=0.20):
    if x - radius < 0.0 or x + radius > env.largeur:
        return False
    if y - radius < 0.0 or y + radius > env.hauteur:
        return False

    for obs in env.obstacles:
        if distance(x, y, obs.x, obs.y) < (radius + obs.rayon + extra_margin):
            return False

    return True


def obstacle_valid_for_house(house, x, y, radius):
    return distance(x, y, house.x, house.y) >= (radius + house.radius + 0.80)


def treasure_is_valid(env, x, y, radius, robot, treasures, house):
    if x - radius < 0.0 or x + radius > env.largeur:
        return False
    if y - radius < 0.0 or y + radius > env.hauteur:
        return False

    if distance(x, y, robot.x, robot.y) < (radius + robot.rayon + 0.80):
        return False

    if distance(x, y, house.x, house.y) < (radius + house.radius + 0.40):
        return False

    for obs in env.obstacles:
        if distance(x, y, obs.x, obs.y) < (radius + obs.rayon + 0.35):
            return False

    for t in treasures:
        if distance(x, y, t.x, t.y) < (radius + t.radius + 0.30):
            return False

    return True


def clear_wave_objects(env):
    env.obstacles = []
    env.treasures = []


def generate_wave_obstacles(env, house, wave_index, n_obstacles=None):
    """
    Difficulté croissante :
    - le nombre d'obstacles augmente avec la vague
    - leur taille moyenne augmente légèrement
    """
    if n_obstacles is None:
        n_obstacles = min(5 + (wave_index - 1), 10)

    for _ in range(n_obstacles):
        placed = False

        for _attempt in range(300):
            r_min = min(0.24 + 0.015 * (wave_index - 1), 0.34)
            r_max = min(0.42 + 0.020 * (wave_index - 1), 0.62)

            rayon = random.uniform(r_min, r_max)
            x = random.uniform(rayon + 0.3, env.largeur - rayon - 0.3)
            y = random.uniform(rayon + 0.3, env.hauteur - rayon - 0.3)

            if not obstacle_valid_for_house(house, x, y, rayon):
                continue

            if point_is_valid_for_circle(env, x, y, rayon):
                env.ajouter_obstacle(ObstacleCirculaire(x=x, y=y, rayon=rayon))
                placed = True
                break

        if not placed:
            print("Attention : un obstacle n'a pas pu être placé.")


def generate_wave_treasures(env, robot, house, wave_index, n_treasures=10):
    """
    Difficulté croissante :
    - les trésors sont de plus en plus loin de la maison
    """
    possible_values = [5, 10, 15, 20]

    min_dist_from_house = min(1.5 + 0.28 * (wave_index - 1), 3.2)

    for _ in range(n_treasures):
        placed = False

        for _attempt in range(500):
            radius = 0.16
            x = random.uniform(radius + 0.3, env.largeur - radius - 0.3)
            y = random.uniform(radius + 0.3, env.hauteur - radius - 0.3)

            if distance(x, y, house.x, house.y) < min_dist_from_house:
                continue

            value = random.choice(possible_values)

            if treasure_is_valid(env, x, y, radius, robot, env.treasures, house):
                env.ajouter_treasure(Treasure(x=x, y=y, radius=radius, value=value))
                placed = True
                break

        if not placed:
            print("Attention : un trésor n'a pas pu être placé.")


def setup_wave(env, robot, game, wave_index):
    clear_wave_objects(env)

    robot.x = game.house.x
    robot.y = game.house.y
    robot.orientation = 0.0

    game.prepare_wave(wave_index)

    generate_wave_obstacles(env, game.house, wave_index)
    generate_wave_treasures(env, robot, game.house, wave_index, n_treasures=10)


def main():
    env = Environnement(largeur=10.0, hauteur=7.0)

    house = House(x=1.2, y=1.2, radius=0.55)
    game = GameState()
    game.house = house
    env.set_game(game)

    robot = RobotMobile(x=house.x, y=house.y, moteur=MoteurDifferentiel(), rayon=0.2)
    lidar = Lidar(n_rays=36, max_range=4.0)
    robot.add_capteur(lidar)
    env.ajouter_robot(robot)

    controleur = ControleurClavierPygame(v_max=2.5, omega_max=2.5)
    vue = VuePygame(largeur_px=900, hauteur_px=650, scale=90)

    mode = "auto"
    autopilot = AutoPilot()

    current_wave = 1
    random.seed()
    setup_wave(env, robot, game, current_wave)

    running = True
    while running:
        if not vue.gerer_evenements():
            game.game_over = True
            running = False
            continue

        dt = vue.tick(fps=60)
        game.step(dt)

        # Fin de vague : le robot est revenu à la maison
        if game.robot_in_house(robot) and game.treasures_collected_wave > 0:
            current_wave += 1
            setup_wave(env, robot, game, current_wave)
            continue

        # Fin de partie : temps écoulé hors maison
        if game.is_time_up:
            if game.robot_in_house(robot):
                current_wave += 1
                setup_wave(env, robot, game, current_wave)
                continue
            else:
                game.game_over = True
                running = False
                continue

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

        robot.read_sensors(env)
        vue.dessiner_environnement(env)

    print(
        f"Fin de partie | Vague atteinte = {game.wave_index} "
        f"| Score total = {game.total_score} "
        f"| Trésors ramassés = {game.treasures_collected_total}"
    )


if __name__ == "__main__":
    main()