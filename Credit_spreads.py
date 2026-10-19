import csv
import io
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SERIES_BCE = {
    "notation_la_plus_elevee": (
        "STP.B.A1.1100.C.XXXX.O.DH.R1.Y.A.EUR.A"
    ),
    "notation_elevee": (
        "STP.B.A1.1100.C.XXXX.O.DH.R2.Y.A.EUR.A"
    ),
}

DOSSIER = Path(__file__).resolve().parent
FICHIER_SORTIE = DOSSIER / "credit_spreads.csv"


def recuperer_serie(identifiant):
    parametres = urlencode({
        "lastNObservations": "365",
        "format": "csvdata",
    })

    url = (
        "https://data-api.ecb.europa.eu/service/data/STP/"
        f"{identifiant}?{parametres}"
    )

    requete = Request(
        url,
        headers={"Accept": "text/csv"},
    )

    try:
        with urlopen(requete, timeout=30) as reponse:
            contenu = reponse.read().decode("utf-8-sig")

    except HTTPError as erreur:
        details = erreur.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"La BCE a renvoyé l'erreur HTTP {erreur.code}.\n"
            f"Série demandée : {identifiant}\n"
            f"URL : {url}\n"
            f"Détail de la BCE : {details}"
        ) from erreur

    except URLError as erreur:
        raise RuntimeError(
            f"Connexion à la BCE impossible : {erreur.reason}"
        ) from erreur

    lecteur = csv.DictReader(io.StringIO(contenu))
    resultats = {}

    for ligne in lecteur:
        date = ligne.get("TIME_PERIOD", "").strip()
        valeur = ligne.get("OBS_VALUE", "").strip()

        if date and valeur and valeur != ".":
            resultats[date] = float(valeur)

    if not resultats:
        raise RuntimeError(
            f"Aucune observation exploitable pour la série {identifiant}."
        )

    return resultats


rendements = {}

for nom, identifiant in SERIES_BCE.items():
    print(f"Téléchargement de la série : {nom}")
    rendements[nom] = recuperer_serie(identifiant)


dates_communes = sorted(
    set(rendements["notation_la_plus_elevee"])
    & set(rendements["notation_elevee"])
)

if not dates_communes:
    raise RuntimeError(
        "La BCE n'a renvoyé aucune date commune pour les deux séries."
    )


with FICHIER_SORTIE.open("w", newline="", encoding="utf-8") as fichier:
    colonnes = [
        "date",
        "rendement_notation_la_plus_elevee_pct",
        "rendement_notation_elevee_pct",
        "spread_notation_points_de_base",
    ]

    ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
    ecrivain.writeheader()

    for date in dates_communes:
        rendement_r1 = rendements["notation_la_plus_elevee"][date]
        rendement_r2 = rendements["notation_elevee"][date]

        # Un point de pourcentage correspond à 100 points de base.
        spread_points_de_base = (rendement_r2 - rendement_r1) * 100

        ecrivain.writerow({
            "date": date,
            "rendement_notation_la_plus_elevee_pct": rendement_r1,
            "rendement_notation_elevee_pct": rendement_r2,
            "spread_notation_points_de_base": spread_points_de_base,
        })


derniere_date = dates_communes[-1]
dernier_r1 = rendements["notation_la_plus_elevee"][derniere_date]
dernier_r2 = rendements["notation_elevee"][derniere_date]
dernier_spread = (dernier_r2 - dernier_r1) * 100

print(f"\nDates communes récupérées : {len(dates_communes)}")
print(f"Période : {dates_communes[0]} → {derniere_date}")
print(f"Fichier créé : {FICHIER_SORTIE}")
print(f"\nDernière date : {derniere_date}")
print(f"Rendement, notation la plus élevée : {dernier_r1:.4f} %")
print(f"Rendement, notation élevée : {dernier_r2:.4f} %")
print(f"Écart entre les rendements : {dernier_spread:.2f} points de base")