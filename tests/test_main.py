"""Tests du classement, du garde-fou et du fichier produit."""
from __future__ import annotations

import json

from ranker import main
from tests.test_criteres import fond_parfait, fond_vide


def entree(ticker: str, score_parfait: bool = False, erreur: str | None = None) -> dict:
    fond = fond_parfait() if score_parfait else fond_vide()
    fond["ticker"] = ticker
    fond["erreur"] = erreur
    fond["nom"] = f"Société {ticker}"
    return main.construire_entree(fond)


def test_entree_contient_les_champs_attendus():
    e = entree("AAPL", score_parfait=True)
    assert e["score"] == 200
    assert e["blacklist"] is False
    assert e["valeurs"]["roic"] == 0.18
    assert e["groupes"]["solidite"] == 60


def test_mention_blacklist():
    assert entree("MSTR")["blacklist"] is True
    assert entree("AAPL")["blacklist"] is False


def test_rangs_avec_ex_aequo():
    entrees = [entree("AAA"), entree("BBB", score_parfait=True),
               entree("CCC", score_parfait=True), entree("DDD")]
    classees = main.classer(entrees)
    assert [e["ticker"] for e in classees] == ["BBB", "CCC", "AAA", "DDD"]
    assert [e["rang"] for e in classees] == [1, 1, 3, 3]


def test_garde_fou_univers_incomplet():
    ok, raison = main.controler([entree("AAA")], nb_univers=120, limite=None)
    assert ok is False
    assert "univers incomplet" in raison


def test_garde_fou_ignore_en_mode_essai():
    ok, _ = main.controler([entree("AAA")], nb_univers=10, limite=10)
    assert ok is True


def test_garde_fou_trop_d_erreurs():
    entrees = [entree(f"T{i}", erreur="réseau") for i in range(3)]
    entrees += [entree(f"U{i}") for i in range(7)]
    ok, raison = main.controler(entrees, nb_univers=500, limite=None)
    assert ok is False
    assert "erreurs" in raison


def test_garde_fou_accepte_peu_d_erreurs():
    entrees = [entree("T0", erreur="réseau")] + [entree(f"U{i}") for i in range(19)]
    ok, _ = main.controler(entrees, nb_univers=500, limite=None)
    assert ok is True


def test_ecriture_et_structure_du_json(tmp_path):
    entrees = main.classer([entree("AAA", score_parfait=True), entree("BBB")])
    document = main.construire_document(entrees, indices_manques=[], nb_univers=503)
    chemin = tmp_path / "sous-dossier" / "classement.json"
    main.ecrire_json(str(chemin), document)

    relu = json.loads(chemin.read_text(encoding="utf-8"))
    assert relu["meta"]["nb_tickers"] == 2
    assert relu["meta"]["score_max"] == 200
    assert relu["meta"]["version_criteres"]
    assert relu["meta"]["date_calcul"].endswith("+00:00")
    assert relu["tickers"][0]["ticker"] == "AAA"
    assert relu["tickers"][0]["rang"] == 1
    assert not list(chemin.parent.glob("*.tmp"))


def test_ecriture_remplace_sans_laisser_de_temporaire(tmp_path):
    chemin = tmp_path / "classement.json"
    main.ecrire_json(str(chemin), {"meta": {}, "tickers": []})
    main.ecrire_json(str(chemin), {"meta": {"nb_tickers": 1}, "tickers": []})
    relu = json.loads(chemin.read_text(encoding="utf-8"))
    assert relu["meta"]["nb_tickers"] == 1
