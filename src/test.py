from time import sleep_ms       # pyright: ignore[reportAttributeAccessIssue]
from capteur_ultrason import CapteurUltrason
from servo import Servo

capteur = CapteurUltrason(14)
servo = Servo(15)

while True:
    servo.angle = 45
    sleep_ms(1250)
    dist_gauche = capteur.lire_distance_mm()

    servo.angle = 90
    sleep_ms(1250) # Attente pour que le servo se stabilise avant de lire les capteurs
    dist_devant = capteur.lire_distance_mm()

    servo.angle = 135
    sleep_ms(1250)
    dist_droite = capteur.lire_distance_mm()

    servo.angle = 90
    sleep_ms(1250) # Attente pour que le servo se stabilise avant de lire les capteurs
    dist_devant = capteur.lire_distance_mm()

    print("Distances lues: ", dist_devant, dist_gauche, dist_droite)
