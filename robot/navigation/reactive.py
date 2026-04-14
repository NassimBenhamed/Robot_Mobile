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


def sector_mean(distances, start_idx, end_idx):
    if start_idx > end_idx:
        return 0.0
    values = distances[start_idx:end_idx + 1]
    if not values:
        return 0.0
    return sum(values) / len(values)


def analyze_sectors(robot, target):
    lidar = get_lidar(robot)
    if lidar is None or not getattr(lidar, "distances", None):
        return None

    distances = lidar.distances
    n = len(distances)
    if n == 0:
        return None

    ray_angles = build_ray_angles(robot, lidar, n)

    dx = target.x - robot.x
    dy = target.y - robot.y
    target_angle = math.atan2(dy, dx)

    target_i = min(
        range(n),
        key=lambda i: abs(normalize_angle(ray_angles[i] - target_angle))
    )

    front_i = min(
        range(n),
        key=lambda i: abs(normalize_angle(ray_angles[i] - robot.orientation))
    )

    third = max(1, n // 3)

    left_mean = sector_mean(distances, 0, third - 1)
    front_mean = sector_mean(
        distances,
        max(0, front_i - 2),
        min(n - 1, front_i + 2)
    )
    right_mean = sector_mean(distances, n - third, n - 1)

    return {
        "distances": distances,
        "ray_angles": ray_angles,
        "target_angle": target_angle,
        "target_distance": distances[target_i],
        "front_mean": front_mean,
        "left_mean": left_mean,
        "right_mean": right_mean,
    }


def rotate_toward(robot, desired_angle, omega_max=2.8):
    angle_error = normalize_angle(desired_angle - robot.orientation)
    if abs(angle_error) < 0.08:
        return {"v": 0.0, "omega": 0.0}

    return {
        "v": 0.0,
        "omega": omega_max if angle_error > 0 else -omega_max
    }


def go_toward(robot, desired_angle, v_max=0.9, omega_max=2.2):
    angle_error = normalize_angle(desired_angle - robot.orientation)

    if abs(angle_error) > 0.35:
        return {
            "v": 0.10,
            "omega": clamp(2.0 * angle_error, -omega_max, omega_max)
        }

    return {
        "v": v_max,
        "omega": clamp(1.4 * angle_error, -omega_max, omega_max)
    }