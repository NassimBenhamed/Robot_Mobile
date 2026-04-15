import math
import pygame
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
from robot.wave_csv import WaveCSVLogger


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


def obstacle_valid_for_house(house, x, y, radius, min_gap=0.80):
    half = house.size / 2.0

    x_min = house.x - half - min_gap - radius
    x_max = house.x + half + min_gap + radius
    y_min = house.y - half - min_gap - radius
    y_max = house.y + half + min_gap + radius

    return not (x_min <= x <= x_max and y_min <= y <= y_max)


def treasure_is_valid(env, x, y, radius, robot, treasures, house):
    if x - radius < 0.0 or x + radius > env.largeur:
        return False
    if y - radius < 0.0 or y + radius > env.hauteur:
        return False

    if distance(x, y, robot.x, robot.y) < (radius + robot.rayon + 0.80):
        return False

    half = house.size / 2.0
    if (
        house.x - half - radius - 0.40 <= x <= house.x + half + radius + 0.40 and
        house.y - half - radius - 0.40 <= y <= house.y + half + radius + 0.40
    ):
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


def generate_house_exit_obstacle(env, house, wave_index):
    if wave_index < 3:
        return

    probability = min(0.25 + 0.08 * (wave_index - 3), 0.65)
    if random.random() > probability:
        return

    for _ in range(120):
        rayon = random.uniform(0.24, min(0.34 + 0.01 * wave_index, 0.42))

        half = house.size / 2.0
        x = house.x + random.uniform(half + 0.8, half + 1.8)
        y = house.y + random.uniform(-0.9, 0.9)

        if x - rayon < 0.0 or x + rayon > env.largeur:
            continue
        if y - rayon < 0.0 or y + rayon > env.hauteur:
            continue

        if not obstacle_valid_for_house(house, x, y, rayon, min_gap=0.35):
            continue

        if point_is_valid_for_circle(env, x, y, rayon, extra_margin=0.10):
            env.ajouter_obstacle(ObstacleCirculaire(x=x, y=y, rayon=rayon))
            return


def generate_wave_obstacles(env, house, wave_index, n_obstacles=None):
    if n_obstacles is None:
        n_obstacles = min(3 + (wave_index - 1), 7)

    generate_house_exit_obstacle(env, house, wave_index)

    for _ in range(n_obstacles):
        placed = False

        for _attempt in range(300):
            r_min = min(0.24 + 0.015 * (wave_index - 1), 0.34)
            r_max = min(0.42 + 0.020 * (wave_index - 1), 0.62)

            rayon = random.uniform(r_min, r_max)
            x = random.uniform(rayon + 0.3, env.largeur - rayon - 0.3)
            y = random.uniform(rayon + 0.3, env.hauteur - rayon - 0.3)

            if not obstacle_valid_for_house(house, x, y, rayon, min_gap=0.80):
                continue

            if point_is_valid_for_circle(env, x, y, rayon):
                env.ajouter_obstacle(ObstacleCirculaire(x=x, y=y, rayon=rayon))
                placed = True
                break

        if not placed:
            print("Attention : un obstacle n'a pas pu être placé.")


def generate_wave_treasures(env, robot, house, wave_index, n_treasures=10):
    possible_values = [5, 10, 15, 20]
    min_dist_from_house = min(1.6 + 0.32 * (wave_index - 1), 3.6)

    for _ in range(n_treasures):
        placed = False

        for _attempt in range(600):
            radius = 0.16

            if wave_index >= 4 and random.random() < 0.55:
                x = random.uniform(env.largeur * 0.45, env.largeur - radius - 0.3)
                y = random.uniform(env.hauteur * 0.30, env.hauteur - radius - 0.3)
            else:
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

    if isinstance(robot.moteur, MoteurDifferentiel):
        robot.moteur.set_wave_level(wave_index)

    game.prepare_wave(wave_index)

    generate_wave_obstacles(env, game.house, wave_index)
    generate_wave_treasures(env, robot, game.house, wave_index, n_treasures=10)


def start_csv_for_wave(wave_logger, current_wave, house, env, robot):
    wave_logger.start_wave(
        wave_index=current_wave,
        start_x=house.x,
        start_y=house.y,
        treasures=env.treasures,
        obstacles=env.obstacles,
        robot_radius=robot.rayon,
    )


def draw_environment_safe(vue, env, paused=False, mode="auto"):
    try:
        vue.dessiner_environnement(env, paused=paused, mode=mode)
    except TypeError:
        vue.dessiner_environnement(env, paused=paused)


def ask_mode(max_attempts=3) -> str:
    """
    Demande le mode de jeu : IA ou joueur.
    """
    for _ in range(max_attempts):
        choice = input("Choisir le mode (IA / joueur) : ").strip().lower()
        if choice in ("ia", "1", "auto"):
            return "auto"
        if choice in ("joueur", "player", "2", "manuel", "manual"):
            return "manual"
        print("Entrée invalide. Réponds par IA ou joueur.")
    print("Mode invalide trop de fois. Passage en mode IA par défaut.")
    return "auto"


