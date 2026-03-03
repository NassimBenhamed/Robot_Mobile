from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurTerminal
from robot.vue import VueTerminalRobot
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire
from robot.game import Treasure, GameState

def main():
    robot = RobotMobile(x=2.9, y=1.0, moteur=MoteurDifferentiel(), rayon=0.2)

    env = Environnement(largeur=10.0, hauteur=7.0)
    env.ajouter_robot(robot)
    env.ajouter_obstacle(ObstacleCirculaire(x=5.0, y=3.5, rayon=1.0))
    
    game = GameState(time_limit=60.0)
    env.set_game(game)

    env.ajouter_treasure(Treasure(x=3.0, y=1.0, radius=0.2, value=10))
    env.ajouter_treasure(Treasure(x=7.0, y=6.0, radius=0.2, value=20))

    controleur = ControleurTerminal()
    vue_robot = VueTerminalRobot()

    dt = 1.0
    running = True

    while running:
        vue_robot.dessiner_robot(robot)

        cmd = controleur.lire_commande()
        if cmd is None:
            running = False
            continue

        if cmd:
            robot.commander(**cmd)

        env.mettre_a_jour(dt)
    
    print(f"Score={game.score} | Trésors={game.treasures_collected}/{len(env.treasures)}")

    print("Fin du programme terminal.")

if __name__ == "__main__":
    main()
