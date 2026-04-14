import math
from dataclasses import dataclass


@dataclass
class Point2D:
    x: float
    y: float


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def point_in_bounds(x: float, y: float, env, margin: float = 0.0) -> bool:
    return (
        margin <= x <= env.largeur - margin and
        margin <= y <= env.hauteur - margin
    )


def point_collides(x: float, y: float, env, robot_radius: float, extra_margin: float = 0.10) -> bool:
    # murs
    if not point_in_bounds(x, y, env, margin=robot_radius + extra_margin):
        return True

    # obstacles
    for obs in env.obstacles:
        d = distance(x, y, obs.x, obs.y)
        if d <= (obs.rayon + robot_radius + extra_margin):
            return True

    return False


def segment_intersects_circle(ax, ay, bx, by, cx, cy, radius) -> bool:
    """
    Test si le segment AB intersecte le cercle de centre C et rayon radius.
    """
    abx = bx - ax
    aby = by - ay
    acx = cx - ax
    acy = cy - ay

    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return distance(ax, ay, cx, cy) <= radius

    t = (acx * abx + acy * aby) / ab_len_sq
    t = clamp(t, 0.0, 1.0)

    px = ax + t * abx
    py = ay + t * aby

    return distance(px, py, cx, cy) <= radius


def first_blocking_obstacle(robot, target, env, margin: float = 0.12):
    """
    Retourne le premier obstacle bloquant la ligne robot -> cible.
    """
    rx, ry = robot.x, robot.y
    tx, ty = target.x, target.y

    blockers = []

    for obs in env.obstacles:
        effective_radius = obs.rayon + robot.rayon + margin
        if segment_intersects_circle(rx, ry, tx, ty, obs.x, obs.y, effective_radius):
            d = distance(rx, ry, obs.x, obs.y)
            blockers.append((d, obs))

    if not blockers:
        return None

    blockers.sort(key=lambda item: item[0])
    return blockers[0][1]


def line_of_sight_clear(robot, target, env, margin: float = 0.12) -> bool:
    return first_blocking_obstacle(robot, target, env, margin=margin) is None


def build_detour_candidates(robot, target, obstacle, env, margin: float = 0.35):
    """
    Construit 4 candidats autour de l'obstacle :
    - gauche / droite
    - avec un léger biais vers l'avant pour mieux contourner
    """
    rx, ry = robot.x, robot.y
    tx, ty = target.x, target.y
    ox, oy = obstacle.x, obstacle.y

    dx = tx - rx
    dy = ty - ry
    norm = math.hypot(dx, dy)
    if norm < 1e-9:
        return []

    ux = dx / norm
    uy = dy / norm

    # vecteur perpendiculaire
    px = -uy
    py = ux

    clearance = obstacle.rayon + robot.rayon + margin
    forward = 0.60 * clearance

    candidates = [
        Point2D(ox + px * clearance + ux * forward, oy + py * clearance + uy * forward),
        Point2D(ox - px * clearance + ux * forward, oy - py * clearance + uy * forward),
        Point2D(ox + px * clearance - ux * 0.20, oy + py * clearance - uy * 0.20),
        Point2D(ox - px * clearance - ux * 0.20, oy - py * clearance - uy * 0.20),
    ]

    valid = []
    for p in candidates:
        if point_collides(p.x, p.y, env, robot.rayon, extra_margin=0.06):
            continue
        valid.append(p)

    return valid


def choose_best_detour(robot, target, env):
    """
    Si la ligne directe est bloquée, on choisit un waypoint autour du premier obstacle bloquant.
    """
    blocker = first_blocking_obstacle(robot, target, env, margin=0.12)
    if blocker is None:
        return None

    candidates = build_detour_candidates(robot, target, blocker, env, margin=0.35)
    if not candidates:
        return None

    scored = []

    for p in candidates:
        # Il faut au moins voir le waypoint depuis le robot
        temp_target = Point2D(p.x, p.y)
        if not line_of_sight_clear(robot, temp_target, env, margin=0.08):
            continue

        # score = proximité du waypoint + rapprochement de la cible finale
        score = (
            1.3 * distance(robot.x, robot.y, p.x, p.y) +
            1.0 * distance(p.x, p.y, target.x, target.y)
        )
        scored.append((score, p))

    if not scored:
        return None

    scored.sort(key=lambda item: item[0])
    return scored[0][1]