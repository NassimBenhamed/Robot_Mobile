from typing import Tuple
import math

from robot.environnement import Environnement
from robot.robot_mobile import RobotMobile

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None


class VueTerminalRobot:
    def dessiner_robot(self, robot: RobotMobile) -> None:
        print(robot)


class VueTerminalEnvironnement:
    def dessiner_environnement(self, env: Environnement) -> None:
        if env.robot is None:
            print("Environnement sans robot.")
            return
        print(
            f"ENV {env.largeur:.1f}x{env.hauteur:.1f} | "
            f"Robot={env.robot} | Obstacles={len(env.obstacles)} | "
            f"Trésors={len(env.treasures)}"
        )


class VuePygame:
    """
    Vue graphique simple.
    - scale : pixels par unité monde
    - show_sensors : affiche ou non les capteurs
    - show_paths : affiche ou non les chemins / debug path
    """
    def __init__(
        self,
        largeur_px: int = 800,
        hauteur_px: int = 600,
        scale: int = 80,
        show_sensors: bool = True,
        show_paths: bool = True,
    ):
        if pygame is None:
            raise RuntimeError("pygame n'est pas installé. Installe-le avec: pip install pygame")

        pygame.init()
        pygame.font.init()

        self.largeur_px = int(largeur_px)
        self.hauteur_px = int(hauteur_px)
        self.scale = int(scale)

        self.show_sensors = bool(show_sensors)
        self.show_paths = bool(show_paths)

        self.screen = pygame.display.set_mode((self.largeur_px, self.hauteur_px))
        pygame.display.set_caption("Treasure Hunter Robot")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 15)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 18, bold=True)

        self.quit_button_rect = pygame.Rect(self.largeur_px - 170, 12, 150, 38)
        self.pause_button_rect = pygame.Rect(self.largeur_px - 340, 12, 150, 38)

    def convertir_coordonnees(self, x: float, y: float) -> Tuple[int, int]:
        px = int(x * self.scale)
        py = int(self.hauteur_px - (y * self.scale))
        return px, py

    def dessiner_robot(self, robot: RobotMobile) -> None:
        px, py = self.convertir_coordonnees(robot.x, robot.y)
        r = max(2, int(robot.rayon * self.scale))

        # Le robot devient rouge lorsque le bruit est actif.
        body_color = (30, 144, 255)

        pygame.draw.circle(self.screen, body_color, (px, py), r)

        x2 = px + int(1.5 * r * math.cos(robot.orientation))
        y2 = py - int(1.5 * r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 255, 255), (px, py), (x2, y2), 2)

    def dessiner_lidar(self, robot: RobotMobile) -> None:
        if not self.show_sensors:
            return

        for capteur in getattr(robot, "capteurs", []):
            if capteur.__class__.__name__ == "Lidar":
                x0, y0 = self.convertir_coordonnees(robot.x, robot.y)

                for (hx, hy) in capteur.hit_points:
                    x1, y1 = self.convertir_coordonnees(hx, hy)
                    pygame.draw.line(self.screen, (0, 255, 0), (x0, y0), (x1, y1), 1)
                    pygame.draw.circle(self.screen, (0, 255, 0), (x1, y1), 2)

    def dessiner_treasures(self, env: Environnement) -> None:
        """
        Dessine les trésors avec :
        - une couleur selon la valeur
        - la valeur affichée sur le board
        """
        for treasure in env.treasures:
            if treasure.collected:
                continue

            px, py = self.convertir_coordonnees(treasure.x, treasure.y)
            r = max(4, int(treasure.radius * self.scale))

            if treasure.value <= 10:
                color = (80, 170, 255)
            elif treasure.value <= 15:
                color = (255, 165, 0)
            else:
                color = (220, 60, 60)

            pygame.draw.circle(self.screen, color, (px, py), r)
            pygame.draw.circle(self.screen, (0, 0, 0), (px, py), r, 2)

            value_text = self.small_font.render(str(treasure.value), True, (255, 255, 255))
            value_rect = value_text.get_rect(center=(px, py - max(12, r + 10)))
            self.screen.blit(value_text, value_rect)

    def dessiner_house(self, env: Environnement) -> None:
        if env.game is None or env.game.house is None:
            return

        house = env.game.house
        half = house.size / 2.0

        x_min = house.x - half
        y_min = house.y - half

        top_left = self.convertir_coordonnees(x_min, y_min + house.size)
        width_px = int(house.size * self.scale)
        height_px = int(house.size * self.scale)

        rect = pygame.Rect(top_left[0], top_left[1], width_px, height_px)

        color = (180, 40, 40)
        if env.robot is not None and env.game.robot_in_house(env.robot):
            color = (40, 180, 60)

        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def dessiner_debug_path(self, env: Environnement) -> None:
        if not self.show_paths:
            return

        if env.debug_direct_line is not None:
            x1, y1, x2, y2, is_clear = env.debug_direct_line
            p1 = self.convertir_coordonnees(x1, y1)
            p2 = self.convertir_coordonnees(x2, y2)

            color = (0, 200, 0) if is_clear else (220, 60, 60)
            pygame.draw.line(self.screen, color, p1, p2, 2)

        if env.debug_path and len(env.debug_path) >= 2:
            converted = [self.convertir_coordonnees(x, y) for (x, y) in env.debug_path]

            for i in range(len(converted) - 1):
                pygame.draw.line(self.screen, (80, 170, 255), converted[i], converted[i + 1], 3)

            for p in converted[1:-1]:
                pygame.draw.circle(self.screen, (255, 140, 0), p, 6)

        if env.debug_target is not None:
            px, py = self.convertir_coordonnees(env.debug_target.x, env.debug_target.y)
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 7, 2)

    def dessiner_hud(self, env: Environnement, mode: str) -> None:
        if env.game is None:
            return

        texte_1 = f"Score : {env.game.score}"
        texte_2 = f"Temps restant : {env.game.time_left:.1f}s"
        texte_3 = f"Vague : {env.game.wave_index}"
        texte_4 = f"Mode : {'IA' if mode == 'auto' else 'Joueur'}"

        surf_1 = self.font.render(texte_1, True, (255, 255, 255))
        surf_2 = self.font.render(texte_2, True, (255, 255, 255))
        surf_3 = self.font.render(texte_3, True, (255, 255, 255))
        surf_4 = self.font.render(texte_4, True, (255, 255, 255))

        self.screen.blit(surf_1, (10, 10))
        self.screen.blit(surf_2, (10, 35))
        self.screen.blit(surf_3, (10, 60))
        self.screen.blit(surf_4, (10, 85))

    def dessiner_bouton_pause(self, paused: bool) -> None:
        color = (180, 140, 40) if not paused else (40, 140, 180)
        pygame.draw.rect(self.screen, color, self.pause_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pause_button_rect, 2, border_radius=8)

        label = "Pause" if not paused else "Reprendre"
        texte = self.button_font.render(label, True, (255, 255, 255))
        texte_rect = texte.get_rect(center=self.pause_button_rect.center)
        self.screen.blit(texte, texte_rect)

    def dessiner_bouton_fin(self) -> None:
        pygame.draw.rect(self.screen, (180, 40, 40), self.quit_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button_rect, 2, border_radius=8)

        texte = self.button_font.render("Fin de partie", True, (255, 255, 255))
        texte_rect = texte.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(texte, texte_rect)

    def dessiner_environnement(self, env: Environnement, paused: bool = False, mode: str = "auto") -> None:
        self.screen.fill((20, 20, 20))

        for obs in env.obstacles:
            if hasattr(obs, "x") and hasattr(obs, "y") and hasattr(obs, "rayon"):
                px, py = self.convertir_coordonnees(float(obs.x), float(obs.y))
                r = max(2, int(float(obs.rayon) * self.scale))
                pygame.draw.circle(self.screen, (220, 20, 60), (px, py), r)

        self.dessiner_house(env)
        self.dessiner_treasures(env)
        self.dessiner_debug_path(env)

        if env.robot is not None:
            self.dessiner_lidar(env.robot)
            self.dessiner_robot(env.robot)

        self.dessiner_hud(env, mode)
        self.dessiner_bouton_pause(paused)
        self.dessiner_bouton_fin()

        if paused:
            overlay = self.font.render("PAUSE", True, (255, 255, 0))
            self.screen.blit(overlay, (self.largeur_px // 2 - 35, 12))

        pygame.display.flip()

    def draw_end_screen(self, score: int, wave: int) -> None:
        """
        Petit menu de fin de partie.
        """
        self.screen.fill((15, 15, 15))

        title = self.title_font.render("Fin de partie", True, (255, 255, 255))
        line_1 = self.font.render(f"Score final : {score}", True, (255, 255, 255))
        line_2 = self.font.render(f"Vagues atteintes : {wave}", True, (255, 255, 255))
        line_3 = self.small_font.render("Appuie sur une touche ou clique pour fermer", True, (200, 200, 200))

        self.screen.blit(title, title.get_rect(center=(self.largeur_px // 2, 180)))
        self.screen.blit(line_1, line_1.get_rect(center=(self.largeur_px // 2, 250)))
        self.screen.blit(line_2, line_2.get_rect(center=(self.largeur_px // 2, 290)))
        self.screen.blit(line_3, line_3.get_rect(center=(self.largeur_px // 2, 360)))

        pygame.display.flip()

    def gerer_evenements(self):
        """
        Retourne :
        - "quit"
        - "pause_toggle"
        - "none"
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.quit_button_rect.collidepoint(event.pos):
                    return "quit"
                if self.pause_button_rect.collidepoint(event.pos):
                    return "pause_toggle"

        return "none"

    def tick(self, fps: int = 60) -> float:
        ms = self.clock.tick(int(fps))
        return ms / 1000.0