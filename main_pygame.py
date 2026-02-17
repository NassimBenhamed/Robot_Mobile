from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement
from robot.obstacles import ObstacleCirculaire

def main():
    # Monde : 10 x 7 (unités)
    env = Environnement(largeur=10.0, hauteur=7.0)

    robot = RobotMobile(x=2.0, y=2.0, moteur=MoteurDifferentiel(), rayon=0.2)
    env.ajouter_robot(robot)

    # Obstacles
    env.ajouter_obstacle(ObstacleCirculaire(x=5.0, y=3.5, rayon=1.0))
    env.ajouter_obstacle(ObstacleCirculaire(x=8.0, y=5.5, rayon=0.7))

    controleur = ControleurClavierPygame(v_max=2.5, omega_max=2.5)
    vue = VuePygame(largeur_px=900, hauteur_px=650, scale=90)

    running = True
    while running:
        dt = vue.tick(fps=60)

        cmd = controleur.lire_commande()
        if cmd is None:
            running = False
            continue

        robot.commander(**cmd)
        env.mettre_a_jour(dt)
        vue.dessiner_environnement(env)

    print("Fin du programme pygame.")

if __name__ == "__main__":
    main()
