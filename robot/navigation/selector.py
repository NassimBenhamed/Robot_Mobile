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


def build_ray_angles(robot, lidar, n: int):
    if n == 1:
        return [robot.orientation]

    angle_start = robot.orientation - lidar.fov / 2.0
    angle_step = lidar.fov / (n - 1)
    return [angle_start + i * angle_step for i in range(n)]


def corridor_clearance_to_point(robot, x: float, y: float, neighbor_span: int = 1) -> float:
    """
    Mesure la 'qualité' du couloir vers un point à partir du Lidar.
    On prend le minimum autour du rayon cible pour être prudent.
    """
    lidar = get_lidar(robot)
    if lidar is None or not getattr(lidar, "distances", None):
        return 0.0

    distances = lidar.distances
    n = len(distances)
    if n == 0:
        return 0.0

    ray_angles = build_ray_angles(robot, lidar, n)
    target_angle = math.atan2(y - robot.y, x - robot.x)

    target_i = min(
        range(n),
        key=lambda i: abs(normalize_angle(ray_angles[i] - target_angle))
    )

    start = max(0, target_i - neighbor_span)
    end = min(n - 1, target_i + neighbor_span)

    return min(distances[start:end + 1])


def compute_treasure_cost(robot, treasure, k_angle: float = 0.7) -> float:
    dx = treasure.x - robot.x
    dy = treasure.y - robot.y

    distance = math.hypot(dx, dy)
    target_angle = math.atan2(dy, dx)
    angle_error = normalize_angle(target_angle - robot.orientation)
    angle_penalty = k_angle * abs(angle_error)

    return distance + angle_penalty


def estimate_trip_time(distance_value: float, speed_estimate: float = 0.75) -> float:
    return distance_value / max(speed_estimate, 1e-6)


def select_feasible_treasure(robot, treasures, game, k_angle: float = 0.7, safety_margin: float = 4.0):
    """
    Choisit un trésor faisable dans le temps :
    aller + retour maison + marge.
    """
    available = [t for t in treasures if not t.collected]
    if not available or game.house is None:
        return None

    candidates = []

    for t in available:
        go_cost = compute_treasure_cost(robot, t, k_angle=k_angle)

        dist_treasure_to_house = math.hypot(
            game.house.x - t.x,
            game.house.y - t.y
        )

        estimated_total_time = (
            estimate_trip_time(go_cost) +
            estimate_trip_time(dist_treasure_to_house)
        )

        if estimated_total_time + safety_margin < game.time_left:
            utility = t.value / max(go_cost, 1e-6)
            candidates.append((utility, t))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def select_best_open_treasure(
    robot,
    treasures,
    game,
    k_angle: float = 0.7,
    safety_margin: float = 4.0,
    min_clearance: float = 0.95,
):
    """
    Choisit parmi les trésors faisables celui qui combine :
    - utilité (valeur / coût)
    - ouverture réelle du couloir Lidar
    """
    available = [t for t in treasures if not t.collected]
    if not available or game.house is None:
        return None

    candidates = []

    for t in available:
        go_cost = compute_treasure_cost(robot, t, k_angle=k_angle)

        dist_treasure_to_house = math.hypot(
            game.house.x - t.x,
            game.house.y - t.y
        )

        estimated_total_time = (
            estimate_trip_time(go_cost) +
            estimate_trip_time(dist_treasure_to_house)
        )

        if estimated_total_time + safety_margin >= game.time_left:
            continue

        clearance = corridor_clearance_to_point(robot, t.x, t.y, neighbor_span=1)
        if clearance < min_clearance:
            continue

        utility = t.value / max(go_cost, 1e-6)

        # Score final : utilité + bonus si le couloir est bien ouvert
        score = utility + 0.35 * clearance
        candidates.append((score, t))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def select_nearest_treasure(robot, treasures):
    available = [t for t in treasures if not t.collected]
    if not available:
        return None

    return min(
        available,
        key=lambda t: math.hypot(t.x - robot.x, t.y - robot.y)
    )