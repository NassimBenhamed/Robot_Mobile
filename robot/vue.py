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
    """
    def __init__(self, largeur_px: int = 800, hauteur_px: int = 600, scale: int = 80):
        if pygame is None:
            raise RuntimeError("pygame n'est pas installé. Installe-le avec: pip install pygame")

        pygame.init()
        pygame.font.init()

        self.largeur_px = int(largeur_px)
        self.hauteur_px = int(hauteur_px)
        self.scale = int(scale)

        self.screen = pygame.display.set_mode((self.largeur_px, self.hauteur_px))
        pygame.display.set_caption("Robot MVC")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)

    def convertir_coordonnees(self, x: float, y: float) -> Tuple[int, int]:
        # (0,0) monde en bas-gauche -> pygame en haut-gauche
        px = int(x * self.scale)
        py = int(self.hauteur_px - (y * self.scale))
        return px, py

    def dessiner_robot(self, robot: RobotMobile) -> None:
        px, py = self.convertir_coordonnees(robot.x, robot.y)
        r = max(2, int(robot.rayon * self.scale))

        pygame.draw.circle(self.screen, (30, 144, 255), (px, py), r)

        x2 = px + int(1.5 * r * math.cos(robot.orientation))
        y2 = py - int(1.5 * r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 255, 255), (px, py), (x2, y2), 2)

    def dessiner_treasures(self, env: Environnement) -> None:
        for treasure in env.treasures:
            if treasure.collected:
                continue

            px, py = self.convertir_coordonnees(treasure.x, treasure.y)
            r = max(4, int(treasure.radius * self.scale))

            pygame.draw.circle(self.screen, (255, 215, 0), (px, py), r)
            pygame.draw.circle(self.screen, (0, 0, 0), (px, py), r, 2)

    def dessiner_hud(self, env: Environnement) -> None:
        if env.game is None:
            return

        texte_1 = f"Score : {env.game.score}"
        texte_2 = f"Temps restant : {env.game.time_left:.1f}s"
        texte_3 = f"Tresors : {env.game.treasures_collected}/{len(env.treasures)}"

        surf_1 = self.font.render(texte_1, True, (255, 255, 255))
        surf_2 = self.font.render(texte_2, True, (255, 255, 255))
        surf_3 = self.font.render(texte_3, True, (255, 255, 255))

        self.screen.blit(surf_1, (10, 10))
        self.screen.blit(surf_2, (10, 35))
        self.screen.blit(surf_3, (10, 60))

    def dessiner_environnement(self, env: Environnement) -> None:
        self.screen.fill((20, 20, 20))

        # Obstacles
        for obs in env.obstacles:
            if hasattr(obs, "x") and hasattr(obs, "y") and hasattr(obs, "rayon"):
                px, py = self.convertir_coordonnees(float(obs.x), float(obs.y))
                r = max(2, int(float(obs.rayon) * self.scale))
                pygame.draw.circle(self.screen, (220, 20, 60), (px, py), r)

        # Trésors
        self.dessiner_treasures(env)

        # Robot
        if env.robot is not None:
            self.dessiner_robot(env.robot)

        # HUD
        self.dessiner_hud(env)

        pygame.display.flip()

    def tick(self, fps: int = 60) -> float:
        ms = self.clock.tick(int(fps))
        return ms / 1000.0