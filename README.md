
# Bond Curve Engine

Projet pédagogique d’analyse des courbes de taux souveraines AAA de la zone euro à partir des données de la Banque centrale européenne (BCE).

## Objectif

Construire progressivement un programme Python qui récupère et analyse les taux d’intérêt selon la durée des obligations, de quelques mois à plusieurs années.

Une courbe de taux aide à comparer le coût d’emprunt à différentes échéances. Sa forme évolue avec les conditions économiques et les attentes du marché.

## Source des données

Les données proviendront du [portail de données de la BCE](https://data.ecb.europa.eu/methodology/yield-curves).

La BCE publie plusieurs types de courbes, dont une courbe fondée sur les obligations souveraines des pays de la zone euro notés AAA. Le projet commencera par cette courbe de référence et se concentrera sur les taux « spot », aussi appelés taux zéro-coupon.

## Étapes prévues

1. Comprendre les maturités et les taux présents dans les données.
2. Récupérer une première observation auprès de la BCE.
3. Récupérer plusieurs maturités pour une même date.
4. Tracer la courbe de taux.
5. Comparer son évolution entre plusieurs dates.
6. Étudier ensuite des mesures de risque obligataire, comme la duration et la sensibilité aux variations de taux.

## État du projet

Le dépôt GitHub a été créé et cloné dans VS Code. Le README est le premier fichier du projet. Le programme d’analyse n’a pas encore été commencé.

## Avertissement

Ce projet sert à apprendre l’analyse quantitative et la programmation. Il ne fournit pas de conseil en investissement et ne passe aucun ordre.