"""
InvestIA PRO
Módulo de Mercado e Dados Fundamentalistas

Versão: v0.7
Fase: 3.0.6 - Análise Fundamentalista Real

Responsabilidades:
- Buscar dados históricos de mercado
- Normalizar o ticker do ativo
- Preparar o histórico de preços
- Obter o preço atual
- Buscar informações da empresa
- Buscar indicadores fundamentalistas
- Normalizar valores ausentes
- Fornecer uma estrutura estável para o restante da aplicação
"""

import time

import pandas as pd
import yfinance as yf


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

DEFAULT_PERIOD = "1y"

VALID_PERIODS = [
    "6mo",
    "1y",
    "2y",
    "5y",
]

BR_TICKER_SUFFIX = ".SA"


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.

    Retorna default quando o valor:
    - é None
    - não pode ser convertido
    - é NaN
    - é infinito
    """

    if value is None:
        return default

    try:

        value = float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default

    if pd.isna(value):
        return default

    if value == float("inf"):
        return default

    if value == float("-inf"):
        return default

    return value


def safe_text(
    value,
    default=None,
):
    """
    Converte valores para texto com segurança.
    """

    if value is None:
        return default

    try:

        value = str(value).strip()

    except Exception:

        return default

    if not value:
        return default

    if value.lower() == "nan":
        return default

    return value


def get_dict_value(
    data,
    *keys,
    default=None,
):
    """
    Procura um valor em um dicionário
    utilizando múltiplas chaves possíveis.
    """

    if not isinstance(
        data,
        dict,
    ):
        return default

    for key in keys:

        if key in data:

            value = data.get(
                key
            )

            if value is not None:

                return value

    return default


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

def normalize_asset(
    asset,
):
    """
    Normaliza o ticker informado pelo usuário.

    Exemplos:

    PETR4   -> PETR4.SA
    VALE3   -> VALE3.SA
    ITUB4   -> ITUB4.SA

    Também mantém compatibilidade com:
    - PETR4.SA
    - AAPL
    - MSFT
    - ETFs internacionais
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
    # ATIVOS JÁ NORMALIZADOS
    # ------------------------------------------------------

    if "." in asset:

        return asset

    # ------------------------------------------------------
    # AÇÕES BRASILEIRAS
    # ------------------------------------------------------
    # Regra básica:
    # códigos com 4 letras + número são tratados
    # como ativos negociados na B3.
    #
    # Exemplos:
    # PETR4
    # VALE3
    # ITUB4
    # BBAS3
    # WEGE3
    # BBDC4
    # ABEV3
    # PETR3
    # SANB11
    # XPML11
    # HGLG11

    if len(asset) >= 5:

        letters = "".join(
            char
            for char in asset
            if char.isalpha()
        )

        numbers = "".join(
            char
            for char in asset
            if char.isdigit()
        )

        if letters and numbers:

            return (
                asset
                + BR_TICKER_SUFFIX
            )

    return asset


# ==========================================================
# VALIDAÇÃO DO PERÍODO
# ==========================================================

def normalize_period(
    period,
):
    """
    Normaliza o período informado.
    """

    if period in VALID_PERIODS:

        return period

    return DEFAULT_PERIOD


# ==========================================================
# OBTENÇÃO DO TICKER
# ==========================================================

def create_ticker(
    asset,
):
    """
    Cria o objeto yfinance.Ticker.
    """

    ticker_symbol = normalize_asset(
        asset
    )

    if not ticker_symbol:

        raise ValueError(
            "Código do ativo não informado."
        )

    return yf.Ticker(
        ticker_symbol
    )


# ==========================================================
# BUSCA DO HISTÓRICO
# ==========================================================

def fetch_history(
    ticker,
    period,
    retries=3,
    retry_delay=2,
):
    """
    Busca o histórico de preços.

    Implementa tentativas adicionais para
    reduzir falhas temporárias ou rate limits.
    """

    last_error = None

    for attempt in range(
        retries
    ):

        try:

            history = ticker.history(
                period=period,
                auto_adjust=False,
                actions=False,
            )

            if isinstance(
                history,
                pd.DataFrame,
            ):

                if not history.empty:

                    return history

        except Exception as error:

            last_error = error

        if attempt < retries - 1:

            time.sleep(
                retry_delay
            )

    if last_error is not None:

        raise last_error

    return pd.DataFrame()


# ==========================================================
# BUSCA DOS DADOS DO MERCADO
# ==========================================================

