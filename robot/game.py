# robot/game.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class Treasure:
    """
    Un trésor à collecter.
    - collected : passe à True quand le robot le ramasse
    """
    x: float
    y: float
    radius: float = 0.15
    value: int = 10
    collected: bool = False

    def distance_to(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)


@dataclass
class GameState:
    """
    État du jeu : timer + score.
    """
    time_limit: float = 60.0
    time_elapsed: float = 0.0
    score: int = 0

    # Stats utiles (bonus pour démo / métriques)
    treasures_collected: int = 0
    collisions: int = 0
    distance_traveled: float = 0.0

    @property
    def time_left(self) -> float:
        return max(0.0, self.time_limit - self.time_elapsed)

    @property
    def is_time_up(self) -> bool:
        return self.time_elapsed >= self.time_limit

    def step(self, dt: float) -> None:
        self.time_elapsed += float(dt)


def check_treasure_pickup(robot, treasures: List[Treasure], game: Optional[GameState] = None) -> int:
    """
    Vérifie si le robot ramasse un/des trésors.
    - robot doit avoir x, y, rayon
    - retourne le nombre de trésors ramassés pendant ce check
    - si game est fourni, on incrémente score + compteur
    """
    picked = 0

    for t in treasures:
        if t.collected:
            continue

        d = t.distance_to(robot.x, robot.y)
        if d <= (robot.rayon + t.radius):
            t.collected = True
            picked += 1

            if game is not None:
                game.score += int(t.value)
                game.treasures_collected += 1

    return picked