"""Récupération des données fondamentales d'un ticker via yfinance.

Code recopié depuis ``wheel-scanner/scanner/fondamentaux.py``
(fonction ``get_fondamentaux``), avec deux ajouts sans effet sur le score :
le nom long de la société et un compteur d'essais.
"""
from __future__ import annotations

import time
import warnings

warnings.filterwarnings("ignore")


def _safe_float(val):
    """Retourne un float, ou None si la valeur est absente ou NaN."""
    if val is None:
        return None
    try:
        f = float(val)
        return None if f != f else f
    except (TypeError, ValueError):
        return None


def _valeur_etat(stmt, cles):
    """Première valeur valide trouvée parmi plusieurs libellés possibles."""
    for cle in cles:
        if cle in stmt.index:
            val = _safe_float(stmt.loc[cle].iloc[0])
            if val is not None:
                return val
    return None


def champs_vides(ticker_symbol: str) -> dict:
    return {
        "ticker": ticker_symbol, "nom": None, "prix": None, "volume_moyen": None,
        "market_cap": None, "forward_pe": None, "price_to_fcf": None,
        "roe": None, "roa": None, "roic": None,
        "marge_brute": None, "marge_op": None, "marge_nette": None,
        "marge_ebitda": None, "ca_croissance": None, "eps_croissance": None,
        "fcf_positif_croissance": None, "debt_to_equity": None,
        "current_ratio": None, "interest_coverage": None,
        "shares_dilution_pct": None, "secteur": None, "industrie": None,
        "beta": None, "erreur": None,
    }


