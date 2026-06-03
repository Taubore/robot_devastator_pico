"""
Parseur du protocole UART en texte ASCII.

Rôle : 
- analyser les lignes de texte reçues sur l'UART
- valider la syntaxe et les arguments en étant permissif avec les espaces et les \r et \n

Exemples :
- PING
- STOP
- STATUS
- SET 300 300
- SET -250 400
- SERVO 95
- DIST
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
    - {"valide": True, "action": "STOP"}
    - {"valide": True, "action": "STATUS"}
    - {"valide": True, "action": "SET", "gauche": ..., "droite": ...}
    - {"valide": True, "action": "DIST"}
    - {"valide": True, "action": "SERVO", "angle": ...}
    - {"valide": True, "action": "ENC"}
    - {"valide": True, "action": "RESET_ENC"}

    Retour possible en cas d'erreur :
    - {"valide": False, "erreur": "..."}
    """
    if ligne is None:
        return _erreur("ligne absente")

    try:
        ligne = normaliser_ligne_commande(ligne)
    except (UnicodeError, ValueError):
        return _erreur("ligne invalide")

    if not ligne:
        return _erreur("ligne vide")

    morceaux = ligne.split()
    commande = morceaux[0].upper()

    if commande == "PING":
        if len(morceaux) != 1:
            return _erreur("PING sans argument")
        return {"valide": True, "action": "PING"}

    if commande == "STOP":
        if len(morceaux) != 1:
            return _erreur("STOP sans argument")
        return {"valide": True, "action": "STOP"}

    if commande == "STATUS":
        if len(morceaux) != 1:
            return _erreur("STATUS sans argument")
        return {"valide": True, "action": "STATUS"}

    if commande == "DIST":
        if len(morceaux) != 1:
            return _erreur("DIST sans argument")
        return {"valide": True, "action": "DIST"}

    if commande == "ENC":
        if len(morceaux) != 1:
            return _erreur("ENC sans argument")
        return {"valide": True, "action": "ENC"}

    if commande == "RESET_ENC":
        if len(morceaux) != 1:
            return _erreur("RESET_ENC sans argument")
        return {"valide": True, "action": "RESET_ENC"}

    if commande == "SERVO":
        if len(morceaux) != 2:
            return _erreur("usage: SERVO <angle>")

        try:
            angle = int(morceaux[1])
        except ValueError:
            return _erreur("angle entier requis")

        if not (SERVO_MIN <= angle <= SERVO_MAX):
            return _erreur(f"angle hors plage [{SERVO_MIN},{SERVO_MAX}]")

        return {
            "valide": True,
            "action": "SERVO",
            "angle": angle,
        }

    if commande == "SET":
        if len(morceaux) != 3:
            return _erreur("usage: SET <gauche> <droite>")

        try:
            gauche = int(morceaux[1])
            droite = int(morceaux[2])
        except ValueError:
            return _erreur("vitesses entières requises")

        if not (VITESSE_MIN <= gauche <= VITESSE_MAX):
            return _erreur(f"gauche hors plage [{VITESSE_MIN},{VITESSE_MAX}]")

        if not (VITESSE_MIN <= droite <= VITESSE_MAX):
            return _erreur(f"droite hors plage [{VITESSE_MIN},{VITESSE_MAX}]")

        return {
            "valide": True,
            "action": "SET",
            "gauche": gauche,
            "droite": droite,
        }

    return _erreur("commande inconnue")


def normaliser_ligne_commande(ligne):
    """
    Normalise une ligne reçue pour tolérer plusieurs styles de fin de ligne.

    Exemples acceptés :
    - "PING\\r\\n"
    - "SET 100 200\\r"
    - b"STATUS\\n"
    - "SET   100   200\\r\\r\\n"
    """
    if isinstance(ligne, bytes):
        ligne = ligne.decode("utf-8")

    if not isinstance(ligne, str):
        ligne = str(ligne)

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
