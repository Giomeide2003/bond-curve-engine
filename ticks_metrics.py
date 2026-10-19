import sqlite3
from pathlib import Path


# Chercher la base de données dans le même dossier que ce fichier
dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"


# Se connecter à la base et calculer les indicateurs
with sqlite3.connect(fichier_base) as connexion:
    connexion.row_factory = sqlite3.Row

    resultats = connexion.execute(
        """
        SELECT
            asset_symbol,
            COUNT(*) AS nombre_transactions,
            MIN(trade_price) AS prix_minimum,
            MAX(trade_price) AS prix_maximum,
            AVG(trade_price) AS prix_moyen_simple,
            SUM(trade_price * volume) / SUM(volume) AS vwap,
            SUM(volume) AS quantite_totale
        FROM market_ticks
        WHERE event_type = 'trade'
          AND volume > 0
        GROUP BY asset_symbol
        ORDER BY asset_symbol
        """
    ).fetchall()


# Afficher le résumé
if not resultats:
    print("Aucune transaction à analyser.")
else:
    for resultat in resultats:
        print(f"Actif : {resultat['asset_symbol']}")
        print(
            f"Nombre de transactions : "
            f"{resultat['nombre_transactions']}"
        )
        print(f"Prix minimum : {resultat['prix_minimum']}")
        print(f"Prix maximum : {resultat['prix_maximum']}")
        print(
            f"Prix moyen simple : "
            f"{resultat['prix_moyen_simple']:.2f}"
        )
        print(
            f"Prix moyen pondéré par les quantités (VWAP) : "
            f"{resultat['vwap']:.2f}"
        )
        print(f"Quantité totale : {resultat['quantite_totale']}")
        print()