from abc import ABC, abstractmethod
from math import cos, sin
import random


class Moteur(ABC):
    """
    Interface commune des moteurs.
    """

    @abstractmethod
    def commander(self, *args, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


class MoteurDifferentiel(Moteur):
    """
    Moteur différentiel avec léger bruit angulaire.

    Le bruit est volontairement faible au début, puis augmente légèrement
    au fil des vagues, avec un plafond pour éviter un comportement abusif.
    """

    def __init__(
        self,
        v=0.0,
        omega=0.0,
        base_noise_sigma_omega=0.05,
        max_noise_sigma_omega=0.14,
        noise_wave_gain=0.01,
    ):
        self.v = v
        self.omega = omega

        self.base_noise_sigma_omega = float(base_noise_sigma_omega)
        self.max_noise_sigma_omega = float(max_noise_sigma_omega)
        self.noise_wave_gain = float(noise_wave_gain)

        self.current_noise_sigma_omega = float(base_noise_sigma_omega)
        self.current_wave_index = 1

    def set_wave_level(self, wave_index: int) -> None:
        """
        Ajuste le niveau de bruit en fonction de la vague.
        """
        self.current_wave_index = max(1, int(wave_index))
        sigma = self.base_noise_sigma_omega + (self.current_wave_index - 1) * self.noise_wave_gain
        self.current_noise_sigma_omega = min(sigma, self.max_noise_sigma_omega)

    def commander(self, v, omega):
        self.v = v
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        """
        Met à jour la pose du robot.

        Le bruit est appliqué principalement lorsque le robot avance presque
        en ligne droite. On stocke aussi sur le robot un indicateur visuel
        permettant de l'afficher en rouge au moment où le bruit agit.
        """
        omega_effectif = self.omega
        noise_applied = False

        if abs(self.v) > 0.05 and abs(self.omega) < 0.20:
            noise = random.uniform(
                -self.current_noise_sigma_omega,
                self.current_noise_sigma_omega
            )
            omega_effectif += noise
            noise_applied = abs(noise) > 1e-9

        robot.noise_active = noise_applied

        robot.orientation += omega_effectif * dt
        robot.x += self.v * cos(robot.orientation) * dt
        robot.y += self.v * sin(robot.orientation) * dt


class MoteurOmnidirectionnel(Moteur):
    """
    Moteur omnidirectionnel sans bruit ajouté pour l'instant.
    """

    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def commander(self, vx, vy, omega):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        theta = robot.orientation

        robot.noise_active = False
        robot.orientation += self.omega * dt
        robot.x += (self.vx * cos(theta) - self.vy * sin(theta)) * dt
        robot.y += (self.vx * sin(theta) + self.vy * cos(theta)) * dt