import sqlite3
from pathlib import Path


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

# Calculer, pour chaque date, le taux à 10 ans moins le taux à 1 an
with sqlite3.connect(fichier_base) as connexion:
    resultats = connexion.execute("""
        SELECT taux_10_ans.observation_date,
               taux_10_ans.spot_rate_percent
               - taux_1_an.spot_rate_percent
        FROM yield_curve AS taux_1_an
        JOIN yield_curve AS taux_10_ans
          ON taux_1_an.observation_date = taux_10_ans.observation_date
        WHERE taux_1_an.maturity_years = 1
          AND taux_10_ans.maturity_years = 10
        ORDER BY taux_10_ans.observation_date
    """).fetchall()

if not resultats:
    raise RuntimeError(
        "La base ne contient pas encore les taux à 1 an et à 10 ans."
    )

print("Écart entre le taux à 10 ans et celui à 1 an :")

for date, ecart in resultats:
    ecart_points_base = ecart * 100
    print(
        f"{date} : {ecart:.4f} point de pourcentage "
        f"({ecart_points_base:.1f} points de base)"
    )