from dataclasses import dataclass

from robot.navigation.selector import (
    select_feasible_treasure,
    select_first_mandatory_treasure,
)
from robot.navigation.go_to_goal import compute_go_to_goal_command
from robot.navigation.path_utils import (
    Point2D,
    line_of_sight_clear,
    choose_best_detour,
    distance,
)


@dataclass
class TargetPoint:
    x: float
    y: float


class AutoPilot:
    def __init__(self):
        self.current_mode = "treasure"   # "treasure" ou "home"
        self.active_waypoint = None
        self.last_target_kind = None

    def _home_target(self, game):
        return TargetPoint(game.house.x, game.house.y)

    def _choose_main_target(self, robot, env):
        game = env.game

        if game is None or game.house is None:
            return None, "idle"

        # Tant qu'aucun trésor n'a encore été ramassé dans la vague,
        # on force au moins une tentative de collecte.
        if game.treasures_collected_wave == 0:
            first_target = select_first_mandatory_treasure(robot, env.treasures)
            if first_target is not None:
                return first_target, "treasure"

        # Ensuite seulement, on applique la logique normale de retour
        if game.should_return_home(robot, safety_margin=4.0, speed_estimate=0.90):
            return self._home_target(game), "home"

        treasure = select_feasible_treasure(
            robot,
            env.treasures,
            game,
            k_angle=0.7,
            safety_margin=4.0,
        )

        if treasure is not None:
            return treasure, "treasure"

        return self._home_target(game), "home"

    def _target_reached(self, robot, target, threshold: float = 0.22) -> bool:
        return distance(robot.x, robot.y, target.x, target.y) < threshold

    def compute_command(self, robot, env, dt: float):
        game = env.game
        if game is None:
            return {"v": 0.0, "omega": 0.0}

        # reset debug visuel
        env.debug_target = None
        env.debug_path = []
        env.debug_direct_line = None

        main_target, target_kind = self._choose_main_target(robot, env)
        if main_target is None:
            return {"v": 0.0, "omega": 0.0}

        self.current_mode = target_kind
        self.last_target_kind = target_kind
        env.debug_target = Point2D(main_target.x, main_target.y)

        # Si on avait déjà un waypoint, on le conserve jusqu'à l'atteindre
        if self.active_waypoint is not None:
            if self._target_reached(robot, self.active_waypoint, threshold=0.25):
                self.active_waypoint = None

        # Si le chemin direct vers la cible est libre, pas besoin de waypoint
        direct_clear = line_of_sight_clear(robot, main_target, env, margin=0.12)
        env.debug_direct_line = (robot.x, robot.y, main_target.x, main_target.y, direct_clear)

        if direct_clear:
            self.active_waypoint = None
            env.debug_path = [(robot.x, robot.y), (main_target.x, main_target.y)]

            if target_kind == "home":
                return compute_go_to_goal_command(robot, main_target, v_max=1.10, omega_max=2.4)
            return compute_go_to_goal_command(robot, main_target, v_max=1.35, omega_max=2.6)

        # Sinon on essaie de contourner avec un waypoint géométrique
        if self.active_waypoint is None:
            waypoint = choose_best_detour(robot, main_target, env)
            self.active_waypoint = waypoint

        if self.active_waypoint is not None:
            env.debug_path = [
                (robot.x, robot.y),
                (self.active_waypoint.x, self.active_waypoint.y),
                (main_target.x, main_target.y),
            ]
            return compute_go_to_goal_command(robot, self.active_waypoint, v_max=1.10, omega_max=2.5)

        # Fallback minimal si aucun waypoint n'est trouvable
        # On tourne pour changer la configuration, sans utiliser de réactif comme cerveau.
        env.debug_path = [(robot.x, robot.y), (main_target.x, main_target.y)]
        return {"v": 0.0, "omega": 1.8}