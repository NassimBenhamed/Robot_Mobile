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


def compute_treasure_cost(robot, treasure, k_angle: float = 0.8) -> float:
    """
    Calcule un coût estimé pour atteindre un trésor.
    Coût = distance + pénalité de rotation.
    """
    dx = treasure.x - robot.x
    dy = treasure.y - robot.y

    distance = math.hypot(dx, dy)

    target_angle = math.atan2(dy, dx)
    angle_error = normalize_angle(target_angle - robot.orientation)

    angle_penalty = k_angle * abs(angle_error)

    return distance + angle_penalty


def compute_treasure_utility(robot, treasure, k_angle: float = 0.8, epsilon: float = 1e-6) -> float:
    """
    Utilité greedy :
    utility = value / cost
    """
    cost = compute_treasure_cost(robot, treasure, k_angle=k_angle)
    return treasure.value / max(cost, epsilon)


def select_nearest_treasure(robot, treasures):
    """
    Conserve l'ancienne stratégie pour comparaison ou fallback.
    """
    available = [t for t in treasures if not t.collected]

    if not available:
        return None

    return min(
        available,
        key=lambda t: math.hypot(t.x - robot.x, t.y - robot.y)
    )


def select_greedy_treasure(robot, treasures, k_angle: float = 0.8):
    """
    Sélection greedy :
    choisit le trésor qui maximise value / cost.
    """
    available = [t for t in treasures if not t.collected]

    if not available:
        return None

    return max(
        available,
        key=lambda t: compute_treasure_utility(robot, t, k_angle=k_angle)
    )