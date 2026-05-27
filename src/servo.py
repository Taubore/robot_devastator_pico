"""
Pour faciliter les mouvements d'un servomoteur.
"""
from machine import Pin, PWM # pyright: ignore[reportMissingImports]


IMPULSION_MIN_NS = 500000
IMPULSION_MAX_NS = 2500000
ANGLE_MIN = 0
ANGLE_MAX = 180


class Servo:

    def __init__(self, gpio_sig: int):
        self.s = PWM(Pin(gpio_sig))
        self.s.freq(50)
        self._angle = None
        self.detach()

    def detach(self):
        # Désactiver l'asservissement en mettant le signal à 0
        self.s.duty_ns(0)

    def attach(self):
        # Activer l'asservissement au dernier angle connu
        if self._angle is not None:
            self.angle = self._angle

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, degrees):
        if not (ANGLE_MIN <= degrees <= ANGLE_MAX):
            raise ValueError("Angle doit être entre 0 et 180 degrés")

        self._angle = int(degrees)

        # Convertir l'angle en durée de signal (en nanosecondes)
        largeur_plage_ns = IMPULSION_MAX_NS - IMPULSION_MIN_NS
        ns = IMPULSION_MIN_NS + largeur_plage_ns * self._angle // ANGLE_MAX
        self.s.duty_ns(int(ns))
