"""
Pré-test direct du protocole par USB/REPL avec mpremote.

Ce script ne passe pas par l'UART matériel. Il est lancé avec mpremote depuis l'ordinateur,
instancie les mêmes objets matériels que le firmware, analyse les mêmes commandes texte, puis
appelle directement les actions correspondantes.

Les roues doivent être dans le vide, car le test envoie de courtes commandes moteur prudentes.
"""

from time import sleep_ms  # pyright: ignore[reportAttributeAccessIssue]

from capteur_ultrason import CapteurUltrason
from controleur_moteurs import ControleurMoteurs
from encodeurs import EncodeursMoteurs
from protocole_uart import analyser_commande
from servo import Servo


CAPTEUR_ULTRASON_GPIO = 14
SERVOMOTEUR_GPIO = 15

DELAI_SECURITE_DEPART_MS = 3000
DELAI_COMMANDE_MS = 500
DELAI_MOUVEMENT_MS = 1200
DELAI_OBSERVATION_MS = 1500

SEPARATEUR_TEST = "-" * 48

COMMANDES_TEST = (
    "PING",
    "STATUS",
    "DIST",
    "SERVO 45",
    "SERVO 95",
    "SERVO 140",
    "SERVO 95",
    "RESET_ENC",
    "ENC",
    "SET 150 150",
    "ENC",
    "ENC",
    "STOP",
    "SET -150 -150",
    "ENC",
    "ENC",
    "STOP",
    "RESET_ENC",
    "ENC",
    "STATUS",
)


def repondre(message):
    """
    Affiche une réponse au même format logique que le protocole UART.
    """
    print(message)


def traiter_commande_directe(commande_texte, controleur, capteur_ultrason, servomoteur, encodeurs):
    """
    Analyse une commande texte et appelle directement les objets matériels concernés.
    """
    commande = analyser_commande(commande_texte)

    if not commande["valide"]:
        repondre("ERREUR : " + commande["erreur"])
        return

    action = commande["action"]

    if action == "PING":
        repondre("PONG")
        return

    if action == "STOP":
        controleur.arreter()
        repondre("OK STOP")
        return

    if action == "SET":
        gauche = commande["gauche"]
        droite = commande["droite"]
        controleur.definir_vitesses(gauche, droite)
        repondre("OK SET {} {}".format(gauche, droite))
        return

    if action == "STATUS":
        etat = controleur.obtenir_etat()
        repondre(
            "OK STATUS gauche={} droite={} actif={}".format(
                etat["gauche"],
                etat["droite"],
                etat["actif"],
            )
        )
        return

    if action == "DIST":
        repondre(str(capteur_ultrason.lire_distance_mm()))
        return

    if action == "SERVO":
        servomoteur.angle = commande["angle"]
        repondre("OK SERVO")
        return

    if action == "ENC":
        ticks = encodeurs.obtenir_ticks()
        repondre("OK ENC gauche={} droite={}".format(ticks["gauche"], ticks["droite"]))
        return

    if action == "RESET_ENC":
        encodeurs.remettre_a_zero()
        repondre("OK RESET_ENC")
        return

    repondre("ERREUR : action inconnue")


def pause_apres_commande(commande_texte):
    """
    Laisse le temps au matériel de réagir, surtout pendant les courts mouvements moteur.
    """
    if commande_texte.startswith("SET "):
        sleep_ms(DELAI_MOUVEMENT_MS)
        return

    sleep_ms(DELAI_COMMANDE_MS)


def main():
    """
    Exécute la séquence de test directe.
    """
    print("Pré-test direct du protocole par mpremote.")
    print("Roues dans le vide requises. Départ dans 3 secondes.")
    sleep_ms(DELAI_SECURITE_DEPART_MS)

    controleur = ControleurMoteurs()
    capteur_ultrason = CapteurUltrason(CAPTEUR_ULTRASON_GPIO)
    servomoteur = Servo(SERVOMOTEUR_GPIO)
    encodeurs = EncodeursMoteurs()

    controleur.arreter()

    try:
        for commande_texte in COMMANDES_TEST:
            print(SEPARATEUR_TEST)
            print("> " + commande_texte)
            traiter_commande_directe(
                commande_texte,
                controleur,
                capteur_ultrason,
                servomoteur,
                encodeurs,
            )
            pause_apres_commande(commande_texte)
            sleep_ms(DELAI_OBSERVATION_MS)

    finally:
        print(SEPARATEUR_TEST)
        controleur.arreter()
        print("OK STOP")
        print("Test terminé.")


main()
