import sqlite3
from pathlib import Path


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    resultats = connexion.execute(
        """
        SELECT
            asset_symbol,
            COUNT(*) AS nombre_cotations,
            AVG(
                (ask_price - bid_price)
                / ((ask_price + bid_price) / 2.0)
                * 10000
            ) AS spread_moyen_points_base
        FROM market_ticks
        WHERE event_type = 'quote'
          AND bid_price IS NOT NULL
          AND ask_price IS NOT NULL
        GROUP BY asset_symbol
        ORDER BY asset_symbol
        """
    ).fetchall()

if not resultats:
    print("Aucune cotation disponible pour mesurer la liquidité.")
else:
    for symbole, nombre, spread_moyen in resultats:
        print(f"Actif : {symbole}")
        print(f"Nombre de cotations : {nombre}")
        print(f"Écart moyen : {spread_moyen:.6f} points de base")
        print()