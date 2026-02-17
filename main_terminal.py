from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurTerminal
from robot.vue import VueTerminalRobot
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire

def main():
    robot = RobotMobile(x=1.0, y=1.0, moteur=MoteurDifferentiel(), rayon=0.2)

    env = Environnement(largeur=10.0, hauteur=7.0)
    env.ajouter_robot(robot)
    env.ajouter_obstacle(ObstacleCirculaire(x=5.0, y=3.5, rayon=1.0))

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

    print("Fin du programme terminal.")

if __name__ == "__main__":
    main()
