import subprocess
import sys
from pathlib import Path


dossier_projet = Path(__file__).resolve().parent

etapes = [
    "tickSchema.py",
    "Data.py",
    "DataBase.py",
    "save_ticks.py",
    "save_quotes.py",
]

for nom_fichier in etapes:
    chemin_fichier = dossier_projet / nom_fichier

    if not chemin_fichier.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin_fichier}"
        )

    print(f"\n--- Exécution de {nom_fichier} ---")

    subprocess.run(
        [sys.executable, str(chemin_fichier)],
        cwd=dossier_projet,
        check=True,
    )

print("\nPipeline terminé.")