def get_market_data(
    asset,
    period=DEFAULT_PERIOD,
):
    """
    Busca os dados principais do ativo.

    Retorna uma estrutura com:
    - asset
    - ticker
    - period
    - history
    - info
    - fast_info
    - fundamentals
    """

    asset = (
        str(asset)
        .strip()
        .upper()
    )

    if not asset:

        raise ValueError(
            "Informe um código de ativo."
        )

    period = normalize_period(
        period
    )

    ticker_symbol = normalize_asset(
        asset
    )

    ticker = create_ticker(
        asset
    )

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = fetch_history(
        ticker,
        period,
    )

    if history is None:

        history = pd.DataFrame()

    # ======================================================
    # INFO
    # ======================================================
    # A propriedade info pode falhar ou sofrer
    # limitação temporária no Yahoo Finance.
    # Por isso, falhas aqui não impedem o retorno
    # do histórico de preços.

    info = {}

    try:

        ticker_info = ticker.info

        if isinstance(
            ticker_info,
            dict,
        ):

            info = ticker_info

    except Exception:

        info = {}

    # ======================================================
    # FAST INFO
    # ======================================================

    fast_info = {}

    try:

        ticker_fast_info = ticker.fast_info

        if ticker_fast_info is not None:

            try:

                fast_info = dict(
                    ticker_fast_info
                )

            except Exception:

                fast_info = {}

    except Exception:

        fast_info = {}

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamentals = extract_fundamentals(
        info
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "asset": asset,

        "ticker": ticker_symbol,

        "period": period,

        "history": history,

        "info": info,

        "fast_info": fast_info,

        "fundamentals": fundamentals,
    }


# ==========================================================
# EXTRAÇÃO DOS FUNDAMENTOS
# ==========================================================

