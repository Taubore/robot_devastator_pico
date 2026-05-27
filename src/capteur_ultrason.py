"""
Module pour le capteur ultrasonique Grove Ultrasonic Ranger V2.0.
Le capteur renvoie une impulsion dont la durée est proportionnelle à la distance (58 us/cm).
Son maximum est de 350 cm * 58 us/cm = environ 20300 us.
"""
from machine import Pin, time_pulse_us  # pyright: ignore[reportMissingImports]
from time import sleep_ms, sleep_us     # pyright: ignore[reportAttributeAccessIssue]

# Plage du Grove Ultrasonic Ranger : 2 à 350 cm.
DISTANCE_MIN_MM = 20
DISTANCE_MAX_MM = 3500

# 30000 us garde une marge sans bloquer trop longtemps si le capteur est défectueux ou
# si l'écho est perdu.
TIMEOUT_ECHO_US = 30000


class CapteurUltrason:
    """Capteur Grove Ultrasonic Ranger V2.0 sur une seule broche SIG."""

    def __init__(self, gpio_sig: int):
        self.broche_sig = Pin(gpio_sig, Pin.OUT)
        self.broche_sig.value(0)
        sleep_ms(50)

    def lire_distance_mm(self) -> int:
        """
        Retourne la distance en mm.

        La valeur est plafonnée entre 20 mm et 3500 mm, soit les limites du capteur.
        Retourne 3500 mm si aucune impulsion d'écho valide n'est reçue avant le délai.
        """

        # État bas de stabilisation avant le déclenchement.
        self.broche_sig.init(Pin.OUT)
        self.broche_sig.value(0)
        sleep_us(2)

        # Impulsion de déclenchement supérieure à 10 us.
        self.broche_sig.value(1)
        sleep_us(12)
        self.broche_sig.value(0)

        # La même broche sert ensuite à lire la largeur de l'écho.
        self.broche_sig.init(Pin.IN)

        duree_echo_us = time_pulse_us(self.broche_sig, 1, TIMEOUT_ECHO_US)

        # La fonction time_pulse_us retourne une valeur négative si le délai est dépassé ou
        # si une erreur survient. On considère dans ce cas que cela correspond à une distance
        # maximale.
        if duree_echo_us <= 0:
            return DISTANCE_MAX_MM

        distance_mm = duree_echo_us * 10 // 58

        # Plafonnement utile pour éviter de propager des valeurs hors plage.
        if distance_mm < DISTANCE_MIN_MM:
            return DISTANCE_MIN_MM

        if distance_mm > DISTANCE_MAX_MM:
            return DISTANCE_MAX_MM

        return distance_mm
