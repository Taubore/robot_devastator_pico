from pathlib import Path
import subprocess
import sys


def main() -> int:
    racine_projet = Path(__file__).resolve().parent.parent
    mpremote = racine_projet / ".venv" / "bin" / "mpremote"
    dossier_src = racine_projet / "src"

    if not mpremote.exists():
        print(f"Erreur : mpremote introuvable : {mpremote}", file=sys.stderr)
        return 1

    if not dossier_src.exists():
        print(f"Erreur : dossier src introuvable : {dossier_src}", file=sys.stderr)
        return 1

    fichiers = sorted(dossier_src.glob("*.py"))

    if not fichiers:
        print("Aucun fichier .py trouvé dans src/", file=sys.stderr)
        return 1

    for fichier in fichiers:
        destination = f":{fichier.name}"
        commande = [
            str(mpremote),
            "connect",
            "auto",
            "fs",
            "cp",
            str(fichier),
            destination,
        ]

        print(f"Upload : {fichier.name}")
        resultat = subprocess.run(commande)

        if resultat.returncode != 0:
            print(f"Échec upload : {fichier.name}", file=sys.stderr)
            return resultat.returncode

    print("Upload terminé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())