def extract_fundamentals(
    info,
):
    """
    Extrai e padroniza os indicadores
    fundamentalistas disponíveis no Yahoo Finance.

    Os valores retornados são mantidos em formato
    numérico bruto.

    Exemplos:
    - ROE: 0.18 = 18%
    - Dividend Yield: 0.08 = 8%
    - Margem: 0.12 = 12%
    """

    if not isinstance(
        info,
        dict,
    ):

        info = {}

    # ======================================================
    # IDENTIFICAÇÃO DA EMPRESA
    # ======================================================

    company_name = safe_text(
        get_dict_value(
            info,
            "longName",
            "shortName",
        )
    )

    sector = safe_text(
        get_dict_value(
            info,
            "sector",
        )
    )

    industry = safe_text(
        get_dict_value(
            info,
            "industry",
        )
    )

    country = safe_text(
        get_dict_value(
            info,
            "country",
        )
    )

    # ======================================================
    # VALUATION
    # ======================================================

    price_to_earnings = safe_float(
        get_dict_value(
            info,
            "trailingPE",
            "forwardPE",
        )
    )

    price_to_book = safe_float(
        get_dict_value(
            info,
            "priceToBook",
        )
    )

    enterprise_to_revenue = safe_float(
        get_dict_value(
            info,
            "enterpriseToRevenue",
        )
    )

    enterprise_to_ebitda = safe_float(
        get_dict_value(
            info,
            "enterpriseToEbitda",
        )
    )

    # ======================================================
    # RENTABILIDADE
    # ======================================================

    return_on_equity = safe_float(
        get_dict_value(
            info,
            "returnOnEquity",
        )
    )

    return_on_assets = safe_float(
        get_dict_value(
            info,
            "returnOnAssets",
        )
    )

    profit_margin = safe_float(
        get_dict_value(
            info,
            "profitMargins",
        )
    )

    operating_margin = safe_float(
        get_dict_value(
            info,
            "operatingMargins",
        )
    )

    gross_margin = safe_float(
        get_dict_value(
            info,
            "grossMargins",
        )
    )

    # ======================================================
    # DIVIDENDOS
    # ======================================================

    dividend_yield = safe_float(
        get_dict_value(
            info,
            "dividendYield",
        )
    )

    trailing_annual_dividend_yield = safe_float(
        get_dict_value(
            info,
            "trailingAnnualDividendYield",
        )
    )

    dividend_rate = safe_float(
        get_dict_value(
            info,
            "dividendRate",
        )
    )

    payout_ratio = safe_float(
        get_dict_value(
            info,
            "payoutRatio",
        )
    )

    # ======================================================
    # CRESCIMENTO
    # ======================================================

    revenue_growth = safe_float(
        get_dict_value(
            info,
            "revenueGrowth",
        )
    )

    earnings_growth = safe_float(
        get_dict_value(
            info,
            "earningsGrowth",
        )
    )

    # ======================================================
    # ENDIVIDAMENTO
    # ======================================================

    debt_to_equity = safe_float(
        get_dict_value(
            info,
            "debtToEquity",
        )
    )

    total_debt = safe_float(
        get_dict_value(
            info,
            "totalDebt",
        )
    )

    total_cash = safe_float(
        get_dict_value(
            info,
            "totalCash",
        )
    )

    # ======================================================
    # BALANÇO
    # ======================================================

    total_revenue = safe_float(
        get_dict_value(
            info,
            "totalRevenue",
        )
    )

    net_income = safe_float(
        get_dict_value(
            info,
            "netIncomeToCommon",
        )
    )

    total_equity = safe_float(
        get_dict_value(
            info,
            "totalStockholderEquity",
            "stockholdersEquity",
        )
    )

    # ======================================================
    # LIQUIDEZ
    # ======================================================

    current_ratio = safe_float(
        get_dict_value(
            info,
            "currentRatio",
        )
    )

    quick_ratio = safe_float(
        get_dict_value(
            info,
            "quickRatio",
        )
    )

    # ======================================================
    # TAMANHO
    # ======================================================

    market_cap = safe_float(
        get_dict_value(
            info,
            "marketCap",
        )
    )

    enterprise_value = safe_float(
        get_dict_value(
            info,
            "enterpriseValue",
        )
    )

    # ======================================================
    # RETORNO
    # ======================================================

    fifty_two_week_change = safe_float(
        get_dict_value(
            info,
            "52WeekChange",
        )
    )

    fifty_two_week_high = safe_float(
        get_dict_value(
            info,
            "fiftyTwoWeekHigh",
        )
    )

    fifty_two_week_low = safe_float(
        get_dict_value(
            info,
            "fiftyTwoWeekLow",
        )
    )

    # ======================================================
    # ESTRUTURA PADRONIZADA
    # ======================================================

    return {

        # --------------------------------------------------
        # IDENTIFICAÇÃO
        # --------------------------------------------------

        "company_name": company_name,

        "sector": sector,

        "industry": industry,

        "country": country,

        # --------------------------------------------------
        # VALUATION
        # --------------------------------------------------

        "price_to_earnings":
            price_to_earnings,

        "price_to_book":
            price_to_book,

        "enterprise_to_revenue":
            enterprise_to_revenue,

        "enterprise_to_ebitda":
            enterprise_to_ebitda,

        # --------------------------------------------------
        # RENTABILIDADE
        # --------------------------------------------------

        "return_on_equity":
            return_on_equity,

        "return_on_assets":
            return_on_assets,

        "profit_margin":
            profit_margin,

        "operating_margin":
            operating_margin,

        "gross_margin":
            gross_margin,

        # --------------------------------------------------
        # DIVIDENDOS
        # --------------------------------------------------

        "dividend_yield":
            dividend_yield,

        "trailing_annual_dividend_yield":
            trailing_annual_dividend_yield,

        "dividend_rate":
            dividend_rate,

        "payout_ratio":
            payout_ratio,

        # --------------------------------------------------
        # CRESCIMENTO
        # --------------------------------------------------

        "revenue_growth":
            revenue_growth,

        "earnings_growth":
            earnings_growth,

        # --------------------------------------------------
        # ENDIVIDAMENTO
        # --------------------------------------------------

        "debt_to_equity":
            debt_to_equity,

        "total_debt":
            total_debt,

        "total_cash":
            total_cash,

        # --------------------------------------------------
        # BALANÇO
        # --------------------------------------------------

        "total_revenue":
            total_revenue,

        "net_income":
            net_income,

        "total_equity":
            total_equity,

        # --------------------------------------------------
        # LIQUIDEZ
        # --------------------------------------------------

        "current_ratio":
            current_ratio,

        "quick_ratio":
            quick_ratio,

        # --------------------------------------------------
        # TAMANHO
        # --------------------------------------------------

        "market_cap":
            market_cap,

        "enterprise_value":
            enterprise_value,

        # --------------------------------------------------
        # MERCADO
        # --------------------------------------------------

        "fifty_two_week_change":
            fifty_two_week_change,

        "fifty_two_week_high":
            fifty_two_week_high,

        "fifty_two_week_low":
            fifty_two_week_low,
    }


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    market_data,
):
    """
    Prepara os dados recebidos do mercado
    para consumo pelos demais módulos.

    Garante:
    - history válido
    - Close numérico
    - índice organizado
    - fundamentals como dicionário
    """

    if not isinstance(
        market_data,
        dict,
    ):

        raise ValueError(
            "Dados de mercado inválidos."
        )

    history = market_data.get(
        "history"
    )

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        raise ValueError(
            "Histórico de preços inválido."
        )

    if history.empty:

        raise ValueError(
            "Histórico de preços vazio."
        )

    history = history.copy()

    # ======================================================
    # NORMALIZAÇÃO DAS COLUNAS
    # ======================================================

    history.columns = [
        str(column).strip()
        for column in history.columns
    ]

    # ======================================================
    # VALIDAÇÃO DO PREÇO DE FECHAMENTO
    # ======================================================

    close_column = None

    for column in [
        "Close",
        "close",
        "Adj Close",
        "adj_close",
    ]:

        if column in history.columns:

            close_column = column
            break

    if close_column is None:

        raise ValueError(
            "Coluna de preço de fechamento não encontrada."
        )

    # ======================================================
    # CRIAÇÃO DA COLUNA PADRONIZADA
    # ======================================================

    history["price"] = pd.to_numeric(
        history[
            close_column
        ],
        errors="coerce",
    )

    history = history.dropna(
        subset=[
            "price"
        ]
    )

    if history.empty:

        raise ValueError(
            "Não existem preços válidos no histórico."
        )

    # ======================================================
    # ORDENAÇÃO
    # ======================================================

    try:

        history = history.sort_index()

    except Exception:

        pass

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamentals = market_data.get(
        "fundamentals",
        {}
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ======================================================
    # RETORNO
    # ======================================================

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

        "info":
            market_data.get(
                "info",
                {}
            ),

        "fast_info":
            market_data.get(
                "fast_info",
                {}
            ),

        "fundamentals":
            fundamentals,
    }


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def get_current_price(
    prepared_data,
):
    """
    Obtém o preço atual do ativo.

    Ordem de prioridade:

    1. fast_info.last_price
    2. fast_info.regular_market_price
    3. info.currentPrice
    4. info.regularMarketPrice
    5. último preço do histórico
    """

    if not isinstance(
        prepared_data,
        dict,
    ):

        return None

    # ======================================================
    # FAST INFO
    # ======================================================

    fast_info = prepared_data.get(
        "fast_info",
        {}
    )

    if isinstance(
        fast_info,
        dict,
    ):

        for key in [

            "last_price",
            "regular_market_price",
            "lastPrice",

        ]:

            value = safe_float(
                fast_info.get(
                    key
                )
            )

            if value is not None:

                return value

    # ======================================================
    # INFO
    # ======================================================

    info = prepared_data.get(
        "info",
        {}
    )

    if isinstance(
        info,
        dict,
    ):

        for key in [

            "currentPrice",
            "regularMarketPrice",
            "previousClose",

        ]:

            value = safe_float(
                info.get(
                    key
                )
            )

            if value is not None:

                return value

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = prepared_data.get(
        "history"
    )

    if isinstance(
        history,
        pd.DataFrame,
    ) and not history.empty:

        for column in [

            "price",
            "Close",
            "close",

        ]:

            if column in history.columns:

                prices = pd.to_numeric(
                    history[
                        column
                    ],
                    errors="coerce",
                ).dropna()

                if not prices.empty:

                    return safe_float(
                        prices.iloc[-1]
                    )

    return None


