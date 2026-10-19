import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


symboles = ["BTCUSDT", "ETHUSDT"]

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

    prix_achat = float(cotation["bidPrice"])
    quantite_achat = float(cotation["bidQty"])
    prix_vente = float(cotation["askPrice"])
    quantite_vente = float(cotation["askQty"])

    ecart = prix_vente - prix_achat
    prix_milieu = (prix_vente + prix_achat) / 2
    ecart_points_base = ecart / prix_milieu * 10_000

    print(f"Actif : {symbole}")
    print(f"Meilleur prix d'achat (bid) : {prix_achat}")
    print(f"Quantité disponible à l'achat : {quantite_achat}")
    print(f"Meilleur prix de vente (ask) : {prix_vente}")
    print(f"Quantité disponible à la vente : {quantite_vente}")
    print(f"Écart achat-vente : {ecart}")
    print(f"Écart en points de base : {ecart_points_base:.4f}")
    print()