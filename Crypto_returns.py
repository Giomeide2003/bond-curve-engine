import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


dossier_projet = Path(__file__).resolve().parent
fichier_sortie = dossier_projet / "crypto_returns.csv"
symboles = ["BTCUSDT", "ETHUSDT"]

rendements_par_actif = {}

for symbole in symboles:
    parametres = urlencode({
        "symbol": symbole,
        "interval": "1d",
        "limit": "500",
    })

    url = (
        "https://data-api.binance.vision/api/v3/klines?"
        f"{parametres}"
    )

    requete = Request(
        url,
        headers={"User-Agent": "Bond-Curve-Engine"},
    )

    with urlopen(requete, timeout=30) as reponse:
        bougies = json.loads(reponse.read().decode("utf-8"))

    maintenant_ms = int(time.time() * 1000)
    clotures = []

    for bougie in bougies:
        heure_ouverture_ms = int(bougie[0])
        heure_cloture_ms = int(bougie[6])

        # Ignorer la bougie du jour si elle n'est pas encore terminée
        if heure_cloture_ms >= maintenant_ms:
            continue

        date = datetime.fromtimestamp(
            heure_ouverture_ms / 1000,
            tz=timezone.utc,
        ).date().isoformat()

        prix_cloture = float(bougie[4])
        clotures.append((date, prix_cloture))

    # 366 clôtures permettent de calculer 365 variations
    clotures = clotures[-366:]

    rendements = {}

    for index in range(1, len(clotures)):
        date = clotures[index][0]
        cloture_precedente = clotures[index - 1][1]
        cloture_actuelle = clotures[index][1]

        rendement_pct = (
            (cloture_actuelle / cloture_precedente) - 1
        ) * 100

        rendements[date] = rendement_pct

    rendements_par_actif[symbole] = rendements

dates_communes = sorted(
    set(rendements_par_actif["BTCUSDT"])
    & set(rendements_par_actif["ETHUSDT"])
)

with fichier_sortie.open("w", newline="", encoding="utf-8") as fichier:
    ecrivain = csv.writer(fichier)
    ecrivain.writerow([
        "date",
        "BTCUSDT_return_pct",
        "ETHUSDT_return_pct",
    ])

    for date in dates_communes:
        ecrivain.writerow([
            date,
            round(rendements_par_actif["BTCUSDT"][date], 8),
            round(rendements_par_actif["ETHUSDT"][date], 8),
        ])

print(f"Dates communes : {len(dates_communes)}")
if dates_communes:
    print(f"Période : {dates_communes[0]} → {dates_communes[-1]}")
print(f"Fichier créé : {fichier_sortie}")