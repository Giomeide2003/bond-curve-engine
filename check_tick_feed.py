import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen


symboles = ["BTCUSDT", "ETHUSDT"]

for symbole in symboles:
    parametres = urlencode({
        "symbol": symbole,
        "limit": "1",
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
        transactions = json.loads(reponse.read().decode("utf-8"))

    transaction = transactions[-1]

    date_heure = datetime.fromtimestamp(
        transaction["time"] / 1000,
        tz=timezone.utc,
    )

    print(f"Actif : {symbole}")
    print(f"Date et heure UTC : {date_heure}")
    print(f"Prix : {transaction['price']}")
    print(f"Quantité : {transaction['qty']}")
    print()