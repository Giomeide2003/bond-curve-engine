import csv
import sqlite3
from pathlib import Path

import cvxpy as cp
import numpy as np


dossier = Path(__file__).resolve().parent
fichier_donnees = dossier / "portfolio_returns.csv"
fichier_base = dossier / "bond_curve.db"

noms_actifs = [
    "Obligation proxy 1 an",
    "Obligation proxy 2 ans",
    "Obligation proxy 5 ans",
    "Obligation proxy 10 ans",
    "BTCUSDT",
    "ETHUSDT",
    "Trésorerie",
]

colonnes_rendements = [
    "bond_1y_return_pct",
    "bond_2y_return_pct",
    "bond_5y_return_pct",
    "bond_10y_return_pct",
    "BTCUSDT_return_pct",
    "ETHUSDT_return_pct",
]

with fichier_donnees.open("r", newline="", encoding="utf-8") as fichier:
    lignes = list(csv.DictReader(fichier))

if len(lignes) < 2:
    raise RuntimeError("Il faut au moins deux lignes de rendements.")

rendements_actifs = np.array([
    [float(ligne[colonne]) / 100 for colonne in colonnes_rendements]
    for ligne in lignes
])

# La trésorerie est supposée avoir un rendement nul
rendements = np.column_stack((
    rendements_actifs,
    np.zeros(len(rendements_actifs)),
))

rendements_annuels_moyens = np.mean(rendements, axis=0) * 252
covariance_annuelle = np.cov(rendements, rowvar=False) * 252
covariance_annuelle += np.eye(len(noms_actifs)) * 1e-10

# Lire les écarts bid-ask moyens observés pour les actifs crypto
with sqlite3.connect(fichier_base) as connexion:
    lignes_liquidite = connexion.execute(
        """
        SELECT
            asset_symbol,
            AVG(
                (ask_price - bid_price)
                / ((ask_price + bid_price) / 2.0)
                * 10000
            )
        FROM market_ticks
        WHERE event_type = 'quote'
          AND bid_price IS NOT NULL
          AND ask_price IS NOT NULL
        GROUP BY asset_symbol
        """
    ).fetchall()

spread_moyen_bps = {
    symbole: spread
    for symbole, spread in lignes_liquidite
}

# Conversion des points de base en coût décimal.
# La moitié du spread représente le coût estimé d'une transaction
# depuis le milieu de la fourchette.
couts_liquidite = np.zeros(len(noms_actifs))
couts_liquidite[4] = spread_moyen_bps.get("BTCUSDT", 0) / 20000
couts_liquidite[5] = spread_moyen_bps.get("ETHUSDT", 0) / 20000

poids = cp.Variable(len(noms_actifs))
poids_initial = np.array([0, 0, 0, 0, 0, 0, 1])

aversion_au_risque = 5.0

cout_de_reallocation = cp.sum(
    cp.multiply(couts_liquidite, cp.abs(poids - poids_initial))
)

objectif = cp.Maximize(
    rendements_annuels_moyens @ poids
    - aversion_au_risque
    * cp.quad_form(poids, cp.psd_wrap(covariance_annuelle))
    - cout_de_reallocation
)

contraintes = [
    cp.sum(poids) == 1,
    poids >= 0,
    poids[:6] <= 0.50,
    poids[4] + poids[5] <= 0.20,
]

probleme = cp.Problem(objectif, contraintes)
probleme.solve()

if poids.value is None:
    print(f"L'optimisation n'a pas abouti : {probleme.status}")
else:
    poids_optimaux = np.maximum(poids.value, 0)

    print(f"Statut : {probleme.status}")
    print(f"Dates utilisées : {len(lignes)}")
    print("\nÉcarts moyens observés :")
    print(f"BTCUSDT : {spread_moyen_bps.get('BTCUSDT', 0):.6f} points de base")
    print(f"ETHUSDT : {spread_moyen_bps.get('ETHUSDT', 0):.6f} points de base")

    print("\nAllocation proposée :")
    for nom, allocation in zip(noms_actifs, poids_optimaux):
        print(f"{nom} : {allocation * 100:.2f} %")

    rendement = rendements_annuels_moyens @ poids_optimaux
    risque = np.sqrt(
        poids_optimaux @ covariance_annuelle @ poids_optimaux
    )

    print(f"\nRendement annuel estimé : {rendement * 100:.2f} %")
    print(f"Risque annuel estimé : {risque * 100:.2f} %")