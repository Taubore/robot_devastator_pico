"""
Script de test rapide pour vérifier le servo et le capteur ultrason sur le Pico.

Ce fichier n'est pas le firmware principal. Il sert à faire bouger le servo vers trois positions,
puis à lire une distance dans chaque direction.
"""

from time import sleep_ms       # pyright: ignore[reportAttributeAccessIssue]
from capteur_ultrason import CapteurUltrason
from servo import Servo


ANGLE_GAUCHE = 45
ANGLE_CENTRE = 90
ANGLE_DROITE = 135

DELAI_STABILISATION_MS = 1250


capteur = CapteurUltrason(14)
servo = Servo(15)

while True:
    # Le délai laisse le temps au servo d'atteindre sa position avant la mesure.
    servo.angle = ANGLE_GAUCHE
    sleep_ms(DELAI_STABILISATION_MS)
    dist_gauche = capteur.lire_distance_mm()

    servo.angle = ANGLE_CENTRE
    sleep_ms(DELAI_STABILISATION_MS)
    dist_devant = capteur.lire_distance_mm()

    servo.angle = ANGLE_DROITE
    sleep_ms(DELAI_STABILISATION_MS)
    dist_droite = capteur.lire_distance_mm()

    servo.angle = ANGLE_CENTRE
    sleep_ms(DELAI_STABILISATION_MS)
    dist_devant = capteur.lire_distance_mm()

    print("Distances lues :", dist_devant, dist_gauche, dist_droite)
