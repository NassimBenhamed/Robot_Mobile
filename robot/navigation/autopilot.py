from robot.navigation.selector import select_nearest_treasure
from robot.navigation.go_to_goal import compute_go_to_goal_command
from robot.navigation.reactive import compute_free_space_command


class AutoPilot:
    """
    Pilote autonome simple :
    - choisit le trésor le plus proche
    - suit une direction libre du Lidar
    - si le chemin direct est libre, il va naturellement vers le trésor
    """
    def __init__(self):
        pass

    def compute_command(self, robot, env, dt: float):
        target = select_nearest_treasure(robot, env.treasures)

        if target is None:
            return {"v": 0.0, "omega": 0.0}

        # navigation locale guidée par l'espace libre
        cmd = compute_free_space_command(
            robot,
            target,
            safe_threshold=1.0,
            v_max=1.0,
            omega_max=2.0
        )

        if cmd is not None:
            return cmd

        # fallback
        return compute_go_to_goal_command(robot, target)