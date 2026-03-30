from typing import Optional, List
import math

from robot.robot_mobile import RobotMobile
from robot.obstacles import Obstacle
from robot.game import Treasure, GameState, check_treasure_pickup


class Environnement:
    """
    Monde 2D : largeur x hauteur, avec 1 robot, des obstacles, et des trésors.
    """
    def __init__(self, largeur: float, hauteur: float):
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)

        self.robot: Optional[RobotMobile] = None
        self.obstacles: List[Obstacle] = []

        self.treasures: List[Treasure] = []
        self.game: Optional[GameState] = None

        # --- état de récupération après collision ---
        self.recovery_time_left = 0.0
        self.recovery_turn_sign = 1.0   # +1 gauche / -1 droite

    def ajouter_robot(self, robot: RobotMobile) -> None:
        self.robot = robot

    def ajouter_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def set_game(self, game: GameState) -> None:
        self.game = game

    def ajouter_treasure(self, treasure: Treasure) -> None:
        self.treasures.append(treasure)

    def ramasser_treasures(self) -> int:
        if self.robot is None:
            return 0
        return check_treasure_pickup(self.robot, self.treasures, self.game)

    def collision_murs(self, x: float, y: float, rayon: float) -> bool:
        return (
            x - rayon < 0.0 or x + rayon > self.largeur or
            y - rayon < 0.0 or y + rayon > self.hauteur
        )

    def collision_obstacles(self, x: float, y: float, rayon: float) -> bool:
        return any(obs.collision(x, y, rayon) for obs in self.obstacles)

    def collision(self, x: float, y: float, rayon: float) -> bool:
        return self.collision_murs(x, y, rayon) or self.collision_obstacles(x, y, rayon)

    def is_recovering(self) -> bool:
        return self.recovery_time_left > 0.0

    def update_recovery_timer(self, dt: float) -> None:
        if self.recovery_time_left > 0.0:
            self.recovery_time_left = max(0.0, self.recovery_time_left - float(dt))

    def _choose_escape_side_from_lidar(self) -> float:
        """
        Choisit le sens de rotation après collision.
        On tourne vers le côté où le Lidar voit le plus d'espace.
        """
        if self.robot is None:
            return 1.0

        for capteur in getattr(self.robot, "capteurs", []):
            if capteur.__class__.__name__ == "Lidar":
                distances = getattr(capteur, "distances", [])
                if not distances:
                    return 1.0

                mid = len(distances) // 2
                left = distances[:mid]
                right = distances[mid:]

                left_score = sum(left) / len(left) if left else 0.0
                right_score = sum(right) / len(right) if right else 0.0

                return 1.0 if left_score >= right_score else -1.0

        return 1.0

    def _push_robot_back(self, robot: RobotMobile, backup_distance: float = 0.35) -> None:
        """
        Recul plus fort que la version précédente.
        """
        new_x = robot.x - backup_distance * math.cos(robot.orientation)
        new_y = robot.y - backup_distance * math.sin(robot.orientation)

        if not self.collision(new_x, new_y, robot.rayon):
            robot.x = new_x
            robot.y = new_y

    def mettre_a_jour(self, dt: float) -> None:
        if self.robot is None:
            return

        self.update_recovery_timer(dt)

        old_x, old_y, old_theta = self.robot.x, self.robot.y, self.robot.orientation

        self.robot.mettre_a_jour(float(dt))

        if self.collision(self.robot.x, self.robot.y, self.robot.rayon):
            # rollback
            self.robot.x, self.robot.y, self.robot.orientation = old_x, old_y, old_theta

            # recul plus net
            self._push_robot_back(self.robot, backup_distance=0.35)

            # choisir un vrai côté de fuite
            self.recovery_turn_sign = self._choose_escape_side_from_lidar()

            # déclencher une manœuvre d'évasion pendant un court temps
            self.recovery_time_left = 0.45

            # petite pré-rotation pour lancer le dégagement
            self.robot.orientation += self.recovery_turn_sign * 0.55

            # arrêt momentané moteur
            if self.robot.moteur is not None:
                try:
                    self.robot.commander(v=0.0, omega=0.0)
                except TypeError:
                    self.robot.commander(vx=0.0, vy=0.0, omega=0.0)

            if self.game is not None:
                self.game.collisions += 1

        self.ramasser_treasures()