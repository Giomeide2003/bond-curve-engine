import sqlite3
from pathlib import Path


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    total = connexion.execute(
        "SELECT COUNT(*) FROM yield_curve"
    ).fetchone()[0]

    print(f"Nombre total d'observations : {total}")
    print()

    resultats = connexion.execute(
        """
        SELECT
            maturity_years,
            COUNT(*) AS nombre,
            MIN(observation_date) AS premiere_date,
            MAX(observation_date) AS derniere_date
        FROM yield_curve
        GROUP BY maturity_years
        ORDER BY maturity_years
        """
    ).fetchall()

    for maturite, nombre, premiere_date, derniere_date in resultats:
        print(f"Maturité : {maturite} an(s)")
        print(f"Observations : {nombre}")
        print(f"Période : {premiere_date} → {derniere_date}")
        print()