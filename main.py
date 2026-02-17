import math
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel

# =========================
# Test moteur différentiel
# =========================
moteur_diff = MoteurDifferentiel()
robot = RobotMobile(moteur=moteur_diff)

dt = 1.0

robot.afficher()
robot.commander(v=1.0, omega=0.0)
robot.mettre_a_jour(dt)
robot.afficher()

# =========================
# Test déplacement x=3, y=1
# =========================
robot.commander(v=2.0, omega=0.0)
robot.mettre_a_jour(1.5)
robot.afficher()

print("Nombre total de robots :", RobotMobile.nombre_robots())

# =========================
# Test moteur omnidirectionnel
# =========================
moteur_omni = MoteurOmnidirectionnel()
robot2 = RobotMobile(moteur=moteur_omni)

robot2.afficher()
robot2.commander(vx=3.0, vy=1.0, omega=0.0)
robot2.mettre_a_jour(1.0)
robot2.afficher()
