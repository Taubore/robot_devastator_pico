# AGENTS.md — Consignes pour Codex

## Portée

Ce dépôt contient du code MicroPython destiné à un Raspberry Pi Pico ou Pico WH.

Le code doit rester simple, robuste, lisible et adapté à un microcontrôleur. Ne pas appliquer des
réflexes de développement PC ou serveur à du code embarqué contraint.

## Environnement

- Langage : MicroPython
- Cible : Raspberry Pi Pico / Pico WH
- Développement principal : VSCode
- Déploiement : copie ou téléversement vers le Pico selon les outils du projet
- Ne pas utiliser ROS 2 dans ce dépôt
- Ne pas ajouter de dépendance externe sans justification et validation

## Principes généraux

- Une seule complexité à la fois.
- Valider physiquement chaque sous-système avant intégration.
- Garder les changements petits, lisibles et faciles à tester.
- Ne pas créer d’architecture parallèle.
- Ne pas ajouter de fichier, dossier ou abstraction sans besoin réel.
- Préférer une solution minimale fiable à une solution générale prématurée.

## Structure du code

- Respecter la structure existante du dépôt.
- `main.py` doit rester un point d’entrée clair.
- `test.py` est une commodité pour tester rapidement sur le Pico, ce n'est pas un script officiel même s'il est tout de même conservé dans Git
- Placer la logique spécialisée dans des modules dédiés lorsque cela améliore réellement la lisibilité.
- Ne pas transformer un firmware simple en framework.
- Éviter de mélanger dans une même modification : refactorisation, nouveau matériel et changement de protocole.

## Sécurité matérielle

Le firmware doit toujours privilégier un état sûr.

- Initialiser les sorties dans un état inoffensif.
- Prévoir un arrêt explicite pour tout actionneur.
- Éviter les mouvements prolongés sans raison.
- Utiliser des vitesses, angles ou intensités prudentes lors des premiers tests.
- Éviter les boucles bloquantes si elles peuvent empêcher une réaction de sécurité.
- Ne jamais désactiver une sécurité pour simplifier un test.

## Communication

- garder le protocole de communication UART simple, textuel et très clairement documenté
- préserver les commandes existantes sauf validation explicite
- garder les réponses courtes, lisibles et faciles à tester
- documenter toute modification de protocole
- éviter les formats complexes tant que le besoin n’est pas démontré

## Style Python / MicroPython

- Identifiants en français sans accents.
- Commentaires, docstrings et messages utilisateur en français avec accents.
- Docstrings multilignes.
- Lignes limitées à 100 caractères.
- Utiliser des constantes nommées au lieu de valeurs magiques.
- Garder les fonctions courtes et orientées action.
- Éviter la surconception.
- Ajouter des commentaires sur l’intention, les contraintes matérielles et les choix non évidents.
- Ne pas commenter trivialement chaque ligne.

## Typage et analyse statique

Le code cible MicroPython. Les modules matériels comme `machine`, `Pin`, `PWM`, `UART`, `ADC`
ou `I2C` peuvent être mal compris par les analyseurs Python standards.

- Ne pas viser une conformité stricte à Pyright/Pylance.
- Ne pas ajouter de complexité uniquement pour satisfaire un analyseur de types.
- Les commentaires d’ignorance pour imports MicroPython sont acceptables si nécessaires.
- Si un diagnostic révèle une vraie ambiguïté logique, corriger le code simplement.

## Tests

Privilégier des tests courts, ciblés et observables.

Ordre recommandé :

1. tester une fonction isolée quand c’est possible
2. tester un périphérique seul
3. tester la communication seule
4. intégrer progressivement
5. valider physiquement avant d’ajouter une nouvelle complexité

Pour tout test matériel :

- commencer avec des valeurs prudentes
- prévoir un arrêt
- observer le comportement réel
- noter les écarts avant de modifier le code

## Documentation

Mettre à jour la documentation si une modification change :

- la procédure de déploiement
- le protocole de communication
- les fichiers importants
- les contraintes matérielles
- les procédures de test
- les règles de sécurité

Ne pas dupliquer inutilement la documentation externe au dépôt.

## Git

- Branches simples et ciblées.
- Commits petits et cohérents.
- Messages de commit en français.
- Ne pas faire de suppression massive, renommage important, reset ou fusion sans accord explicite.
- Ne pas mélanger plusieurs objectifs dans un même commit.

## Interaction avec Codex

Avant une modification non triviale :

1. analyser le code existant
2. proposer un plan court
3. attendre validation

Pour chaque tâche :

- partir du code existant
- faire la plus petite modification utile
- indiquer les fichiers touchés
- expliquer comment tester
- éviter les solutions parallèles