"""Univers : S&P 500 + Nasdaq 100, lus sur Wikipedia.

Même méthode que ``wheel-scanner/scanner/scanner.py`` (``get_index_tickers``) :
même User-Agent, même conversion des points en tirets (BRK.B -> BRK-B), même
tolérance en cas d'échec.
"""
from __future__ import annotations

from io import StringIO

URL_SP500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
URL_NQ100 = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def tickers_indice(url: str, nom_indice: str) -> tuple[list[str], bool]:
    """Retourne ``(tickers, ok)``. Liste vide et ``False`` si la page échoue."""
    import pandas as pd
    import requests

    print(f"Téléchargement de la liste {nom_indice}...")
    try:
        reponse = requests.get(url, headers={"User-Agent": _USER_AGENT}, timeout=15)
        reponse.raise_for_status()
        tables = pd.read_html(StringIO(reponse.text))
        for table in tables:
            for colonne in ("Symbol", "Ticker"):
                if colonne in table.columns:
                    tickers = [str(x).replace(".", "-") for x in table[colonne].tolist()]
                    print(f"  {len(tickers)} tickers {nom_indice}")
                    return tickers, True
        print(f"  {nom_indice} : aucune colonne Symbol/Ticker reconnue")
        return [], False
    except Exception as e:
        print(f"  {nom_indice} inaccessible ({e})")
        return [], False


def charger_univers(quoi: str = "les-deux") -> tuple[list[str], list[str]]:
    """Retourne ``(tickers sans doublons, indices manqués)``."""
    manques: list[str] = []
    tickers: list[str] = []

    if quoi in ("les-deux", "sp500"):
        sp500, ok = tickers_indice(URL_SP500, "S&P 500")
        if not ok:
            manques.append("S&P 500")
        tickers += sp500

    if quoi in ("les-deux", "nq100"):
        nq100, ok = tickers_indice(URL_NQ100, "Nasdaq 100")
        if not ok:
            manques.append("Nasdaq 100")
        tickers += nq100

    tickers = list(dict.fromkeys(tickers))
    print(f"Univers : {len(tickers)} tickers uniques")
    return tickers, manques
