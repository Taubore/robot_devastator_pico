# robot_devastator_pico

Firmware MicroPython du Raspberry Pi Pico / Pico WH pour le projet Devastator.

Le Pico reçoit des commandes texte sur l'UART, contrôle deux moteurs via un driver MDD3A,
lit un capteur ultrason Grove et pilote un servomoteur.

## Structure

- `src/` : fichiers Python destinés au Pico.
- `tools/` : scripts locaux de téléversement et d'essai.
- `.venv/` : environnement Python local attendu pour les outils, non versionné.
- `.vscode/` : configuration VSCode locale si présente.

## Fichiers actuels

- `src/main.py` : point d'entrée du firmware.
- `src/controleur_moteurs.py` : commande PWM des deux moteurs.
- `src/protocole_uart.py` : analyse des commandes texte reçues sur l'UART.
- `src/capteur_ultrason.py` : lecture du Grove Ultrasonic Ranger V2.0.
- `src/servo.py` : commande du servomoteur.
- `src/encodeurs.py` : comptage des ticks quadrature des deux encodeurs moteurs.
- `tools/test_protocole_direct_mpremote.py` : pré-test direct par USB/REPL avec `mpremote`.
- `tools/test_protocole_uart.py` : test final du protocole par l'UART matériel.
- `tools/upload_src_to_pico.py` : copie les fichiers de `src/` vers le Pico avec `mpremote`.

## Matériel

- UART 0 : TX sur GPIO 0, RX sur GPIO 1, 115200 bauds.
- Moteur gauche logique : driver MDD3A sur GPIO 4 et GPIO 5.
- Moteur droit logique : driver MDD3A sur GPIO 2 et GPIO 3.
- Capteur ultrason Grove : SIG sur GPIO 14.
- Servomoteur : signal sur GPIO 15.
- Encodeur gauche logique : A sur GPIO10 (vert), B sur GPIO11 (jaune)
- Encodeur droit logique : A sur GPIO12 (vert), B sur GPIO13 (jaune)

Les noms gauche et droit décrivent la convention logicielle du robot. Cette convention tient
compte du montage actuel, sans inversion physique des connecteurs moteurs ou encodeurs.

Les ticks encodeurs retournés par le Pico suivent la convention du robot :

- valeur positive : la roue contribue à faire avancer le robot ;
- valeur négative : la roue contribue à faire reculer le robot.

Si un encodeur compte dans le mauvais sens, ajuster uniquement les constantes
`FACTEUR_ENCODEUR_GAUCHE` ou `FACTEUR_ENCODEUR_DROITE` dans `src/encodeurs.py`.

### Alimentation
- Important : capteur ultrason Grove alimenté en 3,3 V
- Important : encodeurs alimentés en 3,3V (2 fils bleu et 2 fils noirs sur le GND)

## Démarrage du Pico

Lors de la mise sous tension du Pico et du Raspberry Pi, il faut déconnecter temporairement la
ligne Raspberry Pi TX GPIO14 vers Pico RX GPIO1, car elle peut perturber le démarrage du Pico.

Le démarrage correct est confirmé par 3 clignotements de la LED interne du Pico. Si la LED ne
clignote pas, le démarrage a probablement été perturbé.

Procédure utilisée sur ce montage :

1. Tirer le petit interrupteur vers l'extérieur pendant la mise sous tension.
2. Attendre les 3 clignotements de la LED interne du Pico.
3. Pousser l'interrupteur vers l'intérieur pour réactiver la ligne UART.
4. Vérifier que les voyants du board du Pico pour GPIO 0 et GPIO 1 sont allumés.

Si seul GPIO 0 est allumé, l'état n'est pas correct.

## Protocole UART

Les commandes sont envoyées en texte ASCII, terminées par `\n`, `\r` ou `\r\n`.

Au démarrage, le Pico envoie l'événement spontané :

```text
READY
```

Les réponses de succès suivent ce format :

```text
OK <COMMANDE> [valeurs séparées par un espace...]
```

Les réponses d'erreur suivent ce format :

```text
ERR <CODE>
```

L'arrêt de sécurité par délai sans commande valide envoie l'événement spontané :

```text
AVERT TIMEOUT
```

Commandes disponibles :

- `PING` : teste le lien UART. Retour : `OK PING`.
- `STATUS` : retourne l'état moteur.
  Retour : `OK STATUS <gauche> <droite> <actif>`.
- `STOP_MOT` : arrête les deux moteurs. Retour : `OK STOP_MOT`.
- `SET_MOT <gauche> <droite>` : applique les vitesses moteur de `-1000` à `1000`.
  Retour : `OK SET_MOT <gauche> <droite>`.
