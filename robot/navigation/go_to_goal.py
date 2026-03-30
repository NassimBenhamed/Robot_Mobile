import math


def normalize_angle(angle: float) -> float:
    """
    Ramène un angle dans [-pi, pi].
    """
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def compute_go_to_goal_command(robot, target, v_max: float = 1.5, omega_max: float = 2.0):
    """
    Retourne une commande différentielle simple pour aller vers la cible.
    """
    dx = target.x - robot.x
    dy = target.y - robot.y

    target_angle = math.atan2(dy, dx)
    angle_error = normalize_angle(target_angle - robot.orientation)

    # Si l'erreur angulaire est forte, on tourne presque sur place
    if abs(angle_error) > 0.3:
        v = 0.0
        omega = omega_max if angle_error > 0 else -omega_max
    else:
        v = v_max
        omega = 1.5 * angle_error

        # saturation
        if omega > omega_max:
            omega = omega_max
        elif omega < -omega_max:
            omega = -omega_max

    return {"v": v, "omega": omega}