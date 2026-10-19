import csv
import sqlite3
from pathlib import Path


# Trouver les fichiers à côté de DataBase.py
dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"
fichier_csv = dossier_projet / "observations.csv"

if not fichier_csv.exists():
    raise FileNotFoundError(
        f"Le fichier CSV est introuvable : {fichier_csv}"
    )

# Lire les observations du CSV
with fichier_csv.open("r", newline="", encoding="utf-8-sig") as fichier:
    lignes_csv = list(csv.DictReader(fichier))

# Créer la base et la table, puis importer les observations
with sqlite3.connect(fichier_base) as connexion:
    connexion.execute("""
        CREATE TABLE IF NOT EXISTS yield_curve (
            observation_date TEXT NOT NULL,
            maturity_years REAL NOT NULL,
            spot_rate_percent REAL NOT NULL,
            PRIMARY KEY (observation_date, maturity_years)
        )
    """)

    nombre_ajoute = 0

    for ligne in lignes_csv:
        resultat = connexion.execute(
            """
            INSERT OR IGNORE INTO yield_curve
                (observation_date, maturity_years, spot_rate_percent)
            VALUES (?, ?, ?)
            """,
            (
                ligne["date"],
                float(ligne["maturite"]),
                float(ligne["taux_pourcent"]),
            ),
        )

        nombre_ajoute += resultat.rowcount

print("Base de données :", fichier_base)
print("Observations lues dans le CSV :", len(lignes_csv))
print("Nouvelles lignes ajoutées à la base :", nombre_ajoute)

# Lire les observations enregistrées dans la base
with sqlite3.connect(fichier_base) as connexion:
    lignes_base = connexion.execute("""
        SELECT observation_date, maturity_years, spot_rate_percent
        FROM yield_curve
        ORDER BY observation_date, maturity_years
    """).fetchall()

print("Contenu de la table yield_curve :")

for date, maturite, taux in lignes_base:
    print(f"{date} | {maturite:g} an(s) | {taux:.6f} %")