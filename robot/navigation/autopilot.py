from dataclasses import dataclass

from robot.navigation.selector import (
    select_feasible_treasure,
    select_best_open_treasure,
    corridor_clearance_to_point,
)
from robot.navigation.reactive import analyze_sectors, go_toward


@dataclass
class TargetPoint:
    x: float
    y: float


class AutoPilot:
    def __init__(self):
        self.current_mode = "treasure"   # "treasure", "home", "escape"
        self.escape_side = "left"
        self.escape_time = 0.0

    def _update_timer(self, dt: float):
        if self.escape_time > 0.0:
            self.escape_time = max(0.0, self.escape_time - float(dt))

    def _home_target(self, game):
        return TargetPoint(game.house.x, game.house.y)

    def _near_border(self, robot, env, margin: float = 0.45) -> bool:
        return (
            robot.x <= margin or
            robot.x >= env.largeur - margin or
            robot.y <= margin or
            robot.y >= env.hauteur - margin
        )

    def _border_escape_target(self, env):
        return TargetPoint(env.largeur / 2.0, env.hauteur / 2.0)

    def _choose_escape_side(self, info):
        return "left" if info["left_mean"] >= info["right_mean"] else "right"

    def _choose_target(self, robot, env):
        game = env.game

        if game is None or game.house is None:
            return None, "idle"

        if self._near_border(robot, env, margin=0.45):
            return self._border_escape_target(env), "escape"

        if game.should_return_home(robot, safety_margin=4.0, speed_estimate=0.75):
            return self._home_target(game), "home"

        # priorité à un trésor faisable ET avec un couloir ouvert
        open_target = select_best_open_treasure(
            robot,
            env.treasures,
            game,
            k_angle=0.7,
            safety_margin=4.0,
            min_clearance=0.95,
        )
        if open_target is not None:
            return open_target, "treasure"

        # fallback : trésor faisable même si le couloir est moins bon
        fallback = select_feasible_treasure(
            robot,
            env.treasures,
            game,
            k_angle=0.7,
            safety_margin=4.0,
        )
        if fallback is not None:
            return fallback, "treasure"

        return self._home_target(game), "home"

    def compute_command(self, robot, env, dt: float):
        self._update_timer(dt)

        game = env.game
        if game is None:
            return {"v": 0.0, "omega": 0.0}

        target, desired_mode = self._choose_target(robot, env)
        if target is None:
            return {"v": 0.0, "omega": 0.0}

        info = analyze_sectors(robot, target)
        if info is None:
            return {"v": 0.0, "omega": 0.0}

        target_angle = info["target_angle"]
        front_mean = info["front_mean"]
        left_mean = info["left_mean"]
        right_mean = info["right_mean"]

        # qualité réelle du couloir vers la cible choisie
        target_clearance = corridor_clearance_to_point(robot, target.x, target.y, neighbor_span=1)

        # collision au tick précédent -> petit escape
        if getattr(env, "just_collided", False):
            self.current_mode = "escape"
            self.escape_side = self._choose_escape_side(info)
            self.escape_time = 0.40
            env.just_collided = False

        # proche du bord -> on recentre
        if desired_mode == "escape":
            self.current_mode = "escape"

        # mode escape : rotation seulement
        if self.current_mode == "escape":
            if self.escape_time > 0.0:
                return {
                    "v": 0.0,
                    "omega": 2.6 if self.escape_side == "left" else -2.6
                }

            # si on s'est dégagé, on revient à la logique normale au tick suivant
            self.current_mode = "home" if desired_mode == "escape" else desired_mode

            side = "left" if left_mean >= right_mean else "right"
            return {
                "v": 0.0,
                "omega": 2.4 if side == "left" else -2.4
            }

        # --- Comportement normal ---

        # Si la cible actuelle est un trésor mais que le couloir est nul,
        # on refuse de s'acharner dessus.
        if desired_mode == "treasure" and target_clearance < 0.80:
            alt_target = select_best_open_treasure(
                robot,
                env.treasures,
                game,
                k_angle=0.7,
                safety_margin=4.0,
                min_clearance=0.95,
            )

            if alt_target is not None and (alt_target.x != target.x or alt_target.y != target.y):
                target = alt_target
                info = analyze_sectors(robot, target)
                if info is not None:
                    target_angle = info["target_angle"]
                    front_mean = info["front_mean"]
                    left_mean = info["left_mean"]
                    right_mean = info["right_mean"]
                    target_clearance = corridor_clearance_to_point(robot, target.x, target.y, neighbor_span=1)
            else:
                # S'il n'y a pas de bon trésor ouvert, on tourne et on scanne,
                # au lieu de rester obsédé par cette cible.
                side = "left" if left_mean >= right_mean else "right"
                return {
                    "v": 0.0,
                    "omega": 2.5 if side == "left" else -2.5
                }

        # Si le chemin est vraiment bon, on avance
        if front_mean > 0.95 and target_clearance > 0.90:
            if desired_mode == "home":
                return go_toward(robot, target_angle, v_max=0.82, omega_max=2.0)
            return go_toward(robot, target_angle, v_max=0.92, omega_max=2.2)

        # Si le chemin est moyen, on avance lentement
        if front_mean > 0.75 and target_clearance > 0.75:
            if desired_mode == "home":
                return go_toward(robot, target_angle, v_max=0.55, omega_max=1.9)
            return go_toward(robot, target_angle, v_max=0.60, omega_max=2.0)

        # Sinon : on arrête d'avancer et on tourne vers le côté le plus libre
        side = "left" if left_mean >= right_mean else "right"
        return {
            "v": 0.0,
            "omega": 2.4 if side == "left" else -2.4
        }