import csv
from pathlib import Path
from statistics import pstdev

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


DOSSIER = Path(__file__).resolve().parent
FICHIER_ENTREE = DOSSIER / "portfolio_returns.csv"
FICHIER_SORTIE = DOSSIER / "market_regimes.csv"

COLONNES_RENDEMENTS = [
    "bond_1y_return_pct",
    "bond_2y_return_pct",
    "bond_5y_return_pct",
    "bond_10y_return_pct",
    "BTCUSDT_return_pct",
    "ETHUSDT_return_pct",
]

FENETRE = 20


# Lire les rendements du fichier CSV
with FICHIER_ENTREE.open("r", newline="", encoding="utf-8-sig") as fichier:
    lecteur = csv.DictReader(fichier)

    colonnes_manquantes = [
        colonne
        for colonne in ["date", *COLONNES_RENDEMENTS]
        if colonne not in (lecteur.fieldnames or [])
    ]

    if colonnes_manquantes:
        raise ValueError(
            "Colonnes manquantes dans portfolio_returns.csv : "
            + ", ".join(colonnes_manquantes)
        )

    lignes = list(lecteur)


# Calculer la volatilité sur les 20 derniers jours
dates = []
volatilites = []

for fin in range(FENETRE, len(lignes) + 1):
    fenetre_lignes = lignes[fin - FENETRE : fin]
    date = fenetre_lignes[-1]["date"]

    volatilites_jour = []

    for colonne in COLONNES_RENDEMENTS:
        rendements = [
            float(ligne[colonne])
            for ligne in fenetre_lignes
            if ligne[colonne] not in ("", None)
        ]

        if len(rendements) != FENETRE:
            raise ValueError(
                f"Valeur manquante dans la colonne {colonne}, "
                f"autour de la date {date}."
            )

        volatilites_jour.append(pstdev(rendements))

    dates.append(date)
    volatilites.append(volatilites_jour)


if len(volatilites) < 2:
    raise ValueError(
        "Il faut au moins 21 dates dans portfolio_returns.csv "
        "pour détecter les régimes."
    )


# Mettre les volatilités à la même échelle, puis créer deux groupes
normaliseur = StandardScaler()
volatilites_normalisees = normaliseur.fit_transform(volatilites)

modele = KMeans(
    n_clusters=2,
    random_state=42,
    n_init=10,
)
groupes = modele.fit_predict(volatilites_normalisees)


# Nommer le groupe dont la volatilité moyenne est la plus élevée
moyennes_groupes = {}

for groupe in (0, 1):
    indices = [
        index
        for index, groupe_obtenu in enumerate(groupes)
        if groupe_obtenu == groupe
    ]

    moyenne = sum(
        sum(volatilites_normalisees[index]) / len(COLONNES_RENDEMENTS)
        for index in indices
    ) / len(indices)

    moyennes_groupes[groupe] = moyenne

groupe_volatile = max(moyennes_groupes, key=moyennes_groupes.get)


# Écrire les résultats dans un nouveau CSV
with FICHIER_SORTIE.open("w", newline="", encoding="utf-8") as fichier:
    colonnes_sortie = ["date", "regime"]
    ecrivain = csv.DictWriter(fichier, fieldnames=colonnes_sortie)
    ecrivain.writeheader()

    for date, groupe in zip(dates, groupes):
        regime = (
            "volatilite_elevee"
            if groupe == groupe_volatile
            else "volatilite_faible"
        )

        ecrivain.writerow({
            "date": date,
            "regime": regime,
        })


# Afficher le résumé et les changements de régime détectés
print(f"Dates analysées : {len(dates)}")
print(f"Fichier créé : {FICHIER_SORTIE}")

print("\nChangements de régime détectés :")

nombre_changements = 0
for index in range(1, len(groupes)):
    if groupes[index] != groupes[index - 1]:
        regime = (
            "volatilité élevée"
            if groupes[index] == groupe_volatile
            else "volatilité faible"
        )
        print(f"{dates[index]} : passage à une {regime}")
        nombre_changements += 1

if nombre_changements == 0:
    print("Aucun changement de régime détecté.")