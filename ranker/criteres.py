"""Les 15 critères du score fondamental sur 200 points.

Code recopié depuis ``wheel-scanner/scanner/fondamentaux.py`` (fonction
``calculer_score_fondamental``) avec les seuils de
``wheel-scanner/config.example.py``. Aucun import depuis wheel-scanner : les
deux outils évoluent séparément, cette copie est volontaire.

Ce qui N'EST PAS repris de wheel-scanner, parce qu'il s'agit de filtres de
sélection et non de qualité fondamentale :
  - exclusion des tickers de la blacklist (ici : simple mention) ;
  - filtre beta (risque de marché, pas fondamental) ;
  - planchers de score 150 / 135 / 110 ;
  - garde-fous durs du segment 200 $+ ;
  - exclusion automatique quand la dilution dépasse 25 % (ici : mention).
"""
from __future__ import annotations

VERSION_CRITERES = "1.0"

# --- Seuils (identiques à wheel-scanner/config.example.py) -----------------
DE_MAX = 200.0            # Debt/Equity en % chez yfinance : 200 = D/E 2,0
ICR_MIN = 5.0             # Interest Coverage Ratio : EBIT / intérêts
CURRENT_RATIO_MIN = 1.0
DILUTION_RACHAT_MAX = 0.0     # <= 0 % : rachats d'actions
DILUTION_STABLE_MAX = 10.0    # <= 10 % sur ~4 ans : stable
DILUTION_FORTE_MIN = 25.0     # > 25 % : mention "dilution forte"
ROIC_MIN = 0.08
ROE_MIN = 0.10
PE_MAX = 25.0             # Forward P/E
PRICE_TO_FCF_MAX = 20.0
MARGE_BRUTE_MIN = 30.0    # en %
MARGE_EBITDA_MIN = 10.0   # en %

GROUPES = {
    "solidite": 60,
    "rentabilite": 55,
    "croissance": 30,
    "valorisation": 30,
    "marges": 25,
}
SCORE_MAX = sum(GROUPES.values())  # 200

# Table de référence : sert au score, à la notice et au test de cohérence.
# "cle" est la clé utilisée dans le détail, identique à wheel-scanner.
CRITERES = [
    {"cle": "d_e", "groupe": "solidite", "points": 20,
     "nom": "Dette / fonds propres",
     "seuil_texte": "D/E inférieur à 2,0"},
    {"cle": "icr", "groupe": "solidite", "points": 15,
     "nom": "Couverture des intérêts",
     "seuil_texte": "au moins 5 fois les intérêts"},
    {"cle": "current_ratio", "groupe": "solidite", "points": 10,
     "nom": "Current ratio",
     "seuil_texte": "au moins 1,0"},
    {"cle": "shares_dilution", "groupe": "solidite", "points": 15,
     "nom": "Dilution des actions",
     "seuil_texte": "15 points si rachat (0 % ou moins), 8 points si stable (10 % ou moins)"},
    {"cle": "fcf_pos", "groupe": "rentabilite", "points": 20,
     "nom": "Flux de trésorerie libre",
     "seuil_texte": "positif et en hausse"},
    {"cle": "roic", "groupe": "rentabilite", "points": 20,
     "nom": "ROIC",
     "seuil_texte": "au moins 8 %"},
    {"cle": "roe", "groupe": "rentabilite", "points": 15,
     "nom": "ROE",
     "seuil_texte": "au moins 10 %"},
    {"cle": "ca_croiss", "groupe": "croissance", "points": 15,
     "nom": "Chiffre d'affaires",
     "seuil_texte": "en hausse sur les 3-4 dernières années"},
    {"cle": "eps_croiss", "groupe": "croissance", "points": 15,
     "nom": "Bénéfice par action",
     "seuil_texte": "positif et en hausse sur les 3-4 dernières années"},
    {"cle": "forward_pe", "groupe": "valorisation", "points": 15,
     "nom": "PER prévisionnel",
     "seuil_texte": "entre 0 et 25"},
    {"cle": "p_fcf", "groupe": "valorisation", "points": 15,
     "nom": "Cours / flux de trésorerie libre",
     "seuil_texte": "entre 0 et 20"},
    {"cle": "m_brute", "groupe": "marges", "points": 10,
     "nom": "Marge brute",
     "seuil_texte": "au moins 30 %"},
    {"cle": "m_op", "groupe": "marges", "points": 5,
     "nom": "Marge opérationnelle",
     "seuil_texte": "supérieure à 0 %"},
    {"cle": "m_nette", "groupe": "marges", "points": 5,
     "nom": "Marge nette",
     "seuil_texte": "supérieure à 0 %"},
    {"cle": "m_ebitda", "groupe": "marges", "points": 5,
     "nom": "Marge EBITDA",
     "seuil_texte": "au moins 10 %"},
]

