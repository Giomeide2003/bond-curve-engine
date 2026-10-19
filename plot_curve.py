import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt


# Trouver la base de données à côté de ce fichier
dossier_projet = Path(__file__).resolve().parent
fichier_base = dossier_projet / "bond_curve.db"

# Lire les deux dates les plus récentes dans la base
with sqlite3.connect(fichier_base) as connexion:
    resultats_dates = connexion.execute("""
        SELECT DISTINCT observation_date
        FROM yield_curve
        ORDER BY observation_date DESC
        LIMIT 2
    """).fetchall()

    if len(resultats_dates) < 2:
        raise RuntimeError(
            "La base doit contenir au moins deux dates pour comparer les courbes."
        )

    # Mettre les dates dans l'ordre chronologique pour le graphique
    dates = sorted(resultat[0] for resultat in resultats_dates)

    courbes = []

    for date in dates:
        points = connexion.execute("""
            SELECT maturity_years, spot_rate_percent
            FROM yield_curve
            WHERE observation_date = ?
            ORDER BY maturity_years
        """, (date,)).fetchall()

        courbes.append((date, points))

# Tracer les deux courbes récupérées depuis SQL
for date, points in courbes:
    maturites = [point[0] for point in points]
    taux = [point[1] for point in points]

    plt.plot(maturites, taux, marker="o", label=date)

plt.title("Comparaison des courbes de taux spot AAA")
plt.xlabel("Maturité (années)")
plt.ylabel("Taux spot (% par an)")
plt.xticks([1, 2, 5, 10])
plt.grid(True)
plt.legend(title="Date")
plt.tight_layout()
plt.show()