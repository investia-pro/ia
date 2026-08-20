"""
InvestIA PRO
Motor de Score Técnico e Fundamentalista

Versão: v0.7
Fase: 3.0.2 - Score Fundamentalista
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(score):
    """
    Mantém o Score entre 0 e 100.
    """

    try:
        score = float(score)

    except (
        TypeError,
        ValueError,
    ):
        score = 0

    return max(
        0,
        min(
            100,
            int(round(score)),
        ),
    )


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.
    """

    try:

        if value is None:
            return default

        if isinstance(
            value,
            bool,
        ):
            return default

        value = float(value)

        return value

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# CONTRIBUIÇÃO DOS INDICADORES TÉCNICOS
# ==========================================================

def get_score_breakdown(data):
    """
    Calcula a contribuição individual
    dos indicadores técnicos.

    Score base:
        50 pontos

    MA21:
        +10 / -10

    MA200:
        +20 / -20

    RSI:
        +10 / -10 / 0
    """

    if data is None:

        raise ValueError(
            "Dados não fornecidos para o "
            "detalhamento do Score."
        )

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    missing = [
        field
        for field in required
        if field not in data
        or data[field] is None
    ]

    if missing:

        raise ValueError(
            "Dados ausentes para o Score: "
            + ", ".join(missing)
        )

    price = safe_float(
        data["price"]
    )

    ma21 = safe_float(
        data["ma21"]
    )

    ma200 = safe_float(
        data["ma200"]
    )

    rsi = safe_float(
        data["rsi"]
    )

    if None in [
        price,
        ma21,
        ma200,
        rsi,
    ]:

        raise ValueError(
            "Os dados técnicos possuem "
            "valores inválidos."
        )

    # ======================================================
    # BASE
    # ======================================================

    base = 50

    # ======================================================
    # MA21
    # ======================================================

    if price > ma21:

        ma21_points = 10
        ma21_signal = "Positivo"
        ma21_reason = (
            "Preço acima da MA21."
        )

    elif price < ma21:

        ma21_points = -10
        ma21_signal = "Negativo"
        ma21_reason = (
            "Preço abaixo da MA21."
        )

    else:

        ma21_points = 0
        ma21_signal = "Neutro"
        ma21_reason = (
            "Preço alinhado à MA21."
        )

    # ======================================================
    # MA200
    # ======================================================

    if price > ma200:

        ma200_points = 20
        ma200_signal = "Positivo"
        ma200_reason = (
            "Preço acima da MA200."
        )

    elif price < ma200:

        ma200_points = -20
        ma200_signal = "Negativo"
        ma200_reason = (
            "Preço abaixo da MA200."
        )

    else:

        ma200_points = 0
        ma200_signal = "Neutro"
        ma200_reason = (
            "Preço alinhado à MA200."
        )

    # ======================================================
    # RSI
    # ======================================================

    if rsi <= RSI_OVERSOLD:

        rsi_points = 10
        rsi_signal = "Positivo"
        rsi_reason = (
            "RSI em região de sobrevenda."
        )

    elif rsi >= RSI_OVERBOUGHT:

        rsi_points = -10
        rsi_signal = "Negativo"
        rsi_reason = (
            "RSI em região de sobrecompra."
        )

    else:

        rsi_points = 0
        rsi_signal = "Neutro"
        rsi_reason = (
            "RSI em região neutra."
        )

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    raw_score = (
        base
        + ma21_points
        + ma200_points
        + rsi_points
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    final_score = clamp_score(
        raw_score
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "base": base,

        "ma21": {
            "points": ma21_points,
            "signal": ma21_signal,
            "reason": ma21_reason,
        },

        "ma200": {
            "points": ma200_points,
            "signal": ma200_signal,
            "reason": ma200_reason,
        },

        "rsi": {
            "points": rsi_points,
            "signal": rsi_signal,
            "reason": rsi_reason,
        },

        "raw_score": raw_score,

        "score": final_score,
    }


# ==========================================================
# SCORE TÉCNICO PRINCIPAL
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula o Score Técnico InvestIA
    de 0 a 100.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown["score"]


# ==========================================================
# CLASSIFICAÇÃO DO SCORE
# ==========================================================

def classify_score(score):
    """
    Classifica um Score entre 0 e 100.
    """

    score = clamp_score(
        score
    )

    if score >= 80:
        return "FORTE"

    if score >= 65:
        return "BOM"

    if score >= 50:
        return "NEUTRO"

    if score >= 35:
        return "FRACO"

    return "MUITO FRACO"


# ==========================================================
# SINAL DO SCORE
# ==========================================================

def classify_signal(score):
    """
    Define o sinal com base no Score.
    """

    score = clamp_score(
        score
    )

    if score >= BUY_SCORE:
        return "POSITIVO"

    if score <= SELL_SCORE:
        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# SCORE TÉCNICO COMPLETO
# ==========================================================

def calculate_score_details(data):
    """
    Retorna o Score Técnico completo.
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown["score"]

    return {

        "score": score,

        "classification":
            classify_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),

        "breakdown":
            breakdown,
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - VALUATION
# ==========================================================

def score_pe_ratio(pe_ratio):
    """
    Avalia o indicador P/L.

    Critério geral:

    P/L <= 0:
        0 pontos
        Empresa sem lucro ou indicador inválido.

    P/L <= 5:
        +10

    P/L <= 10:
        +7

    P/L <= 15:
        +4

    P/L <= 25:
        0

    P/L <= 40:
        -5

    P/L > 40:
        -10
    """

    pe_ratio = safe_float(
        pe_ratio
    )

    if pe_ratio is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": "P/L não disponível.",
        }

    if pe_ratio <= 0:

        return {
            "points": 0,
            "signal": "Atenção",
            "reason": (
                "P/L não positivo, podendo indicar "
                "ausência de lucro ou resultado "
                "não recorrente."
            ),
        }

    if pe_ratio <= 5:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "P/L baixo em relação ao lucro atual."
            ),
        }

    if pe_ratio <= 10:

        return {
            "points": 7,
            "signal": "Positivo",
            "reason": (
                "P/L considerado atrativo."
            ),
        }

    if pe_ratio <= 15:

        return {
            "points": 4,
            "signal": "Moderadamente Positivo",
            "reason": (
                "P/L em faixa moderada."
            ),
        }

    if pe_ratio <= 25:

        return {
            "points": 0,
            "signal": "Neutro",
            "reason": (
                "P/L em faixa intermediária."
            ),
        }

    if pe_ratio <= 40:

        return {
            "points": -5,
            "signal": "Negativo",
            "reason": (
                "P/L elevado, indicando valuation "
                "mais exigente."
            ),
        }

    return {
        "points": -10,
        "signal": "Muito Negativo",
        "reason": (
            "P/L muito elevado em relação ao lucro."
        ),
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - P/VP
# ==========================================================

def score_price_to_book(price_to_book):
    """
    Avalia o indicador P/VP.
    """

    price_to_book = safe_float(
        price_to_book
    )

    if price_to_book is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": "P/VP não disponível.",
        }

    if price_to_book <= 0:

        return {
            "points": 0,
            "signal": "Atenção",
            "reason": (
                "P/VP não positivo ou patrimônio "
                "não comparável."
            ),
        }

    if price_to_book <= 1:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "Ativo negociado próximo ou abaixo "
                "do valor patrimonial."
            ),
        }

    if price_to_book <= 2:

        return {
            "points": 6,
            "signal": "Positivo",
            "reason": (
                "P/VP em faixa moderada."
            ),
        }

    if price_to_book <= 4:

        return {
            "points": 0,
            "signal": "Neutro",
            "reason": (
                "P/VP em faixa intermediária."
            ),
        }

    if price_to_book <= 8:

        return {
            "points": -5,
            "signal": "Negativo",
            "reason": (
                "Ativo negociado com prêmio "
                "patrimonial elevado."
            ),
        }

    return {
        "points": -10,
        "signal": "Muito Negativo",
        "reason": (
            "P/VP muito elevado."
        ),
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - DIVIDEND YIELD
# ==========================================================

def score_dividend_yield(dividend_yield):
    """
    Avalia o Dividend Yield.

    Aceita valores em formato decimal.

    Exemplos:

        0.05 = 5%
        0.10 = 10%
    """

    dividend_yield = safe_float(
        dividend_yield
    )

    if dividend_yield is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": "Dividend Yield não disponível.",
        }

    if dividend_yield < 0:

        return {
            "points": 0,
            "signal": "Inválido",
            "reason": (
                "Dividend Yield inválido."
            ),
        }

    if dividend_yield >= 0.10:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "Dividend Yield elevado."
            ),
        }

    if dividend_yield >= 0.06:

        return {
            "points": 7,
            "signal": "Positivo",
            "reason": (
                "Boa geração de dividendos."
            ),
        }

    if dividend_yield >= 0.03:

        return {
            "points": 4,
            "signal": "Moderadamente Positivo",
            "reason": (
                "Dividend Yield moderado."
            ),
        }

    if dividend_yield > 0:

        return {
            "points": 1,
            "signal": "Levemente Positivo",
            "reason": (
                "Empresa distribui dividendos, "
                "porém em percentual reduzido."
            ),
        }

    return {
        "points": 0,
        "signal": "Neutro",
        "reason": (
            "Não há Dividend Yield disponível."
        ),
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - ROE
# ==========================================================

def score_roe(roe):
    """
    Avalia o Return on Equity.

    Aceita valores em formato decimal.

        0.15 = 15%
    """

    roe = safe_float(
        roe
    )

    if roe is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": "ROE não disponível.",
        }

    if roe < 0:

        return {
            "points": -10,
            "signal": "Muito Negativo",
            "reason": (
                "ROE negativo, indicando retorno "
                "negativo sobre o patrimônio."
            ),
        }

    if roe >= 0.25:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "ROE elevado."
            ),
        }

    if roe >= 0.15:

        return {
            "points": 7,
            "signal": "Positivo",
            "reason": (
                "Boa rentabilidade sobre o patrimônio."
            ),
        }

    if roe >= 0.08:

        return {
            "points": 3,
            "signal": "Moderadamente Positivo",
            "reason": (
                "Rentabilidade moderada."
            ),
        }

    if roe >= 0:

        return {
            "points": 0,
            "signal": "Neutro",
            "reason": (
                "Rentabilidade baixa ou limitada."
            ),
        }

    return {
        "points": 0,
        "signal": "Neutro",
        "reason": "ROE sem classificação.",
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - MARGEM DE LUCRO
# ==========================================================

def score_profit_margin(profit_margin):
    """
    Avalia a margem líquida.

    Aceita valores em formato decimal.

        0.10 = 10%
    """

    profit_margin = safe_float(
        profit_margin
    )

    if profit_margin is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": (
                "Margem de lucro não disponível."
            ),
        }

    if profit_margin < 0:

        return {
            "points": -10,
            "signal": "Muito Negativo",
            "reason": (
                "Margem líquida negativa."
            ),
        }

    if profit_margin >= 0.20:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "Margem líquida elevada."
            ),
        }

    if profit_margin >= 0.10:

        return {
            "points": 7,
            "signal": "Positivo",
            "reason": (
                "Boa margem líquida."
            ),
        }

    if profit_margin >= 0.05:

        return {
            "points": 3,
            "signal": "Moderadamente Positivo",
            "reason": (
                "Margem líquida moderada."
            ),
        }

    return {
        "points": 0,
        "signal": "Neutro",
        "reason": (
            "Margem líquida reduzida."
        ),
    }


# ==========================================================
# PONTUAÇÃO FUNDAMENTALISTA - ENDIVIDAMENTO
# ==========================================================

def score_debt_to_equity(debt_to_equity):
    """
    Avalia Dívida/Patrimônio.

    O Yahoo Finance pode retornar:

        50 = 50%
        100 = 100%
    """

    debt_to_equity = safe_float(
        debt_to_equity
    )

    if debt_to_equity is None:

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason": (
                "Indicador de endividamento "
                "não disponível."
            ),
        }

    if debt_to_equity < 0:

        return {
            "points": 0,
            "signal": "Atenção",
            "reason": (
                "Dívida/Patrimônio não comparável."
            ),
        }

    if debt_to_equity <= 30:

        return {
            "points": 10,
            "signal": "Muito Positivo",
            "reason": (
                "Baixo nível de endividamento."
            ),
        }

    if debt_to_equity <= 80:

        return {
            "points": 7,
            "signal": "Positivo",
            "reason": (
                "Endividamento controlado."
            ),
        }

    if debt_to_equity <= 150:

        return {
            "points": 3,
            "signal": "Moderadamente Positivo",
            "reason": (
                "Endividamento moderado."
            ),
        }

    if debt_to_equity <= 250:

        return {
            "points": -5,
            "signal": "Negativo",
            "reason": (
                "Endividamento elevado."
            ),
        }

    return {
        "points": -10,
        "signal": "Muito Negativo",
        "reason": (
            "Endividamento muito elevado."
        ),
    }


# ==========================================================
# BREAKDOWN FUNDAMENTALISTA
# ==========================================================

def get_fundamental_score_breakdown(
    fundamentals,
):
    """
    Calcula o detalhamento do Score Fundamentalista.

    Estrutura avaliada:

        Valuation:
            - P/L
            - P/VP

        Dividendos:
            - Dividend Yield

        Rentabilidade:
            - ROE
            - Margem de Lucro

        Endividamento:
            - Dívida/Patrimônio

    O cálculo bruto possui base de 50 pontos.
    Cada componente adiciona ou reduz pontos.

    O resultado final é limitado entre 0 e 100.
    """

    if fundamentals is None:

        fundamentals = {}

    if not isinstance(
        fundamentals,
        dict,
    ):

        raise ValueError(
            "Os fundamentos devem ser "
            "fornecidos em formato de dicionário."
        )

    # ======================================================
    # BASE
    # ======================================================

    base = 50

    # ======================================================
    # EXTRAÇÃO DOS FUNDAMENTOS
    # ======================================================

    pe_ratio = fundamentals.get(
        "pe_ratio"
    )

    price_to_book = fundamentals.get(
        "price_to_book"
    )

    dividend_yield = fundamentals.get(
        "dividend_yield"
    )

    roe = fundamentals.get(
        "roe"
    )

    profit_margin = fundamentals.get(
        "profit_margin"
    )

    debt_to_equity = fundamentals.get(
        "debt_to_equity"
    )

    # ======================================================
    # VALUATION
    # ======================================================

    pe_data = score_pe_ratio(
        pe_ratio
    )

    pb_data = score_price_to_book(
        price_to_book
    )

    # ======================================================
    # DIVIDENDOS
    # ======================================================

    dividend_data = score_dividend_yield(
        dividend_yield
    )

    # ======================================================
    # RENTABILIDADE
    # ======================================================

    roe_data = score_roe(
        roe
    )

    margin_data = score_profit_margin(
        profit_margin
    )

    # ======================================================
    # ENDIVIDAMENTO
    # ======================================================

    debt_data = score_debt_to_equity(
        debt_to_equity
    )

    # ======================================================
    # PONTOS FUNDAMENTALISTAS
    # ======================================================

    fundamental_points = (

        pe_data["points"]

        + pb_data["points"]

        + dividend_data["points"]

        + roe_data["points"]

        + margin_data["points"]

        + debt_data["points"]
    )

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    raw_score = (
        base
        + fundamental_points
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    final_score = clamp_score(
        raw_score
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "base": base,

        "pe_ratio": pe_data,

        "price_to_book": pb_data,

        "dividend_yield": dividend_data,

        "roe": roe_data,

        "profit_margin": margin_data,

        "debt_to_equity": debt_data,

        "fundamental_points":
            fundamental_points,

        "raw_score":
            raw_score,

        "score":
            final_score,
    }


# ==========================================================
# SCORE FUNDAMENTALISTA PRINCIPAL
# ==========================================================

def calculate_fundamental_score(
    fundamentals,
):
    """
    Calcula o Score Fundamentalista
    do InvestIA.

    Retorna apenas o Score de 0 a 100.
    """

    breakdown = get_fundamental_score_breakdown(
        fundamentals
    )

    return breakdown["score"]


# ==========================================================
# DETALHES FUNDAMENTALISTAS
# ==========================================================

def calculate_fundamental_score_details(
    fundamentals,
):
    """
    Retorna o Score Fundamentalista completo.

    Inclui:

        - Score
        - Classificação
        - Sinal
        - Breakdown
    """

    breakdown = get_fundamental_score_breakdown(
        fundamentals
    )

    score = breakdown["score"]

    return {

        "score":
            score,

        "classification":
            classify_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),

        "breakdown":
            breakdown,
    }
