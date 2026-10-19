import csv
import io
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Séries BCE des taux spot AAA
series_bce = {
    "1": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y",
    "2": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y",
    "5": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y",
    "10": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",
}

# Demander les deux dernières observations de chaque série
parametres = urlencode({
    "lastNObservations": "365",
    "format": "csvdata",
})

observations = {}

# Récupérer les observations de chaque maturité
for maturite, serie_bce in series_bce.items():
    url = (
        f"https://data-api.ecb.europa.eu/service/data/YC/"
        f"{serie_bce}?{parametres}"
    )
    requete = Request(url, headers={"Accept": "text/csv"})

    with urlopen(requete, timeout=30) as reponse:
        contenu = reponse.read().decode("utf-8-sig")

    lignes_bce = list(csv.DictReader(io.StringIO(contenu)))

    if not lignes_bce:
        raise RuntimeError(
            f"La BCE n'a renvoyé aucune donnée pour la maturité {maturite} an."
        )

    observations[maturite] = [
        {
            "date": ligne["TIME_PERIOD"],
            "taux": ligne["OBS_VALUE"],
        }
        for ligne in lignes_bce
    ]

# Garder seulement les dates présentes dans les quatre séries
dates_communes = {
    ligne["date"] for ligne in observations["1"]
}

for lignes_maturite in observations.values():
    dates_de_cette_maturite = {
        ligne["date"] for ligne in lignes_maturite
    }
    dates_communes &= dates_de_cette_maturite

if not dates_communes:
    raise RuntimeError(
        "Aucune date commune n'a été trouvée pour les quatre maturités."
    )

print("Dates communes récupérées :", ", ".join(sorted(dates_communes)))

# Trouver le fichier CSV situé à côté de Data.py
fichier_csv = Path(__file__).resolve().parent / "observations.csv"
print("Fichier CSV utilisé :", fichier_csv)

# Lire les anciennes données, même si l'en-tête manque
lignes_existantes = {}

if fichier_csv.exists():
    with fichier_csv.open("r", newline="", encoding="utf-8-sig") as fichier:
        lecteur = csv.reader(fichier)

        for numero_ligne, ligne in enumerate(lecteur, start=1):
            if not ligne or all(cellule.strip() == "" for cellule in ligne):
                continue

            colonnes = [cellule.strip() for cellule in ligne]

            # Ignorer la ligne d'en-tête
            if colonnes[0].lower() == "date":
                continue

            if len(colonnes) != 3:
                raise ValueError(
                    f"La ligne {numero_ligne} de observations.csv "
                    "ne contient pas exactement 3 colonnes."
                )

            date_ligne, maturite_ligne, taux_ligne = colonnes
            cle = (date_ligne, maturite_ligne)

            # Ne conserver qu'une ligne par date et maturité
            if cle not in lignes_existantes:
                lignes_existantes[cle] = taux_ligne

# Ajouter les nouvelles observations qui ne sont pas déjà enregistrées
nombre_ajoute = 0

for maturite, lignes_maturite in observations.items():
    for ligne in lignes_maturite:
        if ligne["date"] not in dates_communes:
            continue

        cle = (ligne["date"], maturite)

        if cle not in lignes_existantes:
            lignes_existantes[cle] = ligne["taux"]
            nombre_ajoute += 1

# Réécrire le CSV avec son en-tête et sans doublons
with fichier_csv.open("w", newline="", encoding="utf-8") as fichier:
    ecrivain = csv.writer(fichier)
    ecrivain.writerow(["date", "maturite", "taux_pourcent"])

    lignes_triees = sorted(
        lignes_existantes.items(),
        key=lambda element: (element[0][0], int(element[0][1]))
    )

    for (date_ligne, maturite_ligne), taux_ligne in lignes_triees:
        ecrivain.writerow([date_ligne, maturite_ligne, taux_ligne])

print("Nouvelles observations ajoutées :", nombre_ajoute)
print("Le fichier observations.csv a été mis à jour.")