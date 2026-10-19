# Exemple pédagogique d'un calcul de SCR de spread
# pour une obligation d'entreprise fictive.

valeur_obligation_euros = 1_000_000
cqs = 1
duration_modifiee = 5.0


# Paramètres de stress de l'article 176.
# Pour chaque CQS :
# première ligne : coefficient b jusqu'à 5 ans ;
# lignes suivantes : coefficient a, puis coefficient b.
parametres_stress = {
    0: [(None, 0.009), (0.045, 0.005), (0.070, 0.005),
        (0.095, 0.005), (0.120, 0.005)],
    1: [(None, 0.011), (0.055, 0.006), (0.085, 0.005),
        (0.110, 0.005), (0.135, 0.005)],
    2: [(None, 0.014), (0.070, 0.007), (0.105, 0.005),
        (0.130, 0.005), (0.155, 0.005)],
    3: [(None, 0.025), (0.125, 0.015), (0.200, 0.010),
        (0.250, 0.010), (0.300, 0.005)],
    4: [(None, 0.045), (0.225, 0.025), (0.350, 0.018),
        (0.440, 0.005), (0.466, 0.005)],
    5: [(None, 0.075), (0.375, 0.042), (0.585, 0.005),
        (0.610, 0.005), (0.635, 0.005)],
    6: [(None, 0.075), (0.375, 0.042), (0.585, 0.005),
        (0.610, 0.005), (0.635, 0.005)],
}


def calculer_facteur_stress(cqs, duration):
    if cqs not in parametres_stress:
        raise ValueError("Le CQS doit être compris entre 0 et 6.")

    # La duration utilisée ne peut pas être inférieure à un an.
    duration = max(duration, 1.0)
    parametres = parametres_stress[cqs]

    if duration <= 5:
        facteur = parametres[0][1] * duration
    elif duration <= 10:
        a, b = parametres[1]
        facteur = a + b * (duration - 5)
    elif duration <= 15:
        a, b = parametres[2]
        facteur = a + b * (duration - 10)
    elif duration <= 20:
        a, b = parametres[3]
        facteur = a + b * (duration - 15)
    else:
        a, b = parametres[4]
        facteur = min(a + b * (duration - 20), 1.0)

    return facteur


facteur_stress = calculer_facteur_stress(cqs, duration_modifiee)
scr_spread = valeur_obligation_euros * facteur_stress

print("Exemple fictif — SCR de spread")
print(f"Valeur de l'obligation : {valeur_obligation_euros:,.2f} €")
print(f"CQS : {cqs}")
print(f"Duration modifiée : {duration_modifiee:.2f} ans")
print(f"Facteur de stress : {facteur_stress * 100:.2f} %")
print(f"SCR de spread estimé : {scr_spread:,.2f} €")