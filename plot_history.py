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
            bid_price,
            ask_price
        FROM market_ticks
        WHERE event_type = 'quote'
        ORDER BY event_time DESC
        """
    ).fetchall()

# Garder les 6 cotations les plus récentes pour chaque actif
historique = {"BTCUSDT": [], "ETHUSDT": []}

for symbole, date_heure, bid, ask in lignes:
    if symbole in historique and len(historique[symbole]) < 6:
        historique[symbole].append(
            (datetime.fromisoformat(date_heure), (bid + ask) / 2)
        )

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

for axe, symbole in zip(axes, ["BTCUSDT", "ETHUSDT"]):
    points = list(reversed(historique[symbole]))

    if points:
        heures = [point[0] for point in points]
        prix_milieu = [point[1] for point in points]

        axe.plot(heures, prix_milieu, marker="o")
        axe.set_title(symbole)
        axe.ticklabel_format(axis="y", style="plain", useOffset=False)
        axe.grid(True)
    else:
        axe.set_title(f"{symbole} — aucune cotation trouvée")

axes[-1].set_xlabel("Heure de la capture (UTC)")
fig.suptitle("Évolution des prix milieu — dernières cotations")
fig.tight_layout()
plt.show()