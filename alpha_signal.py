import sqlite3
from pathlib import Path


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    lignes = connexion.execute(
        """
        SELECT
            asset_symbol,
            event_time,
            bid_price,
            ask_price,
            bid_quantity,
            ask_quantity
        FROM market_ticks
        WHERE event_type = 'quote'
          AND bid_quantity IS NOT NULL
          AND ask_quantity IS NOT NULL
        ORDER BY event_time DESC
        """
    ).fetchall()

historique = {"BTCUSDT": [], "ETHUSDT": []}

for ligne in lignes:
    symbole = ligne[0]

    if symbole in historique and len(historique[symbole]) < 6:
        prix_milieu = (ligne[2] + ligne[3]) / 2

        historique[symbole].append({
            "heure": ligne[1],
            "prix_milieu": prix_milieu,
            "quantite_achat": ligne[4],
            "quantite_vente": ligne[5],
        })

for symbole, cotations in historique.items():
    print(f"Actif : {symbole}")

    if len(cotations) < 2:
        print("Pas assez de cotations pour calculer le signal.\n")
        continue

    cotation_recente = cotations[0]
    cotation_ancienne = cotations[-1]

    variation_prix = (
        (cotation_recente["prix_milieu"] - cotation_ancienne["prix_milieu"])
        / cotation_ancienne["prix_milieu"]
    ) * 100

    quantite_achat = cotation_recente["quantite_achat"]
    quantite_vente = cotation_recente["quantite_vente"]
    total = quantite_achat + quantite_vente

    desequilibre = (
        (quantite_achat - quantite_vente) / total
    ) * 100 if total > 0 else 0

    if variation_prix > 0 and desequilibre > 0:
        signal = "Biais acheteur"
    elif variation_prix < 0 and desequilibre < 0:
        signal = "Biais vendeur"
    else:
        signal = "Signal mixte"

    print(f"Variation du prix sur les cotations observées : {variation_prix:.5f} %")
    print(f"Déséquilibre achat/vente récent : {desequilibre:.2f} %")
    print(f"Signal pédagogique : {signal}")
    print()