def ask_initial_time(max_attempts=3) -> int:
    """
    Demande le temps de départ en secondes, entre 20 et 60.
    Si l'utilisateur échoue 3 fois, on prend 45 secondes par défaut.
    """
    for _ in range(max_attempts):
        raw = input("Temps initial par vague en secondes (entre 20 et 60) : ").strip()
        try:
            value = int(raw)
            if 20 <= value <= 60:
                return value
        except ValueError:
            pass
        print("Valeur invalide. Entre un entier entre 20 et 60.")
    print("Trop d'erreurs. Temps par défaut appliqué : 45 secondes.")
    return 45


def ask_yes_no(question: str, default: bool = False, max_attempts: int = 3) -> bool:
    """
    Question oui/non.
    """
    for _ in range(max_attempts):
        raw = input(f"{question} (oui/non) : ").strip().lower()
        if raw in ("oui", "o", "y", "yes", "1"):
            return True
        if raw in ("non", "n", "no", "0"):
            return False
        print("Réponse invalide. Réponds par oui ou non.")
    return default


def run_end_screen(vue: VuePygame, score: int, wave: int):
    """
    Affiche un petit écran de fin jusqu'à fermeture.
    """
    waiting = True
    while waiting:
        vue.draw_end_screen(score=score, wave=wave)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        vue.tick(fps=30)


def main():
    import pygame

    mode = ask_mode()
    initial_time = ask_initial_time()

    show_sensors = True
    show_paths = True

    if mode == "auto":
        show_sensors = ask_yes_no("Afficher les capteurs", default=True)
        show_paths = ask_yes_no("Afficher les chemins", default=True)

    env = Environnement(largeur=10.0, hauteur=7.0)

    house = House(x=1.2, y=1.2, size=1.30)
    game = GameState()
    game.house = house
    game.base_time_limit = float(initial_time)
    game.min_time_limit = 15.0
    env.set_game(game)

    robot = RobotMobile(
        x=house.x,
        y=house.y,
        moteur=MoteurDifferentiel(),
        rayon=0.2
    )

    lidar = Lidar(n_rays=36, max_range=4.0)
    robot.add_capteur(lidar)
    env.ajouter_robot(robot)

    controleur = ControleurClavierPygame(v_max=2.5, omega_max=2.5)
    vue = VuePygame(
        largeur_px=900,
        hauteur_px=650,
        scale=90,
        show_sensors=show_sensors,
        show_paths=show_paths,
    )

    paused = False
    autopilot = AutoPilot()
    wave_logger = WaveCSVLogger(filepath="wave_report.csv", speed_estimate=1.10)

    current_wave = 1
    random.seed()

    setup_wave(env, robot, game, current_wave)
    start_csv_for_wave(wave_logger, current_wave, house, env, robot)

    running = True
    while running:
        event_action = vue.gerer_evenements()

        if isinstance(event_action, bool):
            if not event_action:
                game.game_over = True
                break
            event_action = "none"

        if event_action == "quit":
            game.game_over = True
            break

        if event_action == "pause_toggle":
            paused = not paused

        dt = vue.tick(fps=60)

        if paused:
            draw_environment_safe(vue, env, paused=True, mode=mode)
            continue

        if not game.robot_in_house(robot):
            game.left_house_once = True

        game.step(dt)

        if game.robot_in_house(robot) and game.left_house_once:
            wave_logger.flush_wave()
            current_wave += 1
            setup_wave(env, robot, game, current_wave)
            start_csv_for_wave(wave_logger, current_wave, house, env, robot)
            continue

        if game.is_time_up:
            if game.robot_in_house(robot):
                wave_logger.flush_wave()
                current_wave += 1
                setup_wave(env, robot, game, current_wave)
                start_csv_for_wave(wave_logger, current_wave, house, env, robot)
                continue
            else:
                game.game_over = True
                break

        robot.read_sensors(env)

        if mode == "manual":
            cmd = controleur.lire_commande()
            if cmd is None:
                game.game_over = True
                break
        else:
            cmd = autopilot.compute_command(robot, env, dt)

        robot.commander(**cmd)
        env.mettre_a_jour(dt)

        robot.read_sensors(env)

        for treasure in env.treasures:
            if treasure.collected:
                wave_logger.mark_collected(treasure, game.time_elapsed)

        draw_environment_safe(vue, env, paused=False, mode=mode)

    wave_logger.flush_wave()
    run_end_screen(vue, score=game.total_score, wave=game.wave_index)

    print(
        f"Fin de partie | Vague atteinte = {game.wave_index} "
        f"| Score total = {game.total_score} "
        f"| Trésors ramassés = {game.treasures_collected_total}"
    )


if __name__ == "__main__":
    main()