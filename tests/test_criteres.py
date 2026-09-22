"""Tests du score sur 200 points."""
from __future__ import annotations

import pytest

from ranker import criteres


def fond_vide() -> dict:
    """Tous les critères manqués (valeurs absentes)."""
    return {
        "ticker": "TEST", "debt_to_equity": None, "interest_coverage": None,
        "current_ratio": None, "shares_dilution_pct": None,
        "fcf_positif_croissance": None, "roic": None, "roe": None,
        "ca_croissance": None, "eps_croissance": None, "forward_pe": None,
        "price_to_fcf": None, "marge_brute": None, "marge_op": None,
        "marge_nette": None, "marge_ebitda": None,
    }


def fond_parfait() -> dict:
    return {
        "ticker": "TEST", "debt_to_equity": 50.0, "interest_coverage": 12.0,
        "current_ratio": 1.8, "shares_dilution_pct": -3.0,
        "fcf_positif_croissance": True, "roic": 0.18, "roe": 0.25,
        "ca_croissance": True, "eps_croissance": True, "forward_pe": 18.0,
        "price_to_fcf": 15.0, "marge_brute": 0.45, "marge_op": 0.20,
        "marge_nette": 0.15, "marge_ebitda": 0.25,
    }


def test_total_des_baremes_fait_200():
    assert criteres.SCORE_MAX == 200
    assert sum(c["points"] for c in criteres.CRITERES) == 200
    assert len(criteres.CRITERES) == 15


def test_tout_manque_donne_zero():
    resultat = criteres.evaluer(fond_vide())
    assert resultat["score"] == 0
    assert resultat["details"]["shares_dilution"] == "?"
    assert resultat["dilution_forte"] is False


def test_tout_reussi_donne_200():
    resultat = criteres.evaluer(fond_parfait())
    assert resultat["score"] == 200
    assert resultat["groupes"] == {"solidite": 60, "rentabilite": 55,
                                   "croissance": 30, "valorisation": 30,
                                   "marges": 25}


@pytest.mark.parametrize("dilution, points, forte", [
    (-10.0, 15, False),   # rachat d'actions
    (0.0, 15, False),     # limite basse
    (5.0, 8, False),      # stable
    (10.0, 8, False),     # limite stable
    (18.0, 0, False),     # modérée
    (25.0, 0, False),     # limite de la mention
    (40.0, 0, True),      # dilution forte
])
def test_paliers_de_dilution(dilution, points, forte):
    fond = fond_vide()
    fond["shares_dilution_pct"] = dilution
    resultat = criteres.evaluer(fond)
    assert resultat["score"] == points
    assert resultat["groupes"]["solidite"] == points
    assert resultat["dilution_forte"] is forte


def test_seuils_exacts():
    """Les valeurs pile au seuil suivent les règles de wheel-scanner."""
    cas = [
        ("debt_to_equity", 200.0, 0), ("debt_to_equity", 199.9, 20),
        ("interest_coverage", 5.0, 15), ("interest_coverage", 4.9, 0),
        ("current_ratio", 1.0, 10), ("current_ratio", 0.9, 0),
        ("roic", 0.08, 20), ("roic", 0.079, 0),
        ("roe", 0.10, 15), ("roe", 0.099, 0),
        ("forward_pe", 24.9, 15), ("forward_pe", 25.0, 0),
        ("forward_pe", -5.0, 0),
        ("price_to_fcf", 19.9, 15), ("price_to_fcf", 20.0, 0),
        ("marge_brute", 0.30, 10), ("marge_brute", 0.29, 0),
        ("marge_ebitda", 0.10, 5), ("marge_ebitda", 0.09, 0),
        ("marge_op", 0.01, 5), ("marge_op", -0.01, 0),
        ("marge_nette", 0.01, 5), ("marge_nette", -0.01, 0),
    ]
    for champ, valeur, attendu in cas:
        fond = fond_vide()
        fond[champ] = valeur
        score = criteres.evaluer(fond)["score"]
        assert score == attendu, f"{champ}={valeur} : {score} au lieu de {attendu}"


def test_croissance_seulement_si_vrai():
    fond = fond_vide()
    fond["ca_croissance"] = False
    fond["eps_croissance"] = None
    assert criteres.evaluer(fond)["score"] == 0
    fond["ca_croissance"] = True
    assert criteres.evaluer(fond)["score"] == 15
