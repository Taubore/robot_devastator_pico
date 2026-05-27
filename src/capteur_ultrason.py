from machine import Pin, time_pulse_us  # pyright: ignore[reportMissingImports]
from time import sleep_ms, sleep_us     # pyright: ignore[reportAttributeAccessIssue]


class CapteurUltrason:
    """Capteur Grove Ultrasonic Ranger V2.0 sur une seule broche SIG."""

    def __init__(self, gpio_sig: int):
        self.broche_sig = Pin(gpio_sig, Pin.OUT)
        self.broche_sig.value(0)
        sleep_ms(50)

    def lire_distance_mm(self) -> int | None:
        """Retourne la distance en mm, ou None si aucune mesure valide."""
        # État bas de stabilisation
        self.broche_sig.init(Pin.OUT)
        self.broche_sig.value(0)
        sleep_us(2)

        # Impulsion de déclenchement > 10 us
        self.broche_sig.value(1)
        sleep_us(12)
        self.broche_sig.value(0)

        # Passage en entrée pour lire l'écho
        self.broche_sig.init(Pin.IN)

        try:
            # Timeout 30 ms ≈ > 5 m, largement suffisant pour ce capteur
            duree_echo_us = time_pulse_us(self.broche_sig, 1, 30000)
        except OSError:
            return None

        if duree_echo_us <= 0:
            return None

        # Approximation standard pour capteurs ultrasoniques :
        # distance_cm = duree_echo_us / 58
        distance_mm = duree_echo_us * 10 // 58

        # Filtre minimal de plausibilité pour cette étape
        if distance_mm < 10 or distance_mm > 4500:
            return None

        return distance_mm
