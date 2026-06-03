"""
Test final du protocole par l'UART matériel du firmware Pico.

À lancer depuis le Raspberry Pi relié au Pico par UART. Ce script envoie les commandes texte au
firmware réel, lit les réponses UART et affiche le résultat à valider visuellement.

Les roues doivent être dans le vide, car le test envoie de courtes commandes moteur prudentes.
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
PAUSE_COMMANDE_S = 0.4
PAUSE_OBSERVATION_S = 1.5

SEPARATEUR_TEST = "-" * 48

COMMANDES_TEST = (
    ("PING", "OK PING"),
    ("STATUS", "OK STATUS"),
    ("SONAR", "OK SONAR"),
    ("SET_SERVO 45", "OK SET_SERVO 45"),
    ("SET_SERVO 95", "OK SET_SERVO 95"),
    ("SET_SERVO 140", "OK SET_SERVO 140"),
    ("SET_SERVO 95", "OK SET_SERVO 95"),
    ("RESET_ENC", "OK RESET_ENC"),
    ("ENC", "OK ENC"),
    ("SET_MOT 150 150", "OK SET_MOT 150 150"),
    ("ENC", "OK ENC"),
    ("ENC", "OK ENC"),
    ("STOP_MOT", "OK STOP_MOT"),
    ("SET_MOT -150 -150", "OK SET_MOT -150 -150"),
    ("ENC", "OK ENC"),
    ("ENC", "OK ENC"),
    ("STOP_MOT", "OK STOP_MOT"),
    ("RESET_ENC", "OK RESET_ENC"),
    ("ENC", "OK ENC"),
    ("STATUS", "OK STATUS"),
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


def executer_tests(port, baudrate):
    """
    Exécute le parcours de test complet du protocole.
    """
    descripteur = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)

    try:
        configurer_uart(descripteur, baudrate)
        lignes_depart = lire_reponses(descripteur, DELAI_REPONSE_S)

        if lignes_depart:
            print("Réponses déjà présentes :")
            for ligne in lignes_depart:
                print(f"  {ligne}")

        for commande, prefixe_attendu in COMMANDES_TEST:
            print(SEPARATEUR_TEST)
            print(f"> {commande}", flush=True)

            envoyer_commande(descripteur, commande)
            time.sleep(PAUSE_COMMANDE_S)
            lignes = lire_reponses(descripteur, DELAI_REPONSE_S)
            etat = "OK" if verifier_reponse(lignes, prefixe_attendu) else "À VÉRIFIER"

            if lignes:
                for ligne in lignes:
                    print(f"  {ligne}")
            else:
                print("  aucune réponse")

            print(f"  résultat : {etat}\n")
            time.sleep(PAUSE_OBSERVATION_S)

    finally:
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
