"""
Contrôleur des deux moteurs via le driver MDD3A.

Rôle :
- initialiser les sorties PWM pour les moteurs
- appliquer des consignes de vitesse à gauche et à droite  

Convention :
- vitesse positive  -> avance  -> PWM sur A, B à 0
- vitesse négative  -> recul   -> A à 0, PWM sur B
- vitesse nulle     -> arrêt   -> A à 0, B à 0
"""

from machine import Pin, PWM


class ControleurMoteurs:
    """
    Gère les deux moteurs en sortie PWM.
    """

    # GPIO validés pour le projet
    GPIO_GAUCHE_A = 2
    GPIO_GAUCHE_B = 3
    GPIO_DROITE_A = 4
    GPIO_DROITE_B = 5

    # Fréquence PWM actuelle retenue
    FREQUENCE_PWM_HZ = 1000

    # Échelle logique choisie pour les consignes
    VITESSE_MIN = -1000
    VITESSE_MAX = 1000

    def __init__(self):
        """
        Initialise les sorties PWM des quatre lignes de commande.
        """
        self.pwm_gauche_a = PWM(Pin(self.GPIO_GAUCHE_A))
        self.pwm_gauche_b = PWM(Pin(self.GPIO_GAUCHE_B))
        self.pwm_droite_a = PWM(Pin(self.GPIO_DROITE_A))
        self.pwm_droite_b = PWM(Pin(self.GPIO_DROITE_B))

        self.pwm_gauche_a.freq(self.FREQUENCE_PWM_HZ)
        self.pwm_gauche_b.freq(self.FREQUENCE_PWM_HZ)
        self.pwm_droite_a.freq(self.FREQUENCE_PWM_HZ)
        self.pwm_droite_b.freq(self.FREQUENCE_PWM_HZ)

        # On mémorise les dernières consignes demandées
        self.vitesse_gauche = 0
        self.vitesse_droite = 0
        self.actif = False

        # Toujours démarrer à l'arrêt
        self.arreter()

    def definir_vitesses(self, gauche, droite):
        """
        Applique les vitesses demandées aux deux moteurs.

        Paramètres :
        - gauche : entier de -1000 à 1000
        - droite : entier de -1000 à 1000
        """
        gauche = self._borner_vitesse(gauche)
        droite = self._borner_vitesse(droite)

        self._appliquer_moteur(
            pwm_a=self.pwm_gauche_a,
            pwm_b=self.pwm_gauche_b,
            vitesse=gauche
        )

        self._appliquer_moteur(
            pwm_a=self.pwm_droite_a,
            pwm_b=self.pwm_droite_b,
            vitesse=droite
        )

        self.vitesse_gauche = gauche
        self.vitesse_droite = droite
        self.actif = (gauche != 0 or droite != 0)

    def arreter(self):
        """
        Force l'arrêt complet des deux moteurs.
        """
        self._mettre_pwm_a_zero(self.pwm_gauche_a)
        self._mettre_pwm_a_zero(self.pwm_gauche_b)
        self._mettre_pwm_a_zero(self.pwm_droite_a)
        self._mettre_pwm_a_zero(self.pwm_droite_b)

        self.vitesse_gauche = 0
        self.vitesse_droite = 0
        self.actif = False

    def est_actif(self):
        """
        Indique si au moins un moteur est commandé.
        """
        return self.actif

    def obtenir_etat(self):
        """
        Retourne un résumé simple de l'état interne.
        """
        return {
            "gauche": self.vitesse_gauche,
            "droite": self.vitesse_droite,
            "actif": 1 if self.actif else 0,
        }

    def _appliquer_moteur(self, pwm_a, pwm_b, vitesse):
        """
        Applique la convention de commande à un moteur :

        - vitesse > 0  : PWM sur A, B = 0
        - vitesse < 0  : A = 0, PWM sur B
        - vitesse = 0  : A = 0, B = 0
        """
        if vitesse > 0:
            duty = self._convertir_vitesse_en_duty_u16(vitesse)
            pwm_a.duty_u16(duty)
            pwm_b.duty_u16(0)
            return

        if vitesse < 0:
            duty = self._convertir_vitesse_en_duty_u16(-vitesse)
            pwm_a.duty_u16(0)
            pwm_b.duty_u16(duty)
            return

        pwm_a.duty_u16(0)
        pwm_b.duty_u16(0)

    def _borner_vitesse(self, vitesse):
        """
        Force une vitesse dans la plage autorisée.

        Cette méthode tolère aussi des entrées texte ou bytes avec des
        espaces et fins de ligne parasites, ce qui aide lors de tests
        manuels ou REPL.
        """
        vitesse = self._normaliser_vitesse_entree(vitesse)

        if vitesse < self.VITESSE_MIN:
            return self.VITESSE_MIN

        if vitesse > self.VITESSE_MAX:
            return self.VITESSE_MAX

        return int(vitesse)

    def _normaliser_vitesse_entree(self, vitesse):
        """
        Convertit une vitesse reçue en entier exploitable.
        """
        if isinstance(vitesse, bytes):
            vitesse = vitesse.decode("utf-8")

        if isinstance(vitesse, str):
            vitesse = vitesse.replace("\r", " ").replace("\n", " ").strip()

            if not vitesse:
                raise ValueError("vitesse vide")

        return int(vitesse)

    def _convertir_vitesse_en_duty_u16(self, vitesse_absolue):
        """
        Convertit une vitesse de 0..1000 en duty cycle 0..65535.
        """
        vitesse_absolue = max(0, min(self.VITESSE_MAX, int(vitesse_absolue)))
        return (vitesse_absolue * 65535) // self.VITESSE_MAX

    def _mettre_pwm_a_zero(self, pwm):
        """
        Petite fonction utilitaire pour expliciter l'arrêt d'une sortie PWM.
        """
        pwm.duty_u16(0)
