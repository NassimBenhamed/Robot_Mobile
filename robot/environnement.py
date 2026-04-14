from typing import Optional, List

from robot.robot_mobile import RobotMobile
from robot.obstacles import Obstacle
from robot.game import Treasure, GameState, check_treasure_pickup


class Environnement:
    def __init__(self, largeur: float, hauteur: float):
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)

        self.robot: Optional[RobotMobile] = None
        self.obstacles: List[Obstacle] = []

        self.treasures: List[Treasure] = []
        self.game: Optional[GameState] = None

        self.just_collided = False

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

    def mettre_a_jour(self, dt: float) -> None:
        if self.robot is None:
            return

        self.just_collided = False

        old_x, old_y, old_theta = self.robot.x, self.robot.y, self.robot.orientation
        self.robot.mettre_a_jour(float(dt))

        if self.collision(self.robot.x, self.robot.y, self.robot.rayon):
            self.robot.x = old_x
            self.robot.y = old_y
            self.robot.orientation = old_theta
            self.just_collided = True

            if self.game is not None:
                self.game.collisions += 1

        self.ramasser_treasures()