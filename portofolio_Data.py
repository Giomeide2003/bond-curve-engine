import csv
from pathlib import Path


dossier = Path(__file__).resolve().parent
fichier_obligations = dossier / "bond_returns.csv"
fichier_crypto = dossier / "crypto_returns.csv"
fichier_sortie = dossier / "portfolio_returns.csv"

colonnes_obligations = {
    "bond_1y_return_pct": "rendement_1y_pct",
    "bond_2y_return_pct": "rendement_2y_pct",
    "bond_5y_return_pct": "rendement_5y_pct",
    "bond_10y_return_pct": "rendement_10y_pct",
}

with fichier_obligations.open(
    "r", newline="", encoding="utf-8"
) as fichier:
    obligations = {
        ligne["date"]: ligne
        for ligne in csv.DictReader(fichier)
    }

with fichier_crypto.open(
    "r", newline="", encoding="utf-8"
) as fichier:
    crypto = {
        ligne["date"]: ligne
        for ligne in csv.DictReader(fichier)
    }

dates_communes = sorted(set(obligations) & set(crypto))

colonnes_sortie = [
    "date",
    *colonnes_obligations.keys(),
    "BTCUSDT_return_pct",
    "ETHUSDT_return_pct",
]

lignes_sortie = []

for date in dates_communes:
    ligne_obligations = obligations[date]

    valeurs_obligations = [
        ligne_obligations[colonne]
        for colonne in colonnes_obligations.values()
    ]

    # Ignorer la première date, dont les rendements obligataires sont vides
    if any(valeur == "" for valeur in valeurs_obligations):
        continue

    lignes_sortie.append({
        "date": date,
        **dict(zip(colonnes_obligations.keys(), valeurs_obligations)),
        "BTCUSDT_return_pct": crypto[date]["BTCUSDT_return_pct"],
        "ETHUSDT_return_pct": crypto[date]["ETHUSDT_return_pct"],
    })

with fichier_sortie.open("w", newline="", encoding="utf-8") as fichier:
    ecrivain = csv.DictWriter(fichier, fieldnames=colonnes_sortie)
    ecrivain.writeheader()
    ecrivain.writerows(lignes_sortie)

print(f"Dates communes utilisables : {len(lignes_sortie)}")
if lignes_sortie:
    print(
        f"Période : {lignes_sortie[0]['date']} → "
        f"{lignes_sortie[-1]['date']}"
    )
print(f"Fichier créé : {fichier_sortie}")