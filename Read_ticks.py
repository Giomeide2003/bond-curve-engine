import sqlite3
from pathlib import Path


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    connexion.row_factory = sqlite3.Row

    transactions = connexion.execute(
        """
        SELECT
            asset_symbol,
            event_time,
            trade_price,
            volume
        FROM market_ticks
        ORDER BY event_time DESC
        """
    ).fetchall()

if not transactions:
    print("Aucune transaction n'est enregistrée.")
else:
    print(f"Transactions trouvées : {len(transactions)}")
    print()

    for transaction in transactions:
        print(f"Actif : {transaction['asset_symbol']}")
        print(f"Date et heure UTC : {transaction['event_time']}")
        print(f"Prix : {transaction['trade_price']}")
        print(f"Quantité : {transaction['volume']}")
        print()