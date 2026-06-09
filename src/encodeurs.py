"""
Lecture minimale des encodeurs quadrature des deux moteurs FIT0521.

Le Pico compte uniquement les ticks au plus près du matériel. Les valeurs retournées sont
normalisées selon la convention robot :
- positif : la roue contribue à faire avancer le robot ;
- négatif : la roue contribue à faire reculer le robot.
"""

from machine import Pin, disable_irq, enable_irq  # pyright: ignore[reportMissingImports]


GPIO_ENCODEUR_DROIT_A = 12
GPIO_ENCODEUR_DROIT_B = 13 
GPIO_ENCODEUR_GAUCHE_A = 10
GPIO_ENCODEUR_GAUCHE_B = 11

# Ajuster uniquement ces facteurs si un encodeur compte dans le mauvais sens.
FACTEUR_ENCODEUR_GAUCHE = -1
FACTEUR_ENCODEUR_DROITE = 1

IRQ_ENCODEUR = Pin.IRQ_RISING | Pin.IRQ_FALLING

# Table de transition quadrature indexée par : ancien_etat << 2 | nouvel_etat.
TRANSITIONS_QUADRATURE = (
    0, 1, -1, 0,
    -1, 0, 0, 1,
    1, 0, 0, -1,
    0, -1, 1, 0,
)


class EncodeursMoteurs:
    """
    Compte les ticks quadrature des encodeurs gauche et droit.
    """

    def __init__(self):
        """
        Initialise les entrées encodeur et les interruptions.
        """
        self.gauche_a = Pin(GPIO_ENCODEUR_GAUCHE_A, Pin.IN, Pin.PULL_UP)
        self.gauche_b = Pin(GPIO_ENCODEUR_GAUCHE_B, Pin.IN, Pin.PULL_UP)
        self.droite_a = Pin(GPIO_ENCODEUR_DROIT_A, Pin.IN, Pin.PULL_UP)
        self.droite_b = Pin(GPIO_ENCODEUR_DROIT_B, Pin.IN, Pin.PULL_UP)

        self.ticks_gauche = 0
        self.ticks_droite = 0
        self.etat_gauche = self._lire_etat(self.gauche_a, self.gauche_b)
        self.etat_droite = self._lire_etat(self.droite_a, self.droite_b)

        self.gauche_a.irq(trigger=IRQ_ENCODEUR, handler=self._interruption_gauche)
        self.gauche_b.irq(trigger=IRQ_ENCODEUR, handler=self._interruption_gauche)
        self.droite_a.irq(trigger=IRQ_ENCODEUR, handler=self._interruption_droite)
        self.droite_b.irq(trigger=IRQ_ENCODEUR, handler=self._interruption_droite)

    def obtenir_ticks(self):
        """
        Retourne les ticks normalisés des deux roues.
        """
        etat_irq = disable_irq()

        try:
            ticks_gauche = self.ticks_gauche
            ticks_droite = self.ticks_droite
        finally:
            enable_irq(etat_irq)

        return {
            "gauche": ticks_gauche * FACTEUR_ENCODEUR_GAUCHE,
            "droite": ticks_droite * FACTEUR_ENCODEUR_DROITE,
        }

    def remettre_a_zero(self):
        """
        Remet les deux compteurs encodeur à zéro.
        """
        etat_irq = disable_irq()

        try:
            self.ticks_gauche = 0
            self.ticks_droite = 0
            self.etat_gauche = self._lire_etat(self.gauche_a, self.gauche_b)
            self.etat_droite = self._lire_etat(self.droite_a, self.droite_b)
        finally:
            enable_irq(etat_irq)

    def _interruption_gauche(self, broche):
        """
        Met à jour le compteur gauche lors d'un changement sur A ou B.
        """
        etat_actuel = self._lire_etat(self.gauche_a, self.gauche_b)
        index_transition = (self.etat_gauche << 2) | etat_actuel
        self.ticks_gauche += TRANSITIONS_QUADRATURE[index_transition]
        self.etat_gauche = etat_actuel

    def _interruption_droite(self, broche):
        """
        Met à jour le compteur droit lors d'un changement sur A ou B.
        """
        etat_actuel = self._lire_etat(self.droite_a, self.droite_b)
        index_transition = (self.etat_droite << 2) | etat_actuel
        self.ticks_droite += TRANSITIONS_QUADRATURE[index_transition]
        self.etat_droite = etat_actuel

    def _lire_etat(self, broche_a, broche_b):
        """
        Lit les deux phases de l'encodeur sous forme d'état 0..3.
        """
        return (broche_a.value() << 1) | broche_b.value()
