"""
Commande simple d'un servomoteur avec une sortie PWM du Pico.

Le servo reçoit un signal à 50 Hz. La largeur de l'impulsion indique l'angle demandé :
- environ 0,5 ms pour 0 degré ;
- environ 2,5 ms pour 180 degrés.
"""
from machine import Pin, PWM # pyright: ignore[reportMissingImports]


# Largeur minimale et maximale de l'impulsion de commande du servo.
IMPULSION_MIN_NS = 500000
IMPULSION_MAX_NS = 2500000

ANGLE_MIN = 0
ANGLE_MAX = 180


class Servo:
    """
    Représente un servomoteur branché sur une broche GPIO.

    L'angle est exposé comme une propriété pour pouvoir écrire simplement :
    servo.angle = 95
    """

    def __init__(self, gpio_sig: int):
        """
        Prépare la PWM, puis coupe le signal pour éviter un mouvement au démarrage.
        """
        self.s = PWM(Pin(gpio_sig))
        self.s.freq(50)
        self._angle = None
        self.detach()

    def detach(self):
        """
        Désactive l'asservissement en mettant le signal PWM à 0.
        """
        self.s.duty_ns(0)

    def attach(self):
        """
        Réactive l'asservissement au dernier angle connu.
        """
        if self._angle is not None:
            self.angle = self._angle

    @property
    def angle(self):
        """
        Retourne le dernier angle demandé, ou None si aucun angle n'a été demandé.
        """
        return self._angle

    @angle.setter
    def angle(self, degrees):
        """
        Demande un nouvel angle au servo.
        """
        if not (ANGLE_MIN <= degrees <= ANGLE_MAX):
            raise ValueError("L'angle doit être entre 0 et 180 degrés")

        self._angle = int(degrees)

        # Conversion linéaire : 0..180 degrés devient 0,5..2,5 ms.
        largeur_plage_ns = IMPULSION_MAX_NS - IMPULSION_MIN_NS
        ns = IMPULSION_MIN_NS + largeur_plage_ns * self._angle // ANGLE_MAX
        self.s.duty_ns(int(ns))
