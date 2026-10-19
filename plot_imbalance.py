import sqlite3
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


fichier_base = Path(__file__).resolve().parent / "bond_curve.db"

with sqlite3.connect(fichier_base) as connexion:
    lignes = connexion.execute(
        """
        SELECT
            asset_symbol,
            event_time,
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

for symbole, date_heure, quantite_achat, quantite_vente in lignes:
    if symbole not in historique or len(historique[symbole]) >= 6:
        continue

    total = quantite_achat + quantite_vente

    if total > 0:
        desequilibre = (
            (quantite_achat - quantite_vente) / total
        ) * 100

        historique[symbole].append(
            (datetime.fromisoformat(date_heure), desequilibre)
        )

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

for axe, symbole in zip(axes, ["BTCUSDT", "ETHUSDT"]):
    points = list(reversed(historique[symbole]))

    if points:
        heures = [point[0] for point in points]
        valeurs = [point[1] for point in points]

        axe.plot(heures, valeurs, marker="o")
        axe.axhline(0, color="black", linewidth=1)
        axe.set_title(symbole)
        axe.set_ylabel("Déséquilibre (%)")
        axe.set_ylim(-100, 100)
        axe.grid(True)
    else:
        axe.set_title(f"{symbole} — aucune cotation avec quantités")

axes[-1].set_xlabel("Heure de la capture (UTC)")
fig.suptitle("Évolution du déséquilibre achat/vente")
fig.tight_layout()
plt.show()