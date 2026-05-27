"""
Point d'entrée du Pico.

Objectif : contrôler le matériel connecté au Pico à partir de commandes reçues sur l'UART. Lorsque 
l'initialisation du programme dans le Pico est convenablement initialisé, une transmission de READY est
faite sur l'UART.

Commandes supportées : 

PING
- Tester le lien UART. 
- Retour : PONG

SET -9999 -9999
- Enregistrer la vitesse des moteurs gauche et droit.
- Valeurs comprises entre -1000 et 1000
- Retour : OK SET 9999 9999

STATUS
- Demande le statut des moteurs
- Retour : OK STATUS gauche=9999 droite=9999 actif=9
- gauche et droite représente la vitesse et actif indique 1 si actif sinon 0

STOP
- Stopper les deux moteurs rapidement. 
- Retour : OK STOP

DIST
- Retour la distance en mm lue à partir du capteur ultrason
- Retour : 999

SERVO 999
- Positionne le servo moteur à l'angle voulu
- Valeurs comprises entre 45 et 135. Le centre est à 90.
- RETOUR : OK SERVO

Rôle :
- initialiser l'UART
- initialiser le contrôleur moteurs
- lire les commandes texte reçues
- appliquer les commandes valides
- déclencher un arrêt de sécurité si plus aucune commande valide n'arrive
"""

from machine import Pin, UART # pyright: ignore[reportMissingImports]
import time

from controleur_moteurs import ControleurMoteurs
from protocole_uart import analyser_commande


# ============================================================================
# Paramètres matériels et de communication
# ============================================================================

# GPIO
UART_TX_GPIO = 0
UART_RX_GPIO = 1
CAPTEUR_ULTRASON_GPIO = 14
SERVOMOTEUR_GPIO = 15

UART_ID = 0
UART_BAUDRATE = 115200

# Délai maximal sans commande valide avant arrêt de sécurité
DELAI_SECURITE_MS = 500

# Petite pause de boucle pour éviter de tourner inutilement trop vite
PAUSE_BOUCLE_MS = 5

# Longueur maximale tolérée pour une commande texte reçue
LONGUEUR_MAX_LIGNE_UART = 64


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def clignoter_led_depart():
    """
    Fait clignoter la LED intégrée 3 fois pour confirmer que le Pico démarre.
    """
    led = Pin("LED", Pin.OUT)

    for _ in range(3):
        led.on()
        time.sleep_ms(200)
        led.off()
        time.sleep_ms(200)

def envoyer_reponse(uart, message):
    """
    Envoie une réponse texte avec terminaison CRLF, plus compatible avec les
    terminaux série et les outils de test.
    """
    uart.write(message + "\r\n")


def extraire_lignes_uart(donnees, tampon_ligne, separateur_precedent, ligne_en_rejet):
    """
    Assemble les lignes UART en tolérant :
    - \\n
    - \\r
    - \\r\\n
    - \\n\\r
    - répétitions du type \\r\\r\\n

    Retourne :
    - la liste des lignes complètes extraites
    - le tampon de ligne mis à jour
    - l'état mis à jour du séparateur précédent
    - l'état mis à jour d'une ligne en cours de rejet
    - True si une ligne a été rejetée car trop longue
    """
    lignes = []
    ligne_trop_longue = False

    for octet in donnees:
        if octet in (10, 13):
            if separateur_precedent:
                continue

            separateur_precedent = True

            if ligne_en_rejet:
                ligne_en_rejet = False
                ligne_trop_longue = True
                continue

            if tampon_ligne:
                lignes.append(bytes(tampon_ligne))
                tampon_ligne = bytearray()

            continue

        separateur_precedent = False

        if ligne_en_rejet:
            continue

        if len(tampon_ligne) >= LONGUEUR_MAX_LIGNE_UART:
            tampon_ligne = bytearray()
            ligne_en_rejet = True
            continue

        tampon_ligne.append(octet)

    return lignes, tampon_ligne, separateur_precedent, ligne_en_rejet, ligne_trop_longue


