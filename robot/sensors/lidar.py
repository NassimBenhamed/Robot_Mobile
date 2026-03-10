import math
from typing import List, Tuple

from robot.sensors.capteur import Capteur


class Lidar(Capteur):
    """
    Lidar simple 2D par lancer de rayons.
    - n_rays : nombre de rayons
    - max_range : portée maximale en unités monde
    - fov : champ de vision en radians
    """

    def __init__(self, n_rays: int = 36, max_range: float = 3.0, fov: float = 2 * math.pi):
        self.n_rays = int(n_rays)
        self.max_range = float(max_range)
        self.fov = float(fov)

        # Résultats du dernier scan
        self.distances: List[float] = []
        self.hit_points: List[Tuple[float, float]] = []

    def read(self, robot, env):
        """
        Lance n_rays rayons autour du robot.
        Retourne une liste de distances.
        """
        self.distances = []
        self.hit_points = []

        if self.n_rays <= 1:
            angles = [robot.orientation]
        else:
            angle_start = robot.orientation - self.fov / 2.0
            angle_step = self.fov / (self.n_rays - 1)

            angles = [angle_start + i * angle_step for i in range(self.n_rays)]

        for angle in angles:
            distance, hit_x, hit_y = self._cast_single_ray(robot.x, robot.y, angle, env)
            self.distances.append(distance)
            self.hit_points.append((hit_x, hit_y))

        return self.distances

    def _cast_single_ray(self, x0: float, y0: float, angle: float, env):
        """
        Lance un seul rayon.
        Méthode simple : on avance par petits pas jusqu'à collision ou portée max.
        """
        step = 0.03  # précision du lidar
        distance = 0.0

        while distance <= self.max_range:
            x = x0 + distance * math.cos(angle)
            y = y0 + distance * math.sin(angle)

            if env.collision(x, y, 0.0):
                return distance, x, y

            distance += step

        # rien touché : portée max
        x = x0 + self.max_range * math.cos(angle)
        y = y0 + self.max_range * math.sin(angle)
        return self.max_range, x, y