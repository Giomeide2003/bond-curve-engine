import sqlite3
from pathlib import Path


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    colonnes = {
        ligne[1]
        for ligne in connexion.execute(
            "PRAGMA table_info(market_ticks)"
        )
    }

    if "bid_quantity" not in colonnes:
        connexion.execute(
            "ALTER TABLE market_ticks ADD COLUMN bid_quantity REAL"
        )
        print("Colonne bid_quantity ajoutée.")

    if "ask_quantity" not in colonnes:
        connexion.execute(
            "ALTER TABLE market_ticks ADD COLUMN ask_quantity REAL"
        )
        print("Colonne ask_quantity ajoutée.")

    connexion.commit()

print("La table market_ticks est prête pour les quantités bid et ask.")