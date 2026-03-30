from robot.navigation.selector import select_nearest_treasure
from robot.navigation.go_to_goal import compute_go_to_goal_command
from robot.navigation.reactive import (
    compute_free_space_command,
    get_lidar,
    build_ray_angles,
    normalize_angle,
)


class AutoPilot:
    """
    Pilote autonome :
    - choisit le trésor le plus proche
    - utilise le Lidar pour trouver un groupe de directions libres
    - garde temporairement le même couloir pour éviter les hésitations
    """
    def __init__(self):
        self.locked_ray_index = None
        self.lock_time_left = 0.0

    def _update_lock_timer(self, dt: float):
        if self.lock_time_left > 0.0:
            self.lock_time_left = max(0.0, self.lock_time_left - float(dt))
            if self.lock_time_left == 0.0:
                self.locked_ray_index = None

    def compute_command(self, robot, env, dt: float):
        self._update_lock_timer(dt)

        target = select_nearest_treasure(robot, env.treasures)
        if target is None:
            return {"v": 0.0, "omega": 0.0}

        lidar = get_lidar(robot)

        # Si on a déjà un couloir verrouillé et que le Lidar existe encore,
        # on continue dessus un court instant
        if (
            self.locked_ray_index is not None
            and self.lock_time_left > 0.0
            and lidar is not None
            and getattr(lidar, "distances", None)
        ):
            distances = lidar.distances
            n = len(distances)

            if 0 <= self.locked_ray_index < n:
                ray_angles = build_ray_angles(robot, lidar, n)
                chosen_angle = ray_angles[self.locked_ray_index]
                angle_error = normalize_angle(chosen_angle - robot.orientation)

                if abs(angle_error) > 0.30:
                    return {
                        "v": 0.14,
                        "omega": 2.5 if angle_error > 0 else -2.5
                    }

        cmd, chosen_center_i = compute_free_space_command(
            robot,
            target,
            safe_threshold=1.15,
            blocked_threshold=0.90,
            v_max=0.95,
            omega_max=2.5
        )

        if cmd is not None:
            if chosen_center_i is not None:
                self.locked_ray_index = chosen_center_i
                self.lock_time_left = 0.35
            return cmd

        return compute_go_to_goal_command(robot, target)