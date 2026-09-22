"""Blacklist du scanner wheel, reprise ici comme simple mention.

Dans ``wheel-scanner`` ces tickers sont retirés de l'univers avant tout
calcul. Ici, ils sont calculés et classés normalement : le classement montre
la qualité fondamentale, il ne sélectionne rien. La mention permet de se
rappeler pourquoi le scanner d'options les écarte (crypto, ETF à levier,
Chine, biotechs vaccins, cannabis, actions « meme », véhicules électriques
spéculatifs).

Copie de ``BLACKLIST_TICKERS`` (wheel-scanner/config.example.py). À
resynchroniser à la main si la liste bouge là-bas.
"""
from __future__ import annotations

BLACKLIST_TICKERS = [
    "MSTR", "COIN", "MARA", "RIOT", "HUT", "CLSK", "BITF", "HIVE", "BITO",
    "TQQQ", "SQQQ", "SOXL", "SOXS", "SPXL", "SPXS", "TNA", "TZA",
    "UVXY", "VXX", "SVXY", "FNGU", "FNGD", "TMF", "TMV",
    "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "TME", "BILI",
    "NTES", "TAL", "EDU", "IQ", "VIPS", "WB",
    "MRNA", "BNTX", "NVAX", "OCGN", "INO", "VXRT",
    "TLRY", "CGC", "ACB", "CRON", "SNDL", "HEXO",
    "GME", "AMC", "BBBY", "BB", "KOSS", "EXPR",
    "RIVN", "LCID", "NKLA", "FSR", "GOEV", "RIDE",
    "SMCI", "PSKY",
]

_ENSEMBLE = set(BLACKLIST_TICKERS)


def est_blacklist(ticker: str) -> bool:
    return ticker in _ENSEMBLE
