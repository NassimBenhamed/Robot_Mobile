import csv
import math
import os


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def segment_intersects_circle(ax, ay, bx, by, cx, cy, radius):
    abx = bx - ax
    aby = by - ay
    acx = cx - ax
    acy = cy - ay

    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return distance(ax, ay, cx, cy) <= radius

    t = (acx * abx + acy * aby) / ab_len_sq
    t = max(0.0, min(1.0, t))

    px = ax + t * abx
    py = ay + t * aby

    return distance(px, py, cx, cy) <= radius


def count_blocking_obstacles(start_x, start_y, end_x, end_y, obstacles, robot_radius):
    count = 0
    for obs in obstacles:
        effective_radius = obs.rayon + robot_radius + 0.12
        if segment_intersects_circle(start_x, start_y, end_x, end_y, obs.x, obs.y, effective_radius):
            count += 1
    return count


class WaveCSVLogger:
    def __init__(self, filepath="wave_report.csv", speed_estimate=1.10):
        self.filepath = filepath
        self.speed_estimate = speed_estimate
        self.current_rows = {}
        self.current_wave = None

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "wave",
                    "treasure_id",
                    "start_x",
                    "start_y",
                    "treasure_x",
                    "treasure_y",
                    "straight_distance",
                    "straight_time_s",
                    "blocking_obstacles_count",
                    "collision_penalty_estimate_s",
                    "adjusted_estimate_s",
                    "nearest_neighbor_1_id",
                    "nearest_neighbor_1_distance",
                    "nearest_neighbor_2_id",
                    "nearest_neighbor_2_distance",
                    "collected",
                    "actual_time_to_collect_s",
                    "delta_vs_straight_s",
                ])

    def _nearest_neighbors(self, treasures, index):
        base = treasures[index]
        neighbors = []

        for j, other in enumerate(treasures):
            if j == index:
                continue
            d = distance(base.x, base.y, other.x, other.y)
            neighbors.append((d, j))

        neighbors.sort(key=lambda x: x[0])
        first = neighbors[0] if len(neighbors) > 0 else (None, None)
        second = neighbors[1] if len(neighbors) > 1 else (None, None)
        return first, second

    def start_wave(self, wave_index, start_x, start_y, treasures, obstacles, robot_radius):
        self.current_wave = wave_index
        self.current_rows = {}

        for i, t in enumerate(treasures):
            straight_dist = distance(start_x, start_y, t.x, t.y)
            straight_time = straight_dist / max(self.speed_estimate, 1e-6)

            blocking_count = count_blocking_obstacles(
                start_x, start_y, t.x, t.y, obstacles, robot_radius
            )

            # estimation heuristique simple
            collision_penalty = 1.8 * blocking_count
            adjusted_estimate = straight_time + collision_penalty

            n1, n2 = self._nearest_neighbors(treasures, i)

            n1_dist, n1_id = n1
            n2_dist, n2_id = n2

            self.current_rows[id(t)] = {
                "wave": wave_index,
                "treasure_id": i,
                "start_x": start_x,
                "start_y": start_y,
                "treasure_x": t.x,
                "treasure_y": t.y,
                "straight_distance": round(straight_dist, 4),
                "straight_time_s": round(straight_time, 4),
                "blocking_obstacles_count": blocking_count,
                "collision_penalty_estimate_s": round(collision_penalty, 4),
                "adjusted_estimate_s": round(adjusted_estimate, 4),
                "nearest_neighbor_1_id": n1_id if n1_id is not None else "",
                "nearest_neighbor_1_distance": round(n1_dist, 4) if n1_dist is not None else "",
                "nearest_neighbor_2_id": n2_id if n2_id is not None else "",
                "nearest_neighbor_2_distance": round(n2_dist, 4) if n2_dist is not None else "",
                "collected": 0,
                "actual_time_to_collect_s": "",
                "delta_vs_straight_s": "",
            }

    def mark_collected(self, treasure, time_elapsed):
        key = id(treasure)
        if key not in self.current_rows:
            return

        row = self.current_rows[key]
        row["collected"] = 1
        row["actual_time_to_collect_s"] = round(time_elapsed, 4)
        row["delta_vs_straight_s"] = round(
            float(time_elapsed) - float(row["straight_time_s"]), 4
        )

    def flush_wave(self):
        if not self.current_rows:
            return

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in self.current_rows.values():
                writer.writerow([
                    row["wave"],
                    row["treasure_id"],
                    row["start_x"],
                    row["start_y"],
                    row["treasure_x"],
                    row["treasure_y"],
                    row["straight_distance"],
                    row["straight_time_s"],
                    row["blocking_obstacles_count"],
                    row["collision_penalty_estimate_s"],
                    row["adjusted_estimate_s"],
                    row["nearest_neighbor_1_id"],
                    row["nearest_neighbor_1_distance"],
                    row["nearest_neighbor_2_id"],
                    row["nearest_neighbor_2_distance"],
                    row["collected"],
                    row["actual_time_to_collect_s"],
                    row["delta_vs_straight_s"],
                ])