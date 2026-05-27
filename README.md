# robot_devastator_pico

Firmware MicroPython du Raspberry Pi Pico / Pico WH pour le projet Devastator.

Le Pico reçoit des commandes texte sur l'UART, contrôle deux moteurs via un driver MDD3A,
lit un capteur ultrason Grove et pilote un servomoteur.

## Structure

- `src/` : fichiers Python destinés au Pico.
- `tools/` : scripts locaux de téléversement.
- `.venv/` : environnement Python local attendu pour les outils, non versionné.
- `.vscode/` : configuration VSCode locale si présente.

## Fichiers actuels

- `src/main.py` : point d'entrée du firmware.
- `src/controleur_moteurs.py` : commande PWM des deux moteurs.
- `src/protocole_uart.py` : analyse des commandes texte reçues sur l'UART.
- `src/capteur_ultrason.py` : lecture du Grove Ultrasonic Ranger V2.0.
- `src/servo.py` : commande du servomoteur.
- `src/test.py` : script pratique pour tester rapidement le servo et le capteur ultrason.
- `tools/upload_src_to_pico.py` : copie les fichiers de `src/` vers le Pico avec `mpremote`.

## Matériel

- UART 0 : TX sur GPIO 0, RX sur GPIO 1, 115200 bauds.
- Moteurs : driver MDD3A sur GPIO 2 à 5.
- Capteur ultrason Grove : SIG sur GPIO 14.
- Servomoteur : signal sur GPIO 15.

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

- `PING` : teste le lien UART. Retour : `PONG`.
- `STOP` : arrête les deux moteurs. Retour : `OK STOP`.
- `SET <gauche> <droite>` : applique les vitesses moteur de `-1000` à `1000`.
  Retour : `OK SET <gauche> <droite>`.
- `STATUS` : retourne l'état moteur.
  Retour : `OK STATUS gauche=<v> droite=<v> actif=<0|1>`.
- `DIST` : retourne uniquement la distance mesurée en millimètres, par exemple `250`.
  La valeur est plafonnée entre `20` et `3500` mm.
- `SERVO <angle>` : positionne le servomoteur entre `0` et `180` degrés.
  Repères actuels : `45` = gauche, `95` = centre, `140` = droite.
  Retour : `OK SERVO`.

Au démarrage, le Pico envoie aussi `READY` lorsque l'initialisation est terminée.

## Déploiement

Le script de téléversement utilise `mpremote` depuis `.venv`.

Exemple depuis la racine du dépôt :

```bash
python tools/upload_src_to_pico.py
```

## Test UART depuis le Raspberry Pi 4

Le firmware Pico peut être testé depuis le Raspberry Pi par l’UART matériel avec `picocom`.

Connexion utilisée :

- Pico UART0
- Pico TX GPIO0 → Raspberry Pi RX GPIO15
- Pico RX GPIO1 ← Raspberry Pi TX GPIO14
- GND Pico ↔ GND Raspberry Pi
- Débit : 115200 bauds

Commande de test depuis le Raspberry Pi :

```bash
picocom -b 115200 -c /dev/ttyS0
```

Faire `CTRL+A` puis `CTRL+X` pour quitter.