# ==========================================================
# DADOS FUNDAMENTALISTAS
# ==========================================================

def get_fundamentals(
    prepared_data,
):
    """
    Retorna os dados fundamentalistas
    já preparados.

    Função pública para utilização
    pelos módulos analysis.py e score.py.
    """

    if not isinstance(
        prepared_data,
        dict,
    ):

        return {}

    fundamentals = prepared_data.get(
        "fundamentals",
        {}
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        return {}

    return fundamentals.copy()


# ==========================================================
# RESUMO FUNDAMENTALISTA
# ==========================================================

def get_fundamental_summary(
    fundamentals,
):
    """
    Retorna um resumo compacto dos
    principais indicadores fundamentalistas.

    Utilizado principalmente pela interface.
    """

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    return {

        "company_name":
            fundamentals.get(
                "company_name"
            ),

        "sector":
            fundamentals.get(
                "sector"
            ),

        "industry":
            fundamentals.get(
                "industry"
            ),

        "p_e":
            fundamentals.get(
                "price_to_earnings"
            ),

        "p_b":
            fundamentals.get(
                "price_to_book"
            ),

        "roe":
            fundamentals.get(
                "return_on_equity"
            ),

        "dividend_yield":
            fundamentals.get(
                "dividend_yield"
            ),

        "profit_margin":
            fundamentals.get(
                "profit_margin"
            ),

        "revenue_growth":
            fundamentals.get(
                "revenue_growth"
            ),

        "debt_to_equity":
            fundamentals.get(
                "debt_to_equity"
            ),
    }
