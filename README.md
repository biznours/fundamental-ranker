# fundamental-ranker

Classement fondamental hebdomadaire des sociétés du S&P 500 et du Nasdaq 100,
de la plus solide à la plus faible. Score sur 200 points, 15 critères.

Le classement est lu par l'onglet **Scanner → Scanner fondamental** de
wheel-suite. La notice destinée aux utilisateurs est dans
[NOTICE_CLASSEMENT.md](NOTICE_CLASSEMENT.md).

## Ce dépôt ne touche pas à wheel-scanner

`wheel-scanner` sert uniquement de spécification. Son code n'est ni importé ni
modifié. Les 15 critères et leurs seuils sont recopiés dans
`ranker/criteres.py`, et ils sont volontairement **sans** les filtres de
sélection du scanner : pas d'exclusion par la blacklist (simple mention), pas
de filtre beta, pas de plancher 150 / 135 / 110, pas de garde-fou 200 $+, pas
d'exclusion pour dilution supérieure à 25 % (simple mention).

## Fonctionnement

1. `ranker/univers.py` lit les listes S&P 500 et Nasdaq 100 sur Wikipedia
   (environ 515 tickers sans doublons).
2. `ranker/fondamentaux.py` récupère les données de chaque société via
   yfinance (2 essais par ticker, une erreur n'arrête jamais le calcul).
3. `ranker/criteres.py` calcule le score sur 200 et les points par groupe.
4. `ranker/main.py` classe, contrôle, puis écrit `classement/classement.json`.

**Garde-fou** : si l'univers compte moins de 400 tickers, ou si plus de 20 %
des tickers sont en erreur, le fichier existant n'est pas écrasé et le script
sort en erreur. Un classement de la semaine passée vaut mieux qu'un classement
faux.

## Lancer en local (PowerShell, Windows)

```
cd "C:\Users\biznours\Desktop\important juin  2026\codage bourse\fundamental-ranker"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest
pytest -q
python -m ranker.main --limite 10
```

Sans `--limite`, le calcul porte sur tout l'univers.

## Automatisation

`.github/workflows/classement.yml` : chaque lundi à 06:00 UTC (8h à Paris
l'été, 7h l'hiver), plus un déclenchement manuel possible depuis l'onglet
Actions. Le workflow lance les tests, calcule le classement et enregistre
`classement/classement.json` seulement s'il a changé. Aucun secret n'est
nécessaire.

## Le fichier produit

```
{
  "meta": {
    "date_calcul", "nb_tickers", "nb_erreurs", "nb_univers",
    "indices_manques", "version_criteres", "score_max", "groupes"
  },
  "tickers": [
    {
      "rang", "ticker", "nom", "secteur", "industrie", "prix", "market_cap",
      "score",        // sur 200
      "groupes",      // solidite/60, rentabilite/55, croissance/30,
                      // valorisation/30, marges/25
      "details",      // ✓ / ✗ / ? par critère
      "valeurs",      // valeurs brutes (ROIC, PER, marges, dilution...)
      "blacklist", "dilution_forte", "erreur"
    }
  ]
}
```

Les ex æquo partagent le même rang (1, 2, 2, 4).
