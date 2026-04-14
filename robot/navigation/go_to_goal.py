import math


def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def compute_go_to_goal_command(robot, target, v_max: float = 1.25, omega_max: float = 2.6):
    """
    Contrôleur simple :
    - tourne vers la cible
    - avance quand l'angle est correct
    - ralentit à l'approche
    """
    dx = target.x - robot.x
    dy = target.y - robot.y

    dist = math.hypot(dx, dy)
    target_angle = math.atan2(dy, dx)
    angle_error = normalize_angle(target_angle - robot.orientation)

    # cible atteinte
    if dist < 0.18:
        return {"v": 0.0, "omega": 0.0}

    # forte erreur d'angle : tourner presque sur place
    if abs(angle_error) > 0.45:
        v = 0.0
        omega = omega_max if angle_error > 0 else -omega_max
        return {"v": v, "omega": omega}

    # vitesse proportionnelle à la distance, bornée
    v = min(v_max, max(0.22, 1.05 * dist))
    omega = 2.0 * angle_error

    if omega > omega_max:
        omega = omega_max
    elif omega < -omega_max:
        omega = -omega_max

    # si l'angle n'est pas encore parfait, on avance plus doucement
    if abs(angle_error) > 0.20:
        v *= 0.55

    return {"v": v, "omega": omega}