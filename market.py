"""
InvestIA PRO - Módulo de Coleta e Normalização de Dados de Mercado
"""
import yfinance as yf
import pandas as pd
import time
from utils import format_ticker

def fetch_asset_data(ticker: str, period: str = "1y") -> dict:
    """
    Busca cotações e histórico do ativo via yfinance.
    Retorna estrutura padronizada para evitar KeyError nos módulos posteriores.
    """
    formatted_symbol = format_ticker(ticker)
    result = {
        "asset": formatted_symbol,
        "original_symbol": ticker,
        "price": None,
        "change_percent": 0.0,
        "previous_close": None,
        "history": pd.DataFrame(),
        "error": None,
        "is_valid": False
    }

    try:
        ticker_obj = yf.Ticker(formatted_symbol)
        df = ticker_obj.history(period=period)

        if df.empty or len(df) < 5:
            # Segunda tentativa com sufixo bruto se falhou com .SA
            if formatted_symbol != ticker:
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period=period)

        if df.empty or len(df) < 5:
            result["error"] = f"Dados insuficientes ou ativo não encontrado para: {ticker}"
            return result

        # Trata timezone se presente no index
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        current_price = float(df["Close"].iloc[-1])
        prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100.0 if prev_price else 0.0

        result["price"] = round(current_price, 2)
        result["previous_close"] = round(prev_price, 2)
        result["change_percent"] = round(change_pct, 2)
        result["history"] = df
        result["is_valid"] = True

    except Exception as e:
        err_msg = str(e)
        if "Too Many Requests" in err_msg or "Rate Limit" in err_msg:
            result["error"] = "Limite de requisições excedido no yfinance. Aguarde alguns instantes."
        else:
            result["error"] = f"Erro ao acessar dados de {ticker}: {err_msg}"

    return result
