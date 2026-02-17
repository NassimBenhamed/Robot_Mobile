from typing import Tuple

from robot.environnement import Environnement
from robot.robot_mobile import RobotMobile

# Pygame est optionnel : on importera seulement si nécessaire
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
        print(f"ENV {env.largeur:.1f}x{env.hauteur:.1f} | Robot={env.robot} | Obstacles={len(env.obstacles)}")


class VuePygame:
    """
    Vue graphique simple.
    - scale : pixels par unité monde
    """
    def __init__(self, largeur_px: int = 800, hauteur_px: int = 600, scale: int = 80):
        if pygame is None:
            raise RuntimeError("pygame n'est pas installé. Installe-le avec: pip install pygame")

        pygame.init()
        self.largeur_px = int(largeur_px)
        self.hauteur_px = int(hauteur_px)
        self.scale = int(scale)
        self.screen = pygame.display.set_mode((self.largeur_px, self.hauteur_px))
        pygame.display.set_caption("Robot MVC")
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x: float, y: float) -> Tuple[int, int]:
        # (0,0) en bas à gauche du monde -> pygame (0,0) en haut à gauche
        px = int(x * self.scale)
        py = int(self.hauteur_px - (y * self.scale))
        return px, py

    def dessiner_robot(self, robot: RobotMobile) -> None:
        px, py = self.convertir_coordonnees(robot.x, robot.y)
        r = max(2, int(robot.rayon * self.scale))
        pygame.draw.circle(self.screen, (30, 144, 255), (px, py), r)  # bleu
        # direction (petit segment)
        dx = int(r * 1.5)
        dy = int(r * 1.5)
        x2 = px + int(dx * __import__("math").cos(robot.orientation))
        y2 = py - int(dy * __import__("math").sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 255, 255), (px, py), (x2, y2), 2)

    def dessiner_environnement(self, env: Environnement) -> None:
        self.screen.fill((20, 20, 20))

        # obstacles circulaires (si présents)
        for obs in env.obstacles:
            # on dessine seulement si l'obstacle a x,y,rayon (ObstacleCirculaire)
            if hasattr(obs, "x") and hasattr(obs, "y") and hasattr(obs, "rayon"):
                px, py = self.convertir_coordonnees(float(obs.x), float(obs.y))
                r = max(2, int(float(obs.rayon) * self.scale))
                pygame.draw.circle(self.screen, (220, 20, 60), (px, py), r)  # rouge

        if env.robot is not None:
            self.dessiner_robot(env.robot)

        pygame.display.flip()

    def tick(self, fps: int = 60) -> float:
        """
        Bloque pour maintenir un fps constant.
        Retourne dt (secondes).
        """
        ms = self.clock.tick(int(fps))
        return ms / 1000.0
