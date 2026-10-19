import csv
import math
import sqlite3
from pathlib import Path


dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"
fichier_sortie = dossier_projet / "bond_returns.csv"

maturites = [1, 2, 5, 10]
observations_par_date = {}

with sqlite3.connect(fichier_base) as connexion:
    lignes = connexion.execute(
        """
        SELECT observation_date, maturity_years, spot_rate_percent
        FROM yield_curve
        ORDER BY observation_date, maturity_years
        """
    ).fetchall()

for date, maturite, taux_pourcent in lignes:
    observations_par_date.setdefault(date, {})[int(maturite)] = taux_pourcent

dates = sorted(observations_par_date)
prix_precedents = {}

colonnes = ["date"]

for maturite in maturites:
    colonnes.extend([
        f"prix_proxy_{maturite}y",
        f"rendement_{maturite}y_pct",
    ])

with fichier_sortie.open("w", newline="", encoding="utf-8") as fichier:
    ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
    ecrivain.writeheader()

    for date in dates:
        ligne_csv = {"date": date}

        for maturite in maturites:
            taux = observations_par_date[date].get(maturite)

            if taux is None:
                ligne_csv[f"prix_proxy_{maturite}y"] = ""
                ligne_csv[f"rendement_{maturite}y_pct"] = ""
                continue

            # La BCE fournit le taux en pourcentage :
            # on le divise par 100 pour obtenir un taux décimal.
            taux_decimal = taux / 100

            # Prix théorique d'un zéro-coupon de valeur nominale 1.
            prix = math.exp(-taux_decimal * maturite)

            cle_prix = f"prix_proxy_{maturite}y"
            cle_rendement = f"rendement_{maturite}y_pct"

            ligne_csv[cle_prix] = round(prix, 10)

            if maturite in prix_precedents:
                rendement_pct = (
                    prix / prix_precedents[maturite] - 1
                ) * 100
                ligne_csv[cle_rendement] = round(rendement_pct, 8)
            else:
                ligne_csv[cle_rendement] = ""

            prix_precedents[maturite] = prix

        ecrivain.writerow(ligne_csv)

print(f"Lignes de taux lues : {len(lignes)}")
print(f"Dates traitées : {len(dates)}")
print(f"Fichier créé : {fichier_sortie}")
print("Les rendements du premier jour restent vides : il n'y a pas de jour précédent.")