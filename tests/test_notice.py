"""La notice doit rester synchronisée avec les critères du code.

Si un seuil ou un barème change dans ``ranker/criteres.py`` sans être corrigé
dans ``NOTICE_CLASSEMENT.md``, ce test échoue.
"""
from __future__ import annotations

import os

from ranker import criteres

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_NOTICE = os.path.join(RACINE, "NOTICE_CLASSEMENT.md")


def lire_notice() -> str:
    with open(CHEMIN_NOTICE, encoding="utf-8") as f:
        return f.read()


def test_la_notice_existe():
    assert os.path.exists(CHEMIN_NOTICE)


def test_chaque_critere_est_decrit():
    notice = lire_notice()
    for critere in criteres.CRITERES:
        assert critere["nom"] in notice, f"critère absent de la notice : {critere['nom']}"
        assert critere["seuil_texte"] in notice, (
            f"seuil absent ou différent dans la notice : {critere['nom']} "
            f"({critere['seuil_texte']})")


def test_chaque_bareme_de_groupe_est_annonce():
    notice = lire_notice()
    libelles = {
        "solidite": "Solidité financière — 60 points",
        "rentabilite": "Rentabilité et trésorerie — 55 points",
        "croissance": "Croissance — 30 points",
        "valorisation": "Valorisation — 30 points",
        "marges": "Marges — 25 points",
    }
    for groupe, points in criteres.GROUPES.items():
        titre = libelles[groupe]
        assert titre in notice, f"titre de groupe absent : {titre}"
        assert str(points) in titre, f"barème du groupe {groupe} désynchronisé"


def test_mentions_expliquees():
    notice = lire_notice()
    assert "blacklist" in notice
    assert "dilution forte" in notice
    assert f"{criteres.DILUTION_FORTE_MIN:.0f} %" in notice
