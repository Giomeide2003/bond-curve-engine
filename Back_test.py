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
        ORDER BY event_time
        """
    ).fetchall()

historique = {}

for ligne in lignes:
    symbole = ligne[0]
    bid = ligne[2]
    ask = ligne[3]
    quantite_achat = ligne[4]
    quantite_vente = ligne[5]
    total = quantite_achat + quantite_vente

    if total == 0:
        continue

    desequilibre = (quantite_achat - quantite_vente) / total

    historique.setdefault(symbole, []).append({
        "bid": bid,
        "ask": ask,
        "desequilibre": desequilibre,
    })

for symbole, cotations in historique.items():
    rendements = []

    for index in range(len(cotations) - 1):
        cotation_actuelle = cotations[index]
        cotation_suivante = cotations[index + 1]

        # Acheter seulement si le déséquilibre est positif
        if cotation_actuelle["desequilibre"] > 0:
            prix_achat = cotation_actuelle["ask"]
            prix_revente = cotation_suivante["bid"]

            rendement = (
                (prix_revente - prix_achat) / prix_achat
            ) * 100

            rendements.append(rendement)

    print(f"Actif : {symbole}")
    print(f"Achats hypothétiques : {len(rendements)}")

    if rendements:
        nombre_gagnants = sum(1 for rendement in rendements if rendement > 0)
        rendement_moyen = sum(rendements) / len(rendements)

        print(f"Achats avec rendement positif : {nombre_gagnants}")
        print(f"Rendement moyen : {rendement_moyen:.6f} %")
    else:
        print("Aucun déséquilibre positif trouvé.")

    print()