- `SET_SERVO <angle>` : positionne le servomoteur entre `0` et `180` degrés.
  Repères actuels : `45` = gauche, `95` = centre, `140` = droite.
  Retour : `OK SET_SERVO <angle>`.
- `SONAR` : retourne la distance ultrason en millimètres.
  Retour : `OK SONAR <distance_mm>`.
  La valeur est plafonnée entre `20` et `3500` mm.
- `ENC` : retourne les ticks encodeurs normalisés.
  Retour : `OK ENC <gauche_ticks> <droite_ticks>`.
- `RESET_ENC` : remet les deux compteurs encodeurs à zéro.
  Retour : `OK RESET_ENC`.

Les anciens noms `STOP`, `SET`, `DIST` et `SERVO` ne sont plus acceptés.

## Déploiement

Le script de téléversement utilise `mpremote` depuis `.venv`.

Exemple depuis la racine du dépôt :

```bash
.venv/bin/python tools/upload_src_to_pico.py
```

# Commandes pratiques MpRemote

```bash
# Pour effacer tout sur le Pico
mpremote connect auto fs -r rm :

# Pour lister tous les fichiers
mpremote connect auto fs tree -h :
```

## Pré-test direct par USB

Le script `tools/test_protocole_direct_mpremote.py` permet de tester une grande partie du
protocole depuis le Lenovo avec `mpremote`, sans passer par l'UART matériel. Il instancie
directement les objets du firmware, analyse les mêmes commandes texte et affiche des réponses au
même format logique.

Les roues doivent être dans le vide, car ce script envoie de courtes commandes moteur.

```bash
.venv/bin/mpremote run tools/test_protocole_direct_mpremote.py
```

Ce pré-test valide rapidement le parseur, les commandes moteur, le capteur ultrason, le servo et
les encodeurs si les roues tournent réellement. Il ne remplace pas le test final du lien UART
entre le Raspberry Pi et le Pico.

## Test UART depuis le Raspberry Pi 4

Le firmware Pico peut être testé depuis le Raspberry Pi par l’UART matériel avec `picocom`.

Connexion utilisée :

- Pico UART0
- Pico TX GPIO0 → Raspberry Pi RX GPIO15
- Pico RX GPIO1 ← Raspberry Pi TX GPIO14
- Pico GPIO10	FIT0521 - Encodeur moteur gauche logique A (Vert)
- Pico GPIO11	FIT0521 - Encodeur moteur gauche logique B (Jaune)
- Pico GPIO12	FIT0521 - Encodeur moteur droit logique A (Vert)
- Pico GPIO13	FIT0521 - Encodeur moteur droit logique B (Jaune)
- GND Pico ↔ GND Raspberry Pi
- Débit : 115200 bauds

Commande de test depuis le Raspberry Pi :

```bash
picocom -b 115200 -c /dev/ttyS0
```

Faire `CTRL+A` puis `CTRL+X` pour quitter.

Séquence manuelle courte, roues dans le vide :

```text
PING
STATUS
SONAR
SET_SERVO 95
RESET_ENC
ENC
SET_MOT 150 150
ENC
STOP_MOT
STATUS
```

Le script `tools/test_protocole_uart.py` exécute un parcours complet du protocole par l'UART
matériel et affiche les réponses à valider visuellement. Les roues doivent être dans le vide,
car il envoie aussi de courtes commandes moteur à vitesse moyenne. Sa séquence visible est
alignée sur le pré-test direct par `mpremote`. Pendant les pauses moteur, il répète
discrètement la commande active afin de respecter l'arrêt de sécurité du firmware sans écourter
le mouvement.

Le Pico étant connecté sur un Raspberry Pi avec les connexion ci-haut mentionné, il faut alors
amorcer une session SSH et copier ce script sur le Raspberry Pi.

```bash
python test_protocole_uart.py
```

Commandes UART utiles pour valider les encodeurs, roues dans le vide :

```text
PING
STATUS
SONAR
SET_SERVO 45
SONAR
SET_SERVO 95
SONAR
SET_SERVO 140
SONAR
SET_SERVO 95
SONAR
RESET_ENC
ENC
SET_MOT 500 500
ENC
ENC
STOP_MOT
SET_MOT -500 -500
ENC
ENC
STOP_MOT
RESET_ENC
ENC
SET_MOT -500 -500
ENC
ENC
STOP_MOT
STATUS
```

En avance, les deux compteurs doivent augmenter. En recul, les deux compteurs doivent diminuer.
Garder les roues hors sol pendant ces essais.
