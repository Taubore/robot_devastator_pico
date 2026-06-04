"""
Test final du protocole par l'UART matériel du firmware Pico.

À lancer depuis le Raspberry Pi relié au Pico par UART. Ce script envoie les commandes texte au
firmware réel, lit les réponses UART et affiche le résultat à valider visuellement.

Les roues doivent être dans le vide, car le test envoie de courtes commandes moteur à vitesse
moyenne.
"""

import argparse
import os
import select
import termios
import time
import tty


PORT_UART_DEFAUT = "/dev/ttyS0"
BAUDRATE_DEFAUT = 115200
DELAI_REPONSE_S = 0.8
DELAI_REPONSE_RAPPEL_S = 0.12
DELAI_SECURITE_DEPART_S = 3.0
DELAI_COMMANDE_S = 0.5
DELAI_MOUVEMENT_S = 1.2
DELAI_OBSERVATION_S = 1.5
INTERVALLE_RAPPEL_MOTEUR_S = 0.25

SEPARATEUR_TEST = "-" * 48

COMMANDES_TEST = (
    "PING",
    "STATUS",
    "SONAR",
    "SET_SERVO 45",
    "SONAR",
    "SET_SERVO 95",
    "SONAR",
    "SET_SERVO 140",
    "SONAR",
    "SET_SERVO 95",
    "SONAR",
    "RESET_ENC",
    "ENC",
    "SET_MOT 500 500",
    "ENC",
    "ENC",
    "STOP_MOT",
    "SET_MOT -500 -500",
    "ENC",
    "ENC",
    "STOP_MOT",
    "RESET_ENC",
    "ENC",
    "SET_MOT -500 -500",
    "ENC",
    "ENC",
    "STOP_MOT",
    "STATUS",
)


def analyser_arguments():
    """
    Lit les options de lancement du script.
    """
    parseur = argparse.ArgumentParser(
        description="Teste visuellement le protocole UART matériel du firmware Pico."
    )
    parseur.add_argument(
        "--port",
        default=PORT_UART_DEFAUT,
        help=f"Port série à utiliser, par défaut {PORT_UART_DEFAUT}.",
    )
    parseur.add_argument(
        "--baudrate",
        type=int,
        default=BAUDRATE_DEFAUT,
        help=f"Débit UART, par défaut {BAUDRATE_DEFAUT}.",
    )
    return parseur.parse_args()


def configurer_uart(descripteur, baudrate):
    """
    Configure le port série avec les outils standards POSIX.
    """
    if baudrate != 115200:
        raise ValueError("seul le débit 115200 est configuré dans ce script")

    tty.setraw(descripteur)

    attributs = termios.tcgetattr(descripteur)
    attributs[4] = termios.B115200
    attributs[5] = termios.B115200
    attributs[2] = attributs[2] | termios.CLOCAL | termios.CREAD
    attributs[2] = attributs[2] & ~termios.CSIZE
    attributs[2] = attributs[2] | termios.CS8
    attributs[2] = attributs[2] & ~termios.PARENB
    attributs[2] = attributs[2] & ~termios.CSTOPB
    attributs[2] = attributs[2] & ~termios.CRTSCTS
    attributs[3] = 0
    attributs[6][termios.VMIN] = 0
    attributs[6][termios.VTIME] = 0

    termios.tcsetattr(descripteur, termios.TCSANOW, attributs)
    termios.tcflush(descripteur, termios.TCIOFLUSH)


def lire_reponses(descripteur, delai_s):
    """
    Lit les lignes reçues pendant un court délai.
    """
    fin_s = time.monotonic() + delai_s
    donnees = bytearray()

    while time.monotonic() < fin_s:
        restant_s = max(0, fin_s - time.monotonic())
        prets, _, _ = select.select([descripteur], [], [], min(0.1, restant_s))

        if not prets:
            continue

        bloc = os.read(descripteur, 256)

        if not bloc:
            continue

        donnees.extend(bloc)

    texte = donnees.decode("utf-8", errors="replace")
    lignes = []

    for ligne in texte.replace("\r", "\n").split("\n"):
        ligne = ligne.strip()

        if ligne:
            lignes.append(ligne)

    return lignes


