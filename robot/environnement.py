from typing import Optional, List

from robot.robot_mobile import RobotMobile
from robot.obstacles import Obstacle


class Environnement:
    """
    Monde 2D : largeur x hauteur, avec 1 robot et des obstacles.
    Les unités sont libres (mètres, cases, etc).
    """
    def __init__(self, largeur: float, hauteur: float):
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)
        self.robot: Optional[RobotMobile] = None
        self.obstacles: List[Obstacle] = []

    def ajouter_robot(self, robot: RobotMobile) -> None:
        self.robot = robot

    def ajouter_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def collision_murs(self, x: float, y: float, rayon: float) -> bool:
        return (
            x - rayon < 0.0 or x + rayon > self.largeur or
            y - rayon < 0.0 or y + rayon > self.hauteur
        )

    def collision_obstacles(self, x: float, y: float, rayon: float) -> bool:
        return any(obs.collision(x, y, rayon) for obs in self.obstacles)

    def collision(self, x: float, y: float, rayon: float) -> bool:
        return self.collision_murs(x, y, rayon) or self.collision_obstacles(x, y, rayon)

    def mettre_a_jour(self, dt: float) -> None:
        if self.robot is None:
            return

        # sauvegarde
        old_x, old_y, old_theta = self.robot.x, self.robot.y, self.robot.orientation

        # update du modèle (via moteur)
        self.robot.mettre_a_jour(dt)

        # collision -> on annule le mouvement
        if self.collision(self.robot.x, self.robot.y, self.robot.rayon):
            self.robot.x, self.robot.y, self.robot.orientation = old_x, old_y, old_theta

            # Option simple : stopper le robot si collision
            if self.robot.moteur is not None:
                # Pour différentiel : v=0 omega=0 ; pour omni : vx=0 vy=0 omega=0
                try:
                    self.robot.commander(v=0.0, omega=0.0)
                except TypeError:
                    self.robot.commander(vx=0.0, vy=0.0, omega=0.0)
