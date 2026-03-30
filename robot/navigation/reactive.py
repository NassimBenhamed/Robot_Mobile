import math


def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


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


def extract_free_segments(distances, safe_threshold: float, min_segment_size: int = 2):
    """
    Regroupe les rayons consécutifs suffisamment libres.
    Retourne une liste de tuples (start, end).
    """
    segments = []
    start = None

    for i, d in enumerate(distances):
        if d >= safe_threshold:
            if start is None:
                start = i
        else:
            if start is not None:
                end = i - 1
                if end - start + 1 >= min_segment_size:
                    segments.append((start, end))
                start = None

    if start is not None:
        end = len(distances) - 1
        if end - start + 1 >= min_segment_size:
            segments.append((start, end))

    return segments


def choose_best_segment(ray_angles, distances, segments, target_angle):
    """
    Choisit le meilleur groupe de rayons libres.
    On favorise :
    - largeur du couloir
    - distance moyenne
    - proximité angulaire avec la cible
    """
    best_segment = None
    best_score = -float("inf")

    for start, end in segments:
        width = end - start + 1
        center = (start + end) // 2
        mean_clearance = sum(distances[start:end + 1]) / width
        center_angle = ray_angles[center]
        angle_cost = abs(normalize_angle(center_angle - target_angle))

        score = (1.8 * width) + (1.0 * mean_clearance) - (2.0 * angle_cost)

        if score > best_score:
            best_score = score
            best_segment = (start, end)

    return best_segment


def compute_free_space_command(
    robot,
    target,
    safe_threshold: float = 1.15,
    blocked_threshold: float = 0.90,
    v_max: float = 0.95,
    omega_max: float = 2.5
):
    """
    Navigation réactive par groupes de rayons libres.

    Retourne :
    - cmd : dictionnaire {"v": ..., "omega": ...}
    - chosen_center_i : indice du rayon central choisi, utile pour garder
      le même couloir quelques frames
    """
    lidar = get_lidar(robot)
    if lidar is None or not getattr(lidar, "distances", None):
        return None, None

    distances = lidar.distances
    n = len(distances)
    if n == 0:
        return None, None

    ray_angles = build_ray_angles(robot, lidar, n)

    dx = target.x - robot.x
    dy = target.y - robot.y
    target_angle = math.atan2(dy, dx)

    target_i = min(
        range(n),
        key=lambda i: abs(normalize_angle(ray_angles[i] - target_angle))
    )
    target_distance = distances[target_i]

    # Si la direction du trésor est clairement libre, on y va directement
    if target_distance >= safe_threshold:
        chosen_center_i = target_i
        chosen_angle = ray_angles[chosen_center_i]
    else:
        free_segments = extract_free_segments(
            distances,
            safe_threshold=safe_threshold,
            min_segment_size=2
        )

        if not free_segments:
            best_i = max(range(n), key=lambda i: distances[i])
            chosen_center_i = best_i
            chosen_angle = ray_angles[chosen_center_i]
            angle_error = normalize_angle(chosen_angle - robot.orientation)

            cmd = {
                "v": 0.0,
                "omega": omega_max if angle_error >= 0 else -omega_max
            }
            return cmd, chosen_center_i

        best_segment = choose_best_segment(ray_angles, distances, free_segments, target_angle)
        start, end = best_segment
        chosen_center_i = (start + end) // 2
        chosen_angle = ray_angles[chosen_center_i]

    angle_error = normalize_angle(chosen_angle - robot.orientation)

    # Plus réactif qu'avant :
    # si la cible est bloquée -> on tourne plus franchement
    if target_distance < blocked_threshold:
        v = 0.08
        omega = omega_max if angle_error >= 0 else -omega_max
    elif abs(angle_error) > 0.35:
        v = 0.18
        omega = clamp(2.2 * angle_error, -omega_max, omega_max)
    else:
        v = v_max
        omega = clamp(1.6 * angle_error, -omega_max, omega_max)

    return {"v": v, "omega": omega}, chosen_center_i