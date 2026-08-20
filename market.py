"""
InvestIA PRO
Módulo de Mercado e Dados Fundamentalistas

Versão: v0.7
Fase: 3.0.1 - Coleta e Tratamento de Dados Fundamentalistas
"""

import time

import pandas as pd
import yfinance as yf


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

DEFAULT_PERIOD = "1y"

MAX_RETRIES = 3

RETRY_DELAY = 2


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

def normalize_market_asset(asset):
    """
    Normaliza o ativo para consulta no Yahoo Finance.

    Exemplos:

        PETR4
        -> PETR4.SA

        PETR4.SA
        -> PETR4.SA

        AAPL
        -> AAPL
    """

    if asset is None:
        return ""

    asset = (
        str(asset)
        .strip()
        .upper()
        .replace(" ", "")
    )

    if not asset:
        return ""

    # ------------------------------------------------------
    # Tickers brasileiros mais comuns
    # ------------------------------------------------------

    if (
        asset.isalnum()
        and asset[-1:].isdigit()
        and not asset.endswith(".SA")
    ):

        return f"{asset}.SA"

    return asset


# ==========================================================
# VALIDAÇÃO DO DATAFRAME
# ==========================================================

def validate_market_history(data):
    """
    Valida o histórico retornado pelo Yahoo Finance.
    """

    if data is None:
        return False

    if not isinstance(
        data,
        pd.DataFrame,
    ):
        return False

    if data.empty:
        return False

    return True


# ==========================================================
# NORMALIZAÇÃO DAS COLUNAS
# ==========================================================

def normalize_history_columns(data):
    """
    Normaliza as colunas do histórico.

    Trata DataFrames com MultiIndex e garante
    compatibilidade com os demais módulos.
    """

    if not validate_market_history(
        data
    ):
        return None

    history = data.copy()

    # ------------------------------------------------------
    # MULTIINDEX
    # ------------------------------------------------------

    if isinstance(
        history.columns,
        pd.MultiIndex,
    ):

        try:

            history.columns = [
                str(column[0])
                for column in history.columns
            ]

        except Exception:

            return None

    # ------------------------------------------------------
    # LIMPEZA DOS NOMES
    # ------------------------------------------------------

    history.columns = [
        str(column).strip()
        for column in history.columns
    ]

    return history


# ==========================================================
# BUSCA DO HISTÓRICO
# ==========================================================

