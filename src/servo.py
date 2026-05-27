"""
Pour faciliter les mouvements d'un servomoteur.
"""
from machine import PWM # pyright: ignore[reportMissingImports]

class Servo:

    def __init__(self, gpio_sig: int):
        self.s = PWM(gpio_sig)
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
        assert 0 <= degrees <= 180, "Angle doit être entre 0 et 180 degrés"
        self._angle = int(degrees)
        # Convertir l'angle en durée de signal (en nanosecondes)
        ns = 500000 + 2000000/180 * self._angle
        self.s.duty_ns(int(ns))
