# Comment lire le classement fondamental

## À quoi sert ce classement

Il range les sociétés du S&P 500 et du Nasdaq 100, de la plus solide
financièrement à la plus faible, d'après leurs comptes publiés. Environ 515
sociétés y figurent.

Ce n'est **pas** un signal d'achat, **pas** une sélection d'options, et **pas**
un conseil en investissement. C'est un point de départ pour savoir sur quelles
entreprises on travaille.

## D'où viennent les chiffres

Les données viennent de Yahoo Finance : les indicateurs du jour et les comptes
annuels des trois ou quatre dernières années. Le classement est recalculé
**chaque lundi matin**. La date du calcul est affichée en haut de l'écran :
regarde-la toujours avant de t'en servir.

## Le score sur 200 points

Quinze critères, répartis en cinq groupes.

### Solidité financière — 60 points

| Critère | Ce qu'il mesure | Seuil | Points |
|---|---|---|---|
| Dette / fonds propres | Le poids de la dette face aux capitaux des actionnaires | D/E inférieur à 2,0 | 20 |
| Couverture des intérêts | Combien de fois le bénéfice d'exploitation paie les intérêts de la dette | au moins 5 fois les intérêts | 15 |
| Current ratio | La capacité à payer ce qui est dû dans l'année | au moins 1,0 | 10 |
| Dilution des actions | Si la société rachète ses actions ou en crée de nouvelles, ce qui dilue les actionnaires | 15 points si rachat (0 % ou moins), 8 points si stable (10 % ou moins) | 15 |

### Rentabilité et trésorerie — 55 points

| Critère | Ce qu'il mesure | Seuil | Points |
|---|---|---|---|
| Flux de trésorerie libre | Le cash réellement gagné, une fois les investissements payés | positif et en hausse | 20 |
| ROIC | Ce que rapporte chaque euro de capital engagé dans l'activité | au moins 8 % | 20 |
| ROE | Ce que rapportent les capitaux des actionnaires | au moins 10 % | 15 |

### Croissance — 30 points

| Critère | Ce qu'il mesure | Seuil | Points |
|---|---|---|---|
| Chiffre d'affaires | Si les ventes progressent | en hausse sur les 3-4 dernières années | 15 |
| Bénéfice par action | Si le bénéfice revenant à chaque action progresse | positif et en hausse sur les 3-4 dernières années | 15 |

### Valorisation — 30 points

| Critère | Ce qu'il mesure | Seuil | Points |
|---|---|---|---|
| PER prévisionnel | Le prix payé pour les bénéfices attendus | entre 0 et 25 | 15 |
| Cours / flux de trésorerie libre | Le prix payé pour le cash généré | entre 0 et 20 | 15 |

### Marges — 25 points

| Critère | Ce qu'il mesure | Seuil | Points |
|---|---|---|---|
| Marge brute | Le pouvoir de fixer ses prix | au moins 30 % | 10 |
| Marge opérationnelle | Si l'activité elle-même gagne de l'argent | supérieure à 0 % | 5 |
| Marge nette | Ce qui reste une fois tout payé | supérieure à 0 % | 5 |
| Marge EBITDA | La rentabilité avant amortissements et charges financières | au moins 10 % | 5 |

**Important :** chaque critère est en tout ou rien. Une société juste au-dessus
du seuil gagne autant de points qu'une société très au-dessus, et une société
juste en dessous n'en gagne aucun. Seule la dilution a trois paliers. Deux
sociétés au même score peuvent donc avoir des profils très différents : regarde
les points par groupe, pas seulement le total.

## Repères de lecture

Ce sont des repères, pas des recommandations.

- **170 et plus** : très peu de sociétés y arrivent. Bilan solide, cash
  abondant, valorisation encore raisonnable.
- **150 à 169** : profil solide. C'est le niveau que le scanner wheel exige
  avant même de regarder les options.
- **110 à 149** : profil correct mais avec des faiblesses nettes. Regarde
  quel groupe fait chuter le score.
- **moins de 110** : beaucoup de critères manqués, ou beaucoup de données
  absentes. À creuser à la main avant toute décision.

## Les mentions

- **blacklist** : ticker que le scanner wheel écarte pour des raisons de
  risque (crypto, ETF à levier, sociétés chinoises, biotechs de vaccins,
  cannabis, actions « meme », véhicules électriques spéculatifs). Il reste
  classé ici, pour information.
- **dilution forte** : plus de 25 % d'actions supplémentaires en environ
  quatre ans. Ta part du gâteau diminue d'autant.

## Limites à connaître

- Les données Yahoo sont parfois absentes ou fausses. **Un critère sans donnée
  vaut zéro point**, ce qui pénalise la société sans que ce soit mérité.
- **Banques, assurances et foncières (REIT) sont structurellement pénalisées** :
  la marge brute, le current ratio et le ratio dette / fonds propres n'ont pas
  le même sens pour elles. Un score bas n'y veut pas dire grand-chose.
- Les comptes sont annuels : ils ont donc du retard sur les derniers
  trimestres.
- Le classement ignore complètement le prix des options, la volatilité,
  l'actualité de la société et les résultats à venir.

## Différence avec le Scanner wheel-suite

Le **Scanner** cherche des opportunités d'options pour la journée : il filtre
sévèrement, applique la blacklist, le beta, un score minimum, et ne garde
qu'une poignée de lignes.

Le **Classement fondamental** ne filtre rien et ne sélectionne rien. Il montre
la qualité fondamentale de toutes les sociétés, y compris celles que le scanner
écarte.

## Tris et filtres

*(section à compléter quand l'écran sera en place dans wheel-suite)*

- **Score total** : le classement par défaut, du plus solide au plus faible.
- **Solidité**, **Rentabilité**, **Croissance**, **Valorisation**, **Marges** :
  classe sur un seul groupe. Utile pour trouver, par exemple, les sociétés les
  moins endettées sans regarder le reste.
- **ROIC**, **marge brute**, **PER prévisionnel**, **capitalisation** : classe
  sur une valeur brute, sans passer par les points.
- **Ordre alphabétique** : pour retrouver un ticker.
- **Filtre par secteur** : compare ce qui est comparable ; les scores moyens
  diffèrent beaucoup d'un secteur à l'autre.
- **Recherche** : affiche un ticker précis.
- **Score minimum** : masque tout ce qui est sous un seuil choisi.
- **Masquer la blacklist** : retire les tickers que le scanner wheel écarte.
