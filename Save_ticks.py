import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

symboles = ["BTCUSDT", "ETHUSDT"]
nombre_transactions = 10
source = "Binance Spot REST"

nombre_ajoute = 0

with sqlite3.connect(fichier_base) as connexion:
    for symbole in symboles:
        parametres = urlencode({
            "symbol": symbole,
            "limit": str(nombre_transactions),
        })

        url = (
            "https://data-api.binance.vision/api/v3/trades?"
            f"{parametres}"
        )

        requete = Request(
            url,
            headers={"User-Agent": "Bond-Curve-Engine"},
        )

        with urlopen(requete, timeout=30) as reponse:
            transactions = json.loads(
                reponse.read().decode("utf-8")
            )

        ajoutees_pour_actif = 0

        for transaction in transactions:
            date_heure = datetime.fromtimestamp(
                transaction["time"] / 1000,
                tz=timezone.utc,
            ).isoformat(timespec="milliseconds")

            resultat = connexion.execute(
                """
                INSERT OR IGNORE INTO market_ticks (
                    source,
                    asset_symbol,
                    asset_class,
                    event_time,
                    event_type,
                    bid_price,
                    ask_price,
                    trade_price,
                    volume,
                    source_event_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source,
                    symbole,
                    "crypto",
                    date_heure,
                    "trade",
                    None,
                    None,
                    float(transaction["price"]),
                    float(transaction["qty"]),
                    str(transaction["id"]),
                ),
            )

            if resultat.rowcount == 1:
                ajoutees_pour_actif += 1
                nombre_ajoute += 1

        print(
            f"{symbole} : {ajoutees_pour_actif} "
            "nouvelles transactions enregistrées."
        )

    connexion.commit()

print(f"Total ajouté : {nombre_ajoute}")
print(f"Base de données utilisée : {fichier_base}")