import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"
symboles = ["BTCUSDT", "ETHUSDT"]
nombre_captures = 30
intervalle_secondes = 2
source = "Binance Spot REST"

with sqlite3.connect(fichier_base) as connexion:
    for numero_capture in range(nombre_captures):
        print(f"Capture {numero_capture + 1}/{nombre_captures}")

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

            print(f"  Cotation enregistrée : {symbole}")

        connexion.commit()

        if numero_capture < nombre_captures - 1:
            time.sleep(intervalle_secondes)

print("Collecte terminée.")