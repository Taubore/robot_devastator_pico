"""
Parseur du protocole UART en texte ASCII.

Rôle : 
- analyser les lignes de texte reçues sur l'UART
- valider la syntaxe et les arguments en étant permissif avec les espaces et les \r et \n

Exemples :
- PING
- STOP_MOT
- STATUS
- SET_MOT 300 300
- SET_MOT -250 400
- SET_SERVO 95
- SONAR
- ENC
- RESET_ENC
"""

VITESSE_MIN = -1000
VITESSE_MAX = 1000

SERVO_MIN = 0
SERVO_MAX = 180

def analyser_commande(ligne):
    """
    Analyse une ligne texte et retourne un dictionnaire structuré.

    Retour possible en cas de succès :
    - {"valide": True, "action": "PING"}
    - {"valide": True, "action": "STOP_MOT"}
    - {"valide": True, "action": "STATUS"}
    - {"valide": True, "action": "SET_MOT", "gauche": ..., "droite": ...}
    - {"valide": True, "action": "SONAR"}
    - {"valide": True, "action": "SET_SERVO", "angle": ...}
    - {"valide": True, "action": "ENC"}
    - {"valide": True, "action": "RESET_ENC"}

    Retour possible en cas d'erreur :
    - {"valide": False, "erreur": "CODE"}
    """
    if ligne is None:
        return _erreur("LIGNE")

    try:
        ligne = normaliser_ligne_commande(ligne)
    except (UnicodeError, ValueError):
        return _erreur("ENCODAGE")

    if not ligne:
        return _erreur("LIGNE")

    morceaux = ligne.split()
    commande = morceaux[0].upper()

    if commande == "PING":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "PING"}

    if commande == "STOP_MOT":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "STOP_MOT"}

    if commande == "STATUS":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "STATUS"}

    if commande == "SONAR":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "SONAR"}

    if commande == "ENC":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "ENC"}

    if commande == "RESET_ENC":
        if len(morceaux) != 1:
            return _erreur("ARG")
        return {"valide": True, "action": "RESET_ENC"}

    if commande == "SET_SERVO":
        if len(morceaux) != 2:
            return _erreur("ARG")

        try:
            angle = int(morceaux[1])
        except ValueError:
            return _erreur("ENTIER")

        if not (SERVO_MIN <= angle <= SERVO_MAX):
            return _erreur("PLAGE")

        return {
            "valide": True,
            "action": "SET_SERVO",
            "angle": angle,
        }

    if commande == "SET_MOT":
        if len(morceaux) != 3:
            return _erreur("ARG")

        try:
            gauche = int(morceaux[1])
            droite = int(morceaux[2])
        except ValueError:
            return _erreur("ENTIER")

        if not (VITESSE_MIN <= gauche <= VITESSE_MAX):
            return _erreur("PLAGE")

        if not (VITESSE_MIN <= droite <= VITESSE_MAX):
            return _erreur("PLAGE")

        return {
            "valide": True,
            "action": "SET_MOT",
            "gauche": gauche,
            "droite": droite,
        }

    return _erreur("COMMANDE")


def normaliser_ligne_commande(ligne):
    """
    Normalise une ligne reçue pour tolérer plusieurs styles de fin de ligne.

    Exemples acceptés :
    - "PING\\r\\n"
    - "SET_MOT 100 200\\r"
    - b"STATUS\\n"
    - "SET_MOT   100   200\\r\\r\\n"
    """
    if isinstance(ligne, bytes):
        ligne = ligne.decode("ascii")

    if not isinstance(ligne, str):
        ligne = str(ligne)

    ligne.encode("ascii")

    ligne = ligne.replace("\x00", "")
    ligne = ligne.replace("\r", " ")
    ligne = ligne.replace("\n", " ")

    return " ".join(ligne.split())


def _erreur(message):
    """
    Uniformise les réponses d'erreur du parseur.
    """
    return {
        "valide": False,
        "erreur": message,
    }
