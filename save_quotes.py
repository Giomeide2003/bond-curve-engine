import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

symboles = ["BTCUSDT", "ETHUSDT"]
source = "Binance Spot REST"

with sqlite3.connect(fichier_base) as connexion:
    for symbole in symboles:
        parametres = urlencode({"symbol": symbole})
        url = (
            "https://data-api.binance.vision/api/v3/ticker/bookTicker?"
            f"{parametres}"
        )

        requete = Request(
            url,
            headers={"User-Agent": "Bond-Curve-Engine"},
        )

        with urlopen(requete, timeout=30) as reponse:
            cotation = json.loads(reponse.read().decode("utf-8"))

        date_heure = datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        )

        connexion.execute(
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
                source_event_id,
                bid_quantity,
                ask_quantity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                symbole,
                "crypto",
                date_heure,
                "quote",
                float(cotation["bidPrice"]),
                float(cotation["askPrice"]),
                None,
                None,
                date_heure,
                float(cotation["bidQty"]),
                float(cotation["askQty"]),
            ),
        )

        print(f"Cotation avec quantités enregistrée pour {symbole}.")

    connexion.commit()

print(f"Base de données utilisée : {fichier_base}")