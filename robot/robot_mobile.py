import math
from typing import Optional, Any, List
from robot.moteur import Moteur


class RobotMobile:
    _nb_robots = 0

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        orientation: float = 0.0,
        moteur: Optional[Moteur] = None,
        rayon: float = 0.2,
    ):
        self.__x = float(x)
        self.__y = float(y)
        self.__orientation = float(orientation) % (2 * math.pi)
        self.rayon = float(rayon)
        self.capteurs: List[Any] = []

        # Indicateur visuel : True quand le bruit agit sur le robot à ce tick.
        self.noise_active = False

        if moteur is not None and not RobotMobile.moteur_valide(moteur):
            raise TypeError("Le moteur fourni n'est pas valide")

        self.moteur = moteur
        RobotMobile._nb_robots += 1

    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float) -> None:
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float) -> None:
        self.__y = float(value)

    @property
    def orientation(self) -> float:
        return self.__orientation

    @orientation.setter
    def orientation(self, value: float) -> None:
        self.__orientation = float(value) % (2 * math.pi)

    def avancer(self, distance: float) -> None:
        self.__x += float(distance) * math.cos(self.__orientation)
        self.__y += float(distance) * math.sin(self.__orientation)

    def tourner(self, angle: float) -> None:
        self.orientation = self.__orientation + float(angle)

    def afficher(self) -> None:
        print(self)

    def commander(self, **kwargs: Any) -> None:
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt: float) -> None:
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, float(dt))

    def __str__(self) -> str:
        return f"(x={self.x:.2f}, y={self.y:.2f}, orientation={self.orientation:.2f})"

    @classmethod
    def nombre_robots(cls) -> int:
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur: Any) -> bool:
        return isinstance(moteur, Moteur)

    def add_capteur(self, capteur: Any) -> None:
        self.capteurs.append(capteur)

    def read_sensors(self, env) -> dict:
        mesures = {}
        for capteur in self.capteurs:
            nom = capteur.__class__.__name__
            mesures[nom] = capteur.read(self, env)
        return mesures