def traiter_ligne(uart, controleur, ligne):
    """
    Analyse une ligne reçue et applique l'action correspondante.

    Retourne :
    - True si la commande est valide
    - False si la commande est invalide
    """
    commande = analyser_commande(ligne)
    
    if not commande["valide"]:
        envoyer_reponse(uart, f"ERREUR : {commande['erreur']}")
        return False

    action = commande["action"]

    if action == "PING":
        envoyer_reponse(uart, "PONG")
        return True

    if action == "STOP":
        controleur.arreter()
        envoyer_reponse(uart, "OK STOP")
        return True

    if action == "SET":
        gauche = commande["gauche"]
        droite = commande["droite"]
        controleur.definir_vitesses(gauche, droite)
        envoyer_reponse(uart, f"OK SET {gauche} {droite}")
        return True

    if action == "STATUS":
        etat = controleur.obtenir_etat()
        envoyer_reponse(
            uart,
            "OK STATUS "
            f"gauche={etat['gauche']} "
            f"droite={etat['droite']} "
            f"actif={etat['actif']}"
        )
        return True

    envoyer_reponse(uart, "ERREUR : action inconnue")
    return False


# ============================================================================
# Programme principal
# ============================================================================

def main():
    """
    Boucle principale du programme.
    """

    # Signal de démarrage : clignotement de la LED intégrée
    clignoter_led_depart()

    uart = UART(
        UART_ID,
        baudrate=UART_BAUDRATE,
        tx=Pin(UART_TX_GPIO),
        rx=Pin(UART_RX_GPIO),
    )

    controleur = ControleurMoteurs()

    # Par sécurité, on force explicitement l'arrêt au démarrage
    controleur.arreter()

    # Horodatage de la dernière commande valide reçue
    dernier_message_valide_ms = time.ticks_ms()

    # Tampon de réception des octets UART
    tampon_reception = bytearray()
    dernier_octet_etait_separateur = False
    ligne_uart_en_rejet = False

    print("Système prêt. En attente de commandes sur l'UART...")
    envoyer_reponse(uart, "READY")

    while True:
        # --------------------------------------------------------------------
        # 1) Lire ce qui arrive sur l'UART
        # --------------------------------------------------------------------
        donnees = uart.read()

        if donnees:
            print("UART RX:", donnees)
            lignes_brutes, tampon_reception, dernier_octet_etait_separateur, ligne_uart_en_rejet, ligne_trop_longue = extraire_lignes_uart(
                donnees,
                tampon_reception,
                dernier_octet_etait_separateur,
                ligne_uart_en_rejet
            )

            if ligne_trop_longue:
                envoyer_reponse(uart, "ERREUR : ligne trop longue")

            for ligne_brute in lignes_brutes:
                try:
                    ligne = ligne_brute.decode("utf-8")
                except UnicodeError:
                    envoyer_reponse(uart, "ERREUR : encodage invalide")
                    continue

                commande_valide = traiter_ligne(uart, controleur, ligne)

                if commande_valide:
                    dernier_message_valide_ms = time.ticks_ms()

        # --------------------------------------------------------------------
        # 2) Sécurité : arrêt si plus aucune commande valide depuis trop longtemps
        # --------------------------------------------------------------------
        maintenant_ms = time.ticks_ms()
        duree_sans_commande_ms = time.ticks_diff(maintenant_ms, dernier_message_valide_ms)

        if duree_sans_commande_ms > DELAI_SECURITE_MS:
            if controleur.est_actif():
                print("Aucune commande valide depuis", duree_sans_commande_ms, "ms. Arrêt de sécurité déclenché.")
                controleur.arreter()
                envoyer_reponse(uart, "WARN TIMEOUT STOP")

            # On remet la référence à maintenant pour éviter de spammer le message
            dernier_message_valide_ms = maintenant_ms

        time.sleep_ms(PAUSE_BOUCLE_MS)


# Lancement du programme
main()
