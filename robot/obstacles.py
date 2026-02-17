from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


class Obstacle(ABC):
    @abstractmethod
    def collision(self, x: float, y: float, rayon_robot: float) -> bool:
        pass


@dataclass(frozen=True)
class ObstacleCirculaire(Obstacle):
    x: float
    y: float
    rayon: float

    def collision(self, x: float, y: float, rayon_robot: float) -> bool:
        dx = x - self.x
        dy = y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist <= (self.rayon + rayon_robot)