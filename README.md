# robot_devastator_pico

Code MicroPython du Raspberry Pi Pico WH pour le projet Devastator.

## Structure
- `src/` : fichiers déployés sur le Pico
- `tools/` : scripts locaux de téléversement et test
- `.vscode/` : configuration VSCode locale

## Fichiers actuels
- `main.py`
- `controleur_moteurs.py`
- `protocole_uart.py`
- `capteur_ultrason.py`
- `servo.py`

## Matériel
- UART 0 : TX sur GPIO 0, RX sur GPIO 1, 115200 bauds
- Moteurs : driver MDD3A sur GPIO 2 à 5
- Capteur ultrason Grove : SIG sur GPIO 14
- Servomoteur : signal sur GPIO 15

## Important pour éviter problème de démarrage du Pico
Lors de la mise sous tension du Pico et du Raspbery Pi, il faut déconnecter la ligne Raspberry Pi 
TX GPIO14 → Pico RX GPIO1 car elle perturbe le démarrage du Pico. Une fois qu'on constate les
3 clignotements de la LED interne du Pico, c'est OK. Si ça ne clignote pas, c'est qu'il y a eu 
perturbation. On peut ensuite remettre la ligne active. Si tout est OK, GPIO 0 et GPIO 1 du Pico
devrait être à l'état haut.

Pour faciliter, j'ai mis un petit interrupteur qu'il faut tirer vers l'extérieur pendant la mise
sous tension. Ensuite, il s'Agit de le pousser vers l'intérieur. Les voyrant sur le board du Pico 
devraient alors s'allumer pour GPIO 0 et 1. Si seulement GPIO 0 est allumé, ce n'est pas OK.

## Protocole UART
Les commandes sont envoyées en texte ASCII, terminées par `\n`, `\r` ou `\r\n`.

- `PING` : teste le lien UART. Retour : `PONG`
- `STOP` : arrête les deux moteurs. Retour : `OK STOP`
- `SET <gauche> <droite>` : applique les vitesses moteur de `-1000` à `1000`.
  Retour : `OK SET <gauche> <droite>`
- `STATUS` : retourne l'état moteur. Retour : `OK STATUS gauche=<v> droite=<v> actif=<0|1>`
- `DIST` : retourne uniquement la distance mesurée en millimètres, par exemple `250`.
  Retourne `ERREUR : distance invalide` si le capteur ne mesure aucun écho valide.
- `SERVO <angle>` : positionne le servomoteur entre `0` et `180` degrés. `95` = centré, 
  `140` = à droite, `45` = à gauche
  Retour : `OK SERVO`

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
Faire CTRL+A puis CTRL+X pour quitter.
