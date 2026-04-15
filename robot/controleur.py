from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None


class Controleur(ABC):
    @abstractmethod
    def lire_commande(self) -> Optional[Dict[str, Any]]:
        pass


class ControleurTerminal(Controleur):
    def lire_commande(self) -> Optional[Dict[str, Any]]:
        print("Commande differentiel : v omega (ex: 1.0 0.5) | q pour quitter")
        entree = input("> ").strip()

        if entree.lower() in ("q", "quit", "exit"):
            return None

        morceaux = entree.split()
        if len(morceaux) != 2:
            print("Erreur: entre 2 valeurs: v omega (ex: 1.0 0.5)")
            return {}

        try:
            v = float(morceaux[0])
            omega = float(morceaux[1])
        except ValueError:
            print("Erreur: v et omega doivent être des nombres.")
            return {}

        return {"v": v, "omega": omega}


class ControleurClavierPygame(Controleur):
    """
    Contrôle simple en différentiel avec clavier :
    - flèche haut/bas : v +/-
    - flèche gauche/droite : omega +/-
    - espace : stop
    """
    def __init__(self, v_max: float = 2.0, omega_max: float = 2.0):
        if pygame is None:
            raise RuntimeError("pygame n'est pas installé. Installe-le avec: pip install pygame")
        self.v_max = float(v_max)
        self.omega_max = float(omega_max)

    def lire_commande(self) -> Optional[Dict[str, Any]]:
        keys = pygame.key.get_pressed()

        v = 0.0
        omega = 0.0

        if keys[pygame.K_UP]:
            v += self.v_max
        if keys[pygame.K_DOWN]:
            v -= self.v_max
        if keys[pygame.K_LEFT]:
            omega += self.omega_max
        if keys[pygame.K_RIGHT]:
            omega -= self.omega_max

        if keys[pygame.K_SPACE]:
            v = 0.0
            omega = 0.0

        return {"v": v, "omega": omega}