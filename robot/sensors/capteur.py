from abc import ABC, abstractmethod


class Capteur(ABC):
    """
    Classe abstraite pour tous les capteurs du robot.
    """

    @abstractmethod
    def read(self, robot, env):
        """
        Retourne une mesure du capteur à partir du robot et de l'environnement.
        """
        pass