from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import math


@dataclass
class Treasure:
    x: float
    y: float
    radius: float = 0.15
    value: int = 10
    collected: bool = False

    def distance_to(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)


@dataclass
class House:
    """
    Maison carrée.

    x et y représentent le centre du carré.
    size représente la longueur du côté.
    """
    x: float
    y: float
    size: float = 1.10

    def contains(self, x: float, y: float, robot_radius: float = 0.0) -> bool:
        """
        Retourne True uniquement si le robot est complètement à l'intérieur du carré.
        """
        half = self.size / 2.0
        return (
            x - robot_radius >= self.x - half and
            x + robot_radius <= self.x + half and
            y - robot_radius >= self.y - half and
            y + robot_radius <= self.y + half
        )


@dataclass
class GameState:
    """
    Gestion du jeu par vagues.
    """
    wave_index: int = 1
    wave_time_limit: float = 45.0
    time_elapsed: float = 0.0

    total_score: int = 0
    wave_score: int = 0

    treasures_collected_total: int = 0
    treasures_collected_wave: int = 0

    collisions: int = 0
    distance_traveled: float = 0.0

    game_over: bool = False
    wave_completed: bool = False
    left_house_once: bool = False

    # Temps de base choisi par l'utilisateur
    base_time_limit: float = 45.0
    min_time_limit: float = 25.0

    house: Optional[House] = None

    @property
    def time_left(self) -> float:
        return max(0.0, self.wave_time_limit - self.time_elapsed)

    @property
    def score(self) -> int:
        return self.total_score

    @property
    def treasures_collected(self) -> int:
        return self.treasures_collected_total

    @property
    def is_time_up(self) -> bool:
        return self.time_elapsed >= self.wave_time_limit

    def step(self, dt: float) -> None:
        self.time_elapsed += float(dt)

    def reset_for_new_wave(self) -> None:
        self.time_elapsed = 0.0
        self.wave_score = 0
        self.treasures_collected_wave = 0
        self.wave_completed = False
        self.left_house_once = False

    def next_wave_time_limit(self) -> float:
        """
        Le temps baisse de 5 secondes par vague jusqu'à la borne minimale.
        """
        return max(self.base_time_limit - 5.0 * (self.wave_index - 1), self.min_time_limit)

    def prepare_wave(self, wave_index: int) -> None:
        self.wave_index = wave_index
        self.wave_time_limit = max(
            self.base_time_limit - 5.0 * (wave_index - 1),
            self.min_time_limit
        )
        self.reset_for_new_wave()

    def robot_in_house(self, robot) -> bool:
        if self.house is None:
            return False
        return self.house.contains(robot.x, robot.y, getattr(robot, "rayon", 0.0))

    def should_return_home(
        self,
        robot,
        safety_margin: float = 4.0,
        speed_estimate: float = 0.75
    ) -> bool:
        """
        Décide s'il faut rentrer maintenant.
        """
        if self.house is None:
            return False

        dist_home = math.hypot(self.house.x - robot.x, self.house.y - robot.y)
        estimated_return_time = dist_home / max(speed_estimate, 1e-6)

        return estimated_return_time + safety_margin >= self.time_left


def check_treasure_pickup(
    robot,
    treasures: List[Treasure],
    game: Optional[GameState] = None
) -> int:
    picked = 0

    for t in treasures:
        if t.collected:
            continue

        d = t.distance_to(robot.x, robot.y)
        if d <= (robot.rayon + t.radius):
            t.collected = True
            picked += 1

            if game is not None:
                game.total_score += int(t.value)
                game.wave_score += int(t.value)
                game.treasures_collected_total += 1
                game.treasures_collected_wave += 1

    return picked