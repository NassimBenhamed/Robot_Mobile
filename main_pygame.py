from robot import game
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire
from robot.game import Treasure, GameState
from robot.sensors import Lidar

def main():
    # Monde : 10 x 7 (unités)
    env = Environnement(largeur=10.0, hauteur=7.0)
    
    game = GameState(time_limit=60.0)
    env.set_game(game)

    robot = RobotMobile(x=2.0, y=2.0, moteur=MoteurDifferentiel(), rayon=0.2)
    lidar = Lidar(n_rays=36, max_range=3.0)
    robot.add_capteur(lidar)
    env.ajouter_robot(robot)

    # Obstacles
    env.ajouter_obstacle(ObstacleCirculaire(x=5.0, y=3.5, rayon=1.0))
    env.ajouter_obstacle(ObstacleCirculaire(x=8.0, y=5.5, rayon=0.7))
    
    env.ajouter_treasure(Treasure(x=3.0, y=1.5, radius=0.18, value=10))
    env.ajouter_treasure(Treasure(x=7.5, y=5.8, radius=0.18, value=20))
    env.ajouter_treasure(Treasure(x=8.2, y=1.2, radius=0.18, value=15))

    controleur = ControleurClavierPygame(v_max=2.5, omega_max=2.5)
    vue = VuePygame(largeur_px=900, hauteur_px=650, scale=90)

    running = True
    while running:
        dt = vue.tick(fps=60)
        game.step(dt)
        if game.is_time_up:
            running = False
            continue

        cmd = controleur.lire_commande()
        if cmd is None:
            running = False
            continue

        robot.commander(**cmd)
        env.mettre_a_jour(dt)
        robot.read_sensors(env)
        vue.dessiner_environnement(env)

    print(f"Fin du programme pygame. Score final = {game.score} | Trésors = {game.treasures_collected}/{len(env.treasures)}")

if __name__ == "__main__":
    main()
