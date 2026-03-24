import math


def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def get_lidar(robot):
    for capteur in getattr(robot, "capteurs", []):
        if capteur.__class__.__name__ == "Lidar":
            return capteur
    return None


def compute_free_space_command(
    robot,
    target,
    safe_threshold: float = 1.0,
    v_max: float = 1.0,
    omega_max: float = 2.0
):
    """
    Choisit une direction libre à partir du Lidar.
    Parmi les rayons "sûrs", on prend celui qui est le plus proche
    de la direction du trésor.
    """
    lidar = get_lidar(robot)
    if lidar is None or not lidar.distances:
        return None

    n = len(lidar.distances)
    if n == 0:
        return None

    # angle du trésor par rapport au monde
    dx = target.x - robot.x
    dy = target.y - robot.y
    target_angle = math.atan2(dy, dx)

    # reconstruire les angles des rayons
    if n == 1:
        ray_angles = [robot.orientation]
    else:
        angle_start = robot.orientation - lidar.fov / 2.0
        angle_step = lidar.fov / (n - 1)
        ray_angles = [angle_start + i * angle_step for i in range(n)]

    # On garde seulement les rayons assez libres
    candidate_indices = [
        i for i, d in enumerate(lidar.distances)
        if d >= safe_threshold
    ]

    if not candidate_indices:
        return {"v": 0.0, "omega": omega_max}

    # Choisir la direction libre la plus proche du trésor
    best_i = min(
        candidate_indices,
        key=lambda i: abs(normalize_angle(ray_angles[i] - target_angle))
    )

    chosen_angle = ray_angles[best_i]
    angle_error = normalize_angle(chosen_angle - robot.orientation)

    # Commande de suivi de cette direction libre
    if abs(angle_error) > 0.25:
        v = 0.25
        omega = omega_max if angle_error > 0 else -omega_max
    else:
        v = v_max
        omega = 1.2 * angle_error

        if omega > omega_max:
            omega = omega_max
        elif omega < -omega_max:
            omega = -omega_max

    return {"v": v, "omega": omega}