def envoyer_commande(descripteur, commande):
    """
    Envoie une commande terminée par un saut de ligne.
    """
    os.write(descripteur, (commande + "\n").encode("ascii"))


def obtenir_prefixe_attendu(commande):
    """
    Retourne le préfixe de réponse attendu pour une commande visible du test.
    """
    if commande.startswith("SET_MOT "):
        return "OK " + commande

    if commande.startswith("SET_SERVO "):
        return "OK " + commande

    if commande in ("PING", "STOP_MOT", "RESET_ENC"):
        return "OK " + commande

    if commande in ("STATUS", "SONAR", "ENC"):
        return "OK " + commande

    return ""


def verifier_reponse(lignes, prefixe_attendu):
    """
    Vérifie simplement que la réponse attendue est visible.
    """
    if not prefixe_attendu:
        return bool(lignes)

    for ligne in lignes:
        if ligne.startswith(prefixe_attendu):
            return True

    return False


def afficher_reponse(lignes, prefixe_attendu):
    """
    Affiche la réponse utile avec le même format nominal que le pré-test direct.
    """
    for ligne in lignes:
        if ligne.startswith(prefixe_attendu):
            print(ligne)
            return

    if not lignes:
        print("À VÉRIFIER aucune réponse")
        return

    for ligne in lignes:
        print(ligne)

    print(f"À VÉRIFIER réponse attendue absente : {prefixe_attendu}")


def pause_apres_commande_s(commande):
    """
    Laisse le temps au matériel de réagir, surtout pendant les courts mouvements moteur.
    """
    if commande.startswith("SET_MOT "):
        return DELAI_MOUVEMENT_S

    return DELAI_COMMANDE_S


def attendre_avec_rappel_moteur(descripteur, duree_s, commande_moteur):
    """
    Attend en répétant la commande moteur active pour respecter la sécurité du firmware.
    """
    if not commande_moteur:
        time.sleep(duree_s)
        return

    fin_s = time.monotonic() + duree_s
    prochain_rappel_s = time.monotonic() + INTERVALLE_RAPPEL_MOTEUR_S

    while time.monotonic() < fin_s:
        maintenant_s = time.monotonic()

        if maintenant_s >= prochain_rappel_s:
            envoyer_commande(descripteur, commande_moteur)
            lire_reponses(descripteur, DELAI_REPONSE_RAPPEL_S)
            prochain_rappel_s = time.monotonic() + INTERVALLE_RAPPEL_MOTEUR_S
            continue

        attente_s = min(0.05, max(0, prochain_rappel_s - maintenant_s))
        time.sleep(attente_s)

    lire_reponses(descripteur, DELAI_REPONSE_RAPPEL_S)


def executer_tests(port, baudrate):
    """
    Exécute le parcours de test complet du protocole.
    """
    print("Test final du protocole par UART matériel.")
    print("Roues dans le vide requises. Départ dans 3 secondes.")
    time.sleep(DELAI_SECURITE_DEPART_S)

    descripteur = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    commande_moteur = None

    try:
        configurer_uart(descripteur, baudrate)
        lire_reponses(descripteur, DELAI_REPONSE_S)

        for commande in COMMANDES_TEST:
            print(SEPARATEUR_TEST)
            print(f"> {commande}", flush=True)

            envoyer_commande(descripteur, commande)
            lignes = lire_reponses(descripteur, DELAI_REPONSE_S)
            prefixe_attendu = obtenir_prefixe_attendu(commande)
            afficher_reponse(lignes, prefixe_attendu)

            if verifier_reponse(lignes, prefixe_attendu):
                if commande.startswith("SET_MOT "):
                    commande_moteur = commande
                elif commande == "STOP_MOT":
                    commande_moteur = None

            attendre_avec_rappel_moteur(
                descripteur,
                pause_apres_commande_s(commande) + DELAI_OBSERVATION_S,
                commande_moteur,
            )

    finally:
        print(SEPARATEUR_TEST)
        envoyer_commande(descripteur, "STOP_MOT")
        afficher_reponse(lire_reponses(descripteur, DELAI_REPONSE_S), "OK STOP_MOT")
        print("Test terminé.")
        os.close(descripteur)


def main():
    """
    Point d'entrée du script.
    """
    arguments = analyser_arguments()

    executer_tests(arguments.port, arguments.baudrate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