def get_fondamentaux(ticker_symbol: str) -> dict:
    """Récupère les métriques fondamentales d'un ticker via yfinance."""
    import yfinance as yf

    fond = champs_vides(ticker_symbol)
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        fond["nom"] = info.get("longName") or info.get("shortName")
        fond["prix"] = info.get("currentPrice") or info.get("regularMarketPrice")
        fond["volume_moyen"] = info.get("averageVolume")
        fond["market_cap"] = info.get("marketCap")
        fond["forward_pe"] = info.get("forwardPE")
        fond["roe"] = info.get("returnOnEquity")
        fond["roa"] = info.get("returnOnAssets")
        fond["marge_brute"] = info.get("grossMargins")
        fond["marge_op"] = info.get("operatingMargins")
        fond["marge_nette"] = info.get("profitMargins")
        fond["marge_ebitda"] = info.get("ebitdaMargins")
        fond["debt_to_equity"] = info.get("debtToEquity")
        fond["current_ratio"] = info.get("currentRatio")
        fond["secteur"] = info.get("sector")
        fond["industrie"] = info.get("industry")
        fond["beta"] = info.get("beta")

        fcf_info = info.get("freeCashflow")
        if fcf_info and fcf_info > 0 and fond["market_cap"]:
            fond["price_to_fcf"] = fond["market_cap"] / fcf_info

        financials, balance, cashflow = None, None, None
        for nom, getter in (("financials", lambda: ticker.financials),
                            ("balance", lambda: ticker.balance_sheet),
                            ("cashflow", lambda: ticker.cashflow)):
            try:
                valeur = getter()
            except Exception:
                valeur = None
            if nom == "financials":
                financials = valeur
            elif nom == "balance":
                balance = valeur
            else:
                cashflow = valeur

        # --- Compte de résultat ------------------------------------------
        if financials is not None and not financials.empty:
            if "Total Revenue" in financials.index:
                revenus = financials.loc["Total Revenue"].dropna().tolist()
                if len(revenus) >= 3:
                    rev = list(reversed(revenus))
                    n = sum(1 for i in range(1, len(rev)) if rev[i] > rev[i - 1])
                    fond["ca_croissance"] = (n >= len(rev) - 2)

            for eps_key in ("Basic EPS", "Diluted EPS"):
                if eps_key in financials.index:
                    eps_vals = financials.loc[eps_key].dropna().tolist()
                    if len(eps_vals) >= 3:
                        eps = list(reversed(eps_vals))
                        positifs = all(e > 0 for e in eps)
                        n = sum(1 for i in range(1, len(eps)) if eps[i] > eps[i - 1])
                        fond["eps_croissance"] = (positifs and n >= len(eps) - 2)
                    break

            ebit = _valeur_etat(financials, ["EBIT", "Operating Income", "Operating Income Loss"])
            interet = _valeur_etat(financials, ["Interest Expense", "Interest Expense Non Operating"])
            if ebit is not None and interet:
                fond["interest_coverage"] = round(ebit / abs(interet), 1)

            for cle in ("Ordinary Shares Number", "Basic Average Shares",
                        "Diluted Average Shares", "Share Issued"):
                if cle in financials.index:
                    vals = financials.loc[cle].dropna().tolist()
                    if len(vals) >= 2:
                        chrono = list(reversed(vals))
                        ancien, recent = chrono[0], chrono[-1]
                        if ancien > 0:
                            fond["shares_dilution_pct"] = round((recent - ancien) / ancien * 100, 1)
                    break

        # --- Bilan : ROIC -------------------------------------------------
        if (financials is not None and not financials.empty
                and balance is not None and not balance.empty):
            op_income = _valeur_etat(financials, ["Operating Income", "EBIT", "Operating Income Loss"])

            taux_impot = 0.21
            avant_impot = _valeur_etat(financials, ["Pretax Income", "Pretax Income Loss Adjustments"])
            impot = _valeur_etat(financials, ["Tax Provision", "Tax Effect Of Unusual Items"])
            if avant_impot and avant_impot > 0 and impot is not None:
                taux_impot = min(max(abs(impot / avant_impot), 0), 0.40)

            if op_income is not None:
                nopat = op_income * (1 - taux_impot)
                fonds_propres = _valeur_etat(balance, [
                    "Total Stockholder Equity", "Stockholders Equity", "Common Stock Equity"])
                dette = _valeur_etat(balance, [
                    "Total Debt", "Long Term Debt",
                    "Long Term Debt And Capital Lease Obligation"]) or 0
                tresorerie = _valeur_etat(balance, [
                    "Cash And Cash Equivalents",
                    "Cash Cash Equivalents And Short Term Investments"]) or 0
                if fonds_propres is not None:
                    capital_investi = fonds_propres + dette - tresorerie
                    if capital_investi > 0:
                        fond["roic"] = round(nopat / capital_investi, 4)

        # --- Flux de trésorerie : FCF et cours/FCF de secours --------------
        if cashflow is not None and not cashflow.empty:
            fcf_vals = []
            cles_fcf = ["Free Cash Flow", "FreeCashFlow",
                        "Free Cash Flow From Continuing Operations"]
            cle_fcf = next((k for k in cles_fcf if k in cashflow.index), None)

            if cle_fcf:
                fcf_vals = [_safe_float(v) for v in cashflow.loc[cle_fcf].tolist()
                            if _safe_float(v) is not None]
            else:
                cles_opcf = ["Operating Cash Flow",
                             "Cash Flow From Continuing Operating Activities",
                             "Net Cash Provided By Operating Activities",
                             "Cash Flows From Used In Operating Activities"]
                cles_capex = ["Capital Expenditure", "Capital Expenditures",
                              "Purchase Of Property Plant And Equipment",
                              "Capital Expenditure Reported", "Acquisition Of Business"]
                cle_opcf = next((k for k in cles_opcf if k in cashflow.index), None)
                cle_capex = next((k for k in cles_capex if k in cashflow.index), None)
                if cle_opcf and cle_capex:
                    for col in cashflow.columns:
                        opcf_v = _safe_float(cashflow.loc[cle_opcf, col])
                        capex_v = _safe_float(cashflow.loc[cle_capex, col])
                        if opcf_v is not None and capex_v is not None:
                            fcf_vals.append(opcf_v + capex_v if capex_v < 0 else opcf_v - capex_v)

            if fcf_vals:
                if fond["price_to_fcf"] is None and fond["market_cap"] and fcf_vals[0] > 0:
                    fond["price_to_fcf"] = round(fond["market_cap"] / fcf_vals[0], 1)
                if len(fcf_vals) >= 3:
                    chrono = list(reversed(fcf_vals))
                    positifs = all(f > 0 for f in chrono)
                    n = sum(1 for i in range(1, len(chrono)) if chrono[i] > chrono[i - 1])
                    fond["fcf_positif_croissance"] = (positifs and n >= len(chrono) - 2)

    except Exception as e:
        fond["erreur"] = str(e)[:150]
    return fond


def get_fondamentaux_avec_essais(ticker_symbol: str, essais: int = 2,
                                 pause: float = 0.4) -> dict:
    """Appelle ``get_fondamentaux`` jusqu'à ``essais`` fois.

    Un ticker en erreur n'arrête jamais le calcul : le dernier résultat est
    renvoyé tel quel, champ ``erreur`` rempli.
    """
    fond = None
    for tentative in range(1, essais + 1):
        fond = get_fondamentaux(ticker_symbol)
        if not fond["erreur"] and fond["prix"] is not None:
            return fond
        if tentative < essais:
            time.sleep(pause * 2)
    return fond
