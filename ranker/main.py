"""Calcule le classement fondamental et écrit ``classement/classement.json``.

Utilisation :
    python -m ranker.main                 # tout l'univers
    python -m ranker.main --limite 10     # essai rapide sur 10 tickers
    python -m ranker.main --sortie autre/chemin.json

Garde-fou : si l'univers compte moins de ``UNIVERS_MIN`` tickers ou si plus de
``TAUX_ERREUR_MAX`` des tickers sont en erreur, le fichier existant n'est PAS
écrasé et le script sort en code 1. Mieux vaut un classement de la semaine
passée qu'un classement faux.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

from ranker import criteres
from ranker.blacklist import est_blacklist

SORTIE_PAR_DEFAUT = os.path.join("classement", "classement.json")
UNIVERS_MIN = 400
TAUX_ERREUR_MAX = 0.20
PAUSE_ENTRE_TICKERS = 0.4


# ---------------------------------------------------------------------------
# Construction des lignes du classement
# ---------------------------------------------------------------------------

def construire_entree(fond: dict) -> dict:
    """Transforme un dictionnaire de fondamentaux en ligne de classement."""
    evaluation = criteres.evaluer(fond)
    return {
        "ticker": fond.get("ticker"),
        "nom": fond.get("nom"),
        "secteur": fond.get("secteur"),
        "industrie": fond.get("industrie"),
        "prix": fond.get("prix"),
        "market_cap": fond.get("market_cap"),
        "score": evaluation["score"],
        "groupes": evaluation["groupes"],
        "details": evaluation["details"],
        "valeurs": {
            "debt_to_equity": fond.get("debt_to_equity"),
            "interest_coverage": fond.get("interest_coverage"),
            "current_ratio": fond.get("current_ratio"),
            "shares_dilution_pct": fond.get("shares_dilution_pct"),
            "fcf_positif_croissance": fond.get("fcf_positif_croissance"),
            "roic": fond.get("roic"),
            "roe": fond.get("roe"),
            "ca_croissance": fond.get("ca_croissance"),
            "eps_croissance": fond.get("eps_croissance"),
            "forward_pe": fond.get("forward_pe"),
            "price_to_fcf": fond.get("price_to_fcf"),
            "marge_brute": fond.get("marge_brute"),
            "marge_op": fond.get("marge_op"),
            "marge_nette": fond.get("marge_nette"),
            "marge_ebitda": fond.get("marge_ebitda"),
            "beta": fond.get("beta"),
        },
        "blacklist": est_blacklist(fond.get("ticker") or ""),
        "dilution_forte": evaluation["dilution_forte"],
        "erreur": fond.get("erreur"),
    }


def classer(entrees: list[dict]) -> list[dict]:
    """Trie par score décroissant, puis par ticker, et numérote les rangs.

    Deux sociétés à égalité de score partagent le même rang ; le rang suivant
    tient compte des ex æquo (1, 2, 2, 4).
    """
    ordonnees = sorted(entrees, key=lambda e: (-e["score"], e["ticker"] or ""))
    rang, precedent = 0, None
    for position, entree in enumerate(ordonnees, start=1):
        if entree["score"] != precedent:
            rang = position
            precedent = entree["score"]
        entree["rang"] = rang
    return ordonnees


def controler(entrees: list[dict], nb_univers: int, limite: int | None) -> tuple[bool, str]:
    """Garde-fou avant écriture. Retourne ``(ok, raison)``."""
    if limite is None and nb_univers < UNIVERS_MIN:
        return False, (f"univers incomplet : {nb_univers} tickers "
                       f"(minimum attendu {UNIVERS_MIN})")
    if not entrees:
        return False, "aucun ticker calculé"
    erreurs = sum(1 for e in entrees if e.get("erreur"))
    taux = erreurs / len(entrees)
    if taux > TAUX_ERREUR_MAX:
        return False, (f"trop d'erreurs : {erreurs}/{len(entrees)} "
                       f"({taux:.0%}, maximum {TAUX_ERREUR_MAX:.0%})")
    return True, ""


def ecrire_json(chemin: str, contenu: dict) -> None:
    """Écriture atomique : fichier temporaire puis remplacement."""
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as f:
        json.dump(contenu, f, ensure_ascii=False, indent=1, default=str)
    os.replace(temporaire, chemin)


def construire_document(entrees: list[dict], indices_manques: list[str],
                        nb_univers: int) -> dict:
    erreurs = sum(1 for e in entrees if e.get("erreur"))
    return {
        "meta": {
            "date_calcul": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "nb_tickers": len(entrees),
            "nb_erreurs": erreurs,
            "nb_univers": nb_univers,
            "indices_manques": indices_manques,
            "version_criteres": criteres.VERSION_CRITERES,
            "score_max": criteres.SCORE_MAX,
            "groupes": criteres.GROUPES,
        },
        "tickers": entrees,
    }


# ---------------------------------------------------------------------------
# Programme
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classement fondamental S&P 500 + Nasdaq 100")
    parser.add_argument("--limite", type=int, default=None,
                        help="ne calculer que les N premiers tickers (essai)")
    parser.add_argument("--sortie", default=SORTIE_PAR_DEFAUT)
    parser.add_argument("--univers", choices=["les-deux", "sp500", "nq100"],
                        default="les-deux")
    args = parser.parse_args(argv)

    from ranker.fondamentaux import get_fondamentaux_avec_essais
    from ranker.univers import charger_univers

    debut = time.time()
    tickers, indices_manques = charger_univers(args.univers)
    nb_univers = len(tickers)
    if args.limite:
        tickers = tickers[:args.limite]
        print(f"Mode essai : {len(tickers)} tickers")

    entrees = []
    total = len(tickers)
    for i, ticker in enumerate(tickers, start=1):
        fond = get_fondamentaux_avec_essais(ticker)
        entree = construire_entree(fond)
        entrees.append(entree)
        marque = " ERREUR" if entree["erreur"] else ""
        print(f"  [{i}/{total}] {ticker} : {entree['score']}/200{marque}", flush=True)
        time.sleep(PAUSE_ENTRE_TICKERS)

    ok, raison = controler(entrees, nb_univers, args.limite)
    if not ok:
        print(f"\nREFUS D'ÉCRITURE — {raison}")
        print("Le fichier existant est conservé tel quel.")
        return 1

    document = construire_document(classer(entrees), indices_manques, nb_univers)
    ecrire_json(args.sortie, document)
    duree = (time.time() - debut) / 60
    print(f"\n{args.sortie} écrit : {len(entrees)} tickers, "
          f"{document['meta']['nb_erreurs']} erreurs, {duree:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