def fetch_price_history(
    ticker_symbol,
    period=DEFAULT_PERIOD,
):
    """
    Busca o histórico de preços.

    Possui tentativas automáticas para reduzir
    falhas temporárias e erros de rate limit.
    """

    if not ticker_symbol:
        return None

    ticker = yf.Ticker(
        ticker_symbol
    )

    last_error = None

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            data = ticker.history(
                period=period,
                auto_adjust=False,
            )

            if validate_market_history(
                data
            ):

                return data

        except Exception as error:

            last_error = error

        if attempt < (
            MAX_RETRIES - 1
        ):

            time.sleep(
                RETRY_DELAY
                * (
                    attempt + 1
                )
            )

    return None


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float.
    """

    try:

        if value is None:
            return default

        if isinstance(
            value,
            bool,
        ):
            return default

        value = float(
            value
        )

        if pd.isna(
            value
        ):

            return default

        return value

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# EXTRAÇÃO SEGURA DE FUNDAMENTOS
# ==========================================================

def get_info_value(
    info,
    key,
    default=None,
):
    """
    Obtém um valor do dicionário de informações
    fundamentalistas.
    """

    if not isinstance(
        info,
        dict,
    ):
        return default

    value = info.get(
        key,
        default,
    )

    if pd.isna(
        value
    ) if value is not None else False:

        return default

    return value


# ==========================================================
# MARKET CAP
# ==========================================================

def get_market_cap(
    info,
):
    """
    Retorna o valor de mercado da empresa.
    """

    return safe_float(
        get_info_value(
            info,
            "marketCap",
        )
    )


# ==========================================================
# P/L
# ==========================================================

def get_pe_ratio(
    info,
):
    """
    Retorna o indicador Preço/Lucro.

    Prioridade:
        1. trailingPE
        2. forwardPE
    """

    value = safe_float(
        get_info_value(
            info,
            "trailingPE",
        )
    )

    if value is not None:
        return value

    return safe_float(
        get_info_value(
            info,
            "forwardPE",
        )
    )


# ==========================================================
# P/VP
# ==========================================================

def get_price_to_book(
    info,
):
    """
    Retorna o indicador Preço/Valor Patrimonial.
    """

    return safe_float(
        get_info_value(
            info,
            "priceToBook",
        )
    )


# ==========================================================
# DIVIDEND YIELD
# ==========================================================

def get_dividend_yield(
    info,
):
    """
    Retorna o Dividend Yield.

    O Yahoo Finance normalmente retorna o valor
    em formato decimal.

    Exemplo:
        0.08 = 8%
    """

    return safe_float(
        get_info_value(
            info,
            "dividendYield",
        )
    )


# ==========================================================
# ROE
# ==========================================================

def get_roe(
    info,
):
    """
    Retorna o Return on Equity.

    Exemplo:
        0.15 = 15%
    """

    return safe_float(
        get_info_value(
            info,
            "returnOnEquity",
        )
    )


# ==========================================================
# MARGEM DE LUCRO
# ==========================================================

def get_profit_margin(
    info,
):
    """
    Retorna a margem líquida.
    """

    return safe_float(
        get_info_value(
            info,
            "profitMargins",
        )
    )


# ==========================================================
# ENDIVIDAMENTO
# ==========================================================

def get_debt_to_equity(
    info,
):
    """
    Retorna a relação Dívida/Patrimônio.

    Dependendo da fonte, o Yahoo Finance pode
    retornar o indicador em percentual.

    Exemplo:
        85 = 85%
    """

    return safe_float(
        get_info_value(
            info,
            "debtToEquity",
        )
    )


# ==========================================================
# RECEITA
# ==========================================================

def get_total_revenue(
    info,
):
    """
    Retorna a receita total da empresa.
    """

    return safe_float(
        get_info_value(
            info,
            "totalRevenue",
        )
    )


# ==========================================================
# LUCRO
# ==========================================================

def get_net_income(
    info,
):
    """
    Retorna o lucro líquido.

    Caso o campo não esteja disponível,
    retorna None.
    """

    return safe_float(
        get_info_value(
            info,
            "netIncomeToCommon",
        )
    )


# ==========================================================
# NOME DA EMPRESA
# ==========================================================

def get_company_name(
    info,
    fallback="",
):
    """
    Retorna o nome da empresa.
    """

    if not isinstance(
        info,
        dict,
    ):
        return fallback

    for key in [
        "longName",
        "shortName",
    ]:

        value = info.get(
            key
        )

        if value:

            return str(
                value
            )

    return fallback


# ==========================================================
# SETOR
# ==========================================================

def get_sector(
    info,
):
    """
    Retorna o setor da empresa.
    """

    value = get_info_value(
        info,
        "sector",
    )

    if value is None:
        return None

    return str(
        value
    )


# ==========================================================
# INDÚSTRIA
# ==========================================================

def get_industry(
    info,
):
    """
    Retorna a indústria da empresa.
    """

    value = get_info_value(
        info,
        "industry",
    )

    if value is None:
        return None

    return str(
        value
    )


# ==========================================================
# COLETA DOS FUNDAMENTOS
# ==========================================================

def fetch_fundamentals(
    ticker_symbol,
):
    """
    Coleta os dados fundamentalistas do ativo.

    Retorna um dicionário padronizado mesmo
    quando alguns dados não estão disponíveis.
    """

    fundamentals = {

        "company_name": None,

        "sector": None,

        "industry": None,

        "market_cap": None,

        "pe_ratio": None,

        "price_to_book": None,

        "dividend_yield": None,

        "roe": None,

        "profit_margin": None,

        "debt_to_equity": None,

        "total_revenue": None,

        "net_income": None,
    }

    if not ticker_symbol:
        return fundamentals

    try:

        ticker = yf.Ticker(
            ticker_symbol
        )

        info = ticker.info

        if not isinstance(
            info,
            dict,
        ):
            return fundamentals

        fundamentals = {

            "company_name":
                get_company_name(
                    info,
                    fallback=ticker_symbol,
                ),

            "sector":
                get_sector(
                    info,
                ),

            "industry":
                get_industry(
                    info,
                ),

            "market_cap":
                get_market_cap(
                    info,
                ),

            "pe_ratio":
                get_pe_ratio(
                    info,
                ),

            "price_to_book":
                get_price_to_book(
                    info,
                ),

            "dividend_yield":
                get_dividend_yield(
                    info,
                ),

            "roe":
                get_roe(
                    info,
                ),

            "profit_margin":
                get_profit_margin(
                    info,
                ),

            "debt_to_equity":
                get_debt_to_equity(
                    info,
                ),

            "total_revenue":
                get_total_revenue(
                    info,
                ),

            "net_income":
                get_net_income(
                    info,
                ),
        }

    except Exception:

        pass

    return fundamentals


# ==========================================================
# FUNÇÃO PRINCIPAL DE MERCADO
# ==========================================================

def get_market_data(
    asset,
    period=DEFAULT_PERIOD,
):
    """
    Busca todos os dados necessários para
    a análise do ativo.

    Retorna:

        {
            "asset": ...,
            "ticker": ...,
            "period": ...,
            "history": ...,
            "fundamentals": {...}
        }
    """

    normalized_asset = (
        str(asset)
        .strip()
        .upper()
        if asset is not None
        else ""
    )

    if not normalized_asset:

        return None

    ticker_symbol = normalize_market_asset(
        normalized_asset
    )

    if not ticker_symbol:

        return None

    # ------------------------------------------------------
    # HISTÓRICO
    # ------------------------------------------------------

    history = fetch_price_history(
        ticker_symbol,
        period,
    )

    if not validate_market_history(
        history
    ):

        return None

    history = normalize_history_columns(
        history
    )

    if history is None:

        return None

    # ------------------------------------------------------
    # FUNDAMENTOS
    # ------------------------------------------------------

    fundamentals = fetch_fundamentals(
        ticker_symbol
    )

    # ------------------------------------------------------
    # RETORNO
    # ------------------------------------------------------

    return {

        "asset":
            normalized_asset,

        "ticker":
            ticker_symbol,

        "period":
            period,

        "history":
            history,

        "fundamentals":
            fundamentals,
    }


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    market_data,
):
    """
    Prepara os dados de mercado para uso
    pelos módulos de indicadores e análise.

    Mantém:
        - asset
        - ticker
        - period
        - history
        - price
        - fundamentals
    """

    if not isinstance(
        market_data,
        dict,
    ):
        return None

    history = market_data.get(
        "history"
    )

    if not validate_market_history(
        history
    ):
        return None

    history = normalize_history_columns(
        history
    )

    if history is None:
        return None

    if "Close" not in history.columns:
        return None

    try:

        close = pd.to_numeric(
            history["Close"],
            errors="coerce",
        ).dropna()

    except Exception:

        return None

    if close.empty:
        return None

    price = safe_float(
        close.iloc[-1]
    )

    if price is None:
        return None

    fundamentals = market_data.get(
        "fundamentals",
        {},
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    return {

        "asset":
            market_data.get(
                "asset"
            ),

        "ticker":
            market_data.get(
                "ticker"
            ),

        "period":
            market_data.get(
                "period"
            ),

        "history":
            history,

        "price":
            price,

        "fundamentals":
            fundamentals,
    }


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def get_current_price(
    market_data,
):
    """
    Retorna o último preço disponível.

    Primeiro tenta utilizar o preço já preparado.
    Caso necessário, utiliza o histórico.
    """

    if not isinstance(
        market_data,
        dict,
    ):
        return None

    # ------------------------------------------------------
    # PREÇO DIRETO
    # ------------------------------------------------------

    price = safe_float(
        market_data.get(
            "price"
        )
    )

    if price is not None:

        return price

    # ------------------------------------------------------
    # HISTÓRICO
    # ------------------------------------------------------

    history = market_data.get(
        "history"
    )

    if not validate_market_history(
        history
    ):
        return None

    if "Close" not in history.columns:
        return None

    try:

        close = pd.to_numeric(
            history["Close"],
            errors="coerce",
        ).dropna()

        if close.empty:
            return None

        return safe_float(
            close.iloc[-1]
        )

    except Exception:

        return None


# ==========================================================
# FUNDAMENTOS PREPARADOS
# ==========================================================

def get_fundamentals(
    market_data,
):
    """
    Retorna os dados fundamentalistas
    de forma segura.
    """

    if not isinstance(
        market_data,
        dict,
    ):
        return {}

    fundamentals = market_data.get(
        "fundamentals",
        {},
    )

    if not isinstance(
        fundamentals,
        dict,
    ):
        return {}

    return fundamentals