POINTS_PAR_CLE = {c["cle"]: c["points"] for c in CRITERES}
GROUPE_PAR_CLE = {c["cle"]: c["groupe"] for c in CRITERES}


def evaluer(fond: dict) -> dict:
    """Évalue un dictionnaire de fondamentaux.

    Retourne ``{"score", "groupes", "details", "dilution_forte"}``.
    ``details`` reprend les marqueurs de wheel-scanner ("✓", "✗", "?") pour
    rester lisible et comparable.
    """
    details: dict[str, str] = {}
    gagnes: dict[str, int] = {}

    def acquis(cle: str, obtenu: bool, marque: str | None = None, points: int | None = None):
        pts = POINTS_PAR_CLE[cle] if points is None else points
        gagnes[cle] = pts if obtenu else 0
        details[cle] = marque if marque is not None else ("✓" if obtenu else "✗")

    # --- Solidité financière : 60 points ---------------------------------
    acquis("d_e", fond.get("debt_to_equity") is not None
           and fond["debt_to_equity"] < DE_MAX)

    acquis("icr", bool(fond.get("interest_coverage"))
           and fond["interest_coverage"] >= ICR_MIN)

    acquis("current_ratio", bool(fond.get("current_ratio"))
           and fond["current_ratio"] >= CURRENT_RATIO_MIN)

    dilution = fond.get("shares_dilution_pct")
    dilution_forte = False
    if dilution is None:
        gagnes["shares_dilution"] = 0
        details["shares_dilution"] = "?"
    elif dilution <= DILUTION_RACHAT_MAX:
        acquis("shares_dilution", True, "✓ rachat", 15)
    elif dilution <= DILUTION_STABLE_MAX:
        acquis("shares_dilution", True, "✓ stable", 8)
    elif dilution <= DILUTION_FORTE_MIN:
        acquis("shares_dilution", False, "✗ modérée")
    else:
        acquis("shares_dilution", False, "✗ dilution forte")
        dilution_forte = True

    # --- Rentabilité et cash : 55 points ---------------------------------
    acquis("fcf_pos", fond.get("fcf_positif_croissance") is True)
    acquis("roic", bool(fond.get("roic")) and fond["roic"] >= ROIC_MIN)
    acquis("roe", bool(fond.get("roe")) and fond["roe"] >= ROE_MIN)

    # --- Croissance : 30 points ------------------------------------------
    acquis("ca_croiss", fond.get("ca_croissance") is True)
    acquis("eps_croiss", fond.get("eps_croissance") is True)

    # --- Valorisation : 30 points ----------------------------------------
    acquis("forward_pe", bool(fond.get("forward_pe"))
           and 0 < fond["forward_pe"] < PE_MAX)
    acquis("p_fcf", bool(fond.get("price_to_fcf"))
           and 0 < fond["price_to_fcf"] < PRICE_TO_FCF_MAX)

    # --- Marges : 25 points ----------------------------------------------
    acquis("m_brute", bool(fond.get("marge_brute"))
           and fond["marge_brute"] * 100 >= MARGE_BRUTE_MIN)
    acquis("m_op", bool(fond.get("marge_op")) and fond["marge_op"] > 0)
    acquis("m_nette", bool(fond.get("marge_nette")) and fond["marge_nette"] > 0)
    acquis("m_ebitda", bool(fond.get("marge_ebitda"))
           and fond["marge_ebitda"] * 100 >= MARGE_EBITDA_MIN)

    groupes = {nom: 0 for nom in GROUPES}
    for cle, pts in gagnes.items():
        groupes[GROUPE_PAR_CLE[cle]] += pts

    return {
        "score": sum(gagnes.values()),
        "groupes": groupes,
        "details": details,
        "dilution_forte": dilution_forte,
    }
