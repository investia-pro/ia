"""
InvestIA PRO
Motor de Scores

Versão: v0.7
Fase: 3.0.6 - Score Fundamentalista Real

Responsabilidades:
- Calcular Score Técnico
- Explicar o Score Técnico
- Calcular Score Fundamentalista
- Explicar o Score Fundamentalista
- Integrar os Scores
- Classificar os resultados
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# CONFIGURAÇÕES DO SCORE FUNDAMENTALISTA
# ==========================================================

FUNDAMENTAL_SCORE_BASE = 50

# Pesos máximos positivos e negativos por indicador.
# O score parte de 50 e pode variar entre 0 e 100.

FUNDAMENTAL_WEIGHTS = {

    "price_to_earnings": 10,

    "price_to_book": 10,

    "return_on_equity": 15,

    "dividend_yield": 10,

    "profit_margin": 10,

    "revenue_growth": 10,

    "debt_to_equity": 15,
}


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def clamp_score(score):
    """
    Mantém qualquer Score entre 0 e 100.
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


def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.
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

    # NaN
    if value != value:

        return default

    # Infinity
    if value == float("inf"):

        return default

    if value == float("-inf"):

        return default

    return value


def get_data_value(
    data,
    *keys,
    default=None,
):
    """
    Busca um valor utilizando diferentes
    nomes possíveis para a mesma informação.
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


def percent_value(
    value,
):
    """
    Normaliza percentuais.

    Exemplos:

    0.15 -> 15
    15   -> 15
    """

    value = safe_float(
        value
    )

    if value is None:

        return None

    if abs(value) <= 1:

        return value * 100

    return value


# ==========================================================
# SCORE TÉCNICO - BREAKDOWN
# ==========================================================

def get_score_breakdown(data):
    """
    Calcula a contribuição individual
    de cada indicador técnico.

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
            "Dados não fornecidos para o Score Técnico."
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
            "Dados ausentes para o Score Técnico: "
            + ", ".join(missing)
        )

    price = safe_float(
        data.get("price")
    )

    ma21 = safe_float(
        data.get("ma21")
    )

    ma200 = safe_float(
        data.get("ma200")
    )

    rsi = safe_float(
        data.get("rsi")
    )

    if (
        price is None
        or ma21 is None
        or ma200 is None
        or rsi is None
    ):

        raise ValueError(
            "Dados técnicos inválidos."
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

        ma21_signal = (
            "Positivo"
        )

        ma21_reason = (
            "Preço acima da MA21, "
            "indicando força no curto prazo."
        )

    elif price < ma21:

        ma21_points = -10

        ma21_signal = (
            "Negativo"
        )

        ma21_reason = (
            "Preço abaixo da MA21, "
            "indicando pressão no curto prazo."
        )

    else:

        ma21_points = 0

        ma21_signal = (
            "Neutro"
        )

        ma21_reason = (
            "Preço alinhado à MA21."
        )

    # ======================================================
    # MA200
    # ======================================================

    if price > ma200:

        ma200_points = 20

        ma200_signal = (
            "Positivo"
        )

        ma200_reason = (
            "Preço acima da MA200, "
            "indicando tendência positiva "
            "no longo prazo."
        )

    elif price < ma200:

        ma200_points = -20

        ma200_signal = (
            "Negativo"
        )

        ma200_reason = (
            "Preço abaixo da MA200, "
            "indicando fraqueza na tendência "
            "de longo prazo."
        )

    else:

        ma200_points = 0

        ma200_signal = (
            "Neutro"
        )

        ma200_reason = (
            "Preço alinhado à MA200."
        )

    # ======================================================
    # RSI
    # ======================================================

    if rsi <= RSI_OVERSOLD:

        rsi_points = 10

        rsi_signal = (
            "Positivo"
        )

        rsi_reason = (
            "RSI em região de sobrevenda, "
            "com possibilidade de recuperação."
        )

    elif rsi >= RSI_OVERBOUGHT:

        rsi_points = -10

        rsi_signal = (
            "Negativo"
        )

        rsi_reason = (
            "RSI em região de sobrecompra, "
            "aumentando o risco de correção."
        )

    else:

        rsi_points = 0

        rsi_signal = (
            "Neutro"
        )

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

            "points":
                ma21_points,

            "signal":
                ma21_signal,

            "reason":
                ma21_reason,
        },

        "ma200": {

            "points":
                ma200_points,

            "signal":
                ma200_signal,

            "reason":
                ma200_reason,
        },

        "rsi": {

            "points":
                rsi_points,

            "signal":
                rsi_signal,

            "reason":
                rsi_reason,
        },

        "raw_score":
            raw_score,

        "score":
            final_score,
    }


# ==========================================================
# SCORE TÉCNICO PRINCIPAL
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula o Score Técnico InvestIA.

    Mantido com este nome para preservar
    compatibilidade com as versões anteriores.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown[
        "score"
    ]


# ==========================================================
# SCORE FUNDAMENTALISTA - P/L
# ==========================================================

def score_price_to_earnings(
    value,
):
    """
    Avalia o indicador P/L.

    Quanto menor o múltiplo positivo,
    melhor a pontuação.

    Empresas com prejuízo normalmente
    apresentam P/L negativo e recebem
    pontuação negativa.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "price_to_earnings"
    ]

    value = safe_float(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "P/L não disponível.",
        }

    if value <= 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                "P/L não positivo, indicando "
                "ausência de lucro positivo "
                "no período analisado.",
        }

    if value <= 8:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"P/L de {value:.2f}, "
                "em faixa considerada atrativa.",
        }

    if value <= 15:

        return {

            "points": 5,

            "signal": "Positivo",

            "reason":
                f"P/L de {value:.2f}, "
                "em faixa moderada.",
        }

    if value <= 25:

        return {

            "points": 0,

            "signal": "Neutro",

            "reason":
                f"P/L de {value:.2f}, "
                "em faixa intermediária.",
        }

    return {

        "points": -weight,

        "signal": "Negativo",

        "reason":
            f"P/L de {value:.2f}, "
            "em patamar elevado.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - P/VP
# ==========================================================

def score_price_to_book(
    value,
):
    """
    Avalia o indicador P/VP.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "price_to_book"
    ]

    value = safe_float(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "P/VP não disponível.",
        }

    if value <= 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                "P/VP inválido ou patrimônio "
                "líquido negativo.",
        }

    if value <= 1:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"P/VP de {value:.2f}, "
                "indicando preço próximo ou "
                "abaixo do valor patrimonial.",
        }

    if value <= 2:

        return {

            "points": 5,

            "signal": "Positivo",

            "reason":
                f"P/VP de {value:.2f}, "
                "em faixa moderada.",
        }

    if value <= 4:

        return {

            "points": 0,

            "signal": "Neutro",

            "reason":
                f"P/VP de {value:.2f}, "
                "em faixa intermediária.",
        }

    return {

        "points": -weight,

        "signal": "Negativo",

        "reason":
            f"P/VP de {value:.2f}, "
            "em patamar elevado.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - ROE
# ==========================================================

def score_return_on_equity(
    value,
):
    """
    Avalia o ROE.

    Quanto maior o ROE positivo,
    melhor a rentabilidade sobre
    o patrimônio.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "return_on_equity"
    ]

    value = percent_value(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "ROE não disponível.",
        }

    if value < 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                f"ROE de {value:.2f}%, "
                "indicando rentabilidade negativa.",
        }

    if value >= 20:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"ROE de {value:.2f}%, "
                "indicando elevada rentabilidade.",
        }

    if value >= 12:

        return {

            "points": 8,

            "signal": "Positivo",

            "reason":
                f"ROE de {value:.2f}%, "
                "indicando boa rentabilidade.",
        }

    if value >= 5:

        return {

            "points": 2,

            "signal": "Neutro",

            "reason":
                f"ROE de {value:.2f}%, "
                "em nível moderado.",
        }

    return {

        "points": -8,

        "signal": "Negativo",

        "reason":
            f"ROE de {value:.2f}%, "
            "em nível baixo.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - DIVIDEND YIELD
# ==========================================================

def score_dividend_yield(
    value,
):
    """
    Avalia o Dividend Yield.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "dividend_yield"
    ]

    value = percent_value(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "Dividend Yield não disponível.",
        }

    if value < 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                "Dividend Yield inválido.",
        }

    if value >= 8:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"Dividend Yield de {value:.2f}%, "
                "em patamar elevado.",
        }

    if value >= 4:

        return {

            "points": 5,

            "signal": "Positivo",

            "reason":
                f"Dividend Yield de {value:.2f}%, "
                "em nível atrativo.",
        }

    if value >= 1:

        return {

            "points": 2,

            "signal": "Neutro",

            "reason":
                f"Dividend Yield de {value:.2f}%, "
                "em nível moderado.",
        }

    return {

        "points": 0,

        "signal": "Neutro",

        "reason":
            "Empresa apresenta baixo ou nenhum "
            "retorno recorrente em dividendos.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - MARGEM DE LUCRO
# ==========================================================

def score_profit_margin(
    value,
):
    """
    Avalia a margem líquida.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "profit_margin"
    ]

    value = percent_value(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "Margem de lucro não disponível.",
        }

    if value < 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                f"Margem líquida de {value:.2f}%, "
                "indicando prejuízo.",
        }

    if value >= 20:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"Margem líquida de {value:.2f}%, "
                "indicando alta eficiência.",
        }

    if value >= 10:

        return {

            "points": 5,

            "signal": "Positivo",

            "reason":
                f"Margem líquida de {value:.2f}%, "
                "indicando boa eficiência.",
        }

    if value >= 3:

        return {

            "points": 1,

            "signal": "Neutro",

            "reason":
                f"Margem líquida de {value:.2f}%, "
                "em nível moderado.",
        }

    return {

        "points": -5,

        "signal": "Negativo",

        "reason":
            f"Margem líquida de {value:.2f}%, "
            "em nível baixo.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - CRESCIMENTO DA RECEITA
# ==========================================================

def score_revenue_growth(
    value,
):
    """
    Avalia o crescimento da receita.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "revenue_growth"
    ]

    value = percent_value(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "Crescimento da receita não disponível.",
        }

    if value >= 20:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"Receita crescendo {value:.2f}%, "
                "indicando forte expansão.",
        }

    if value >= 5:

        return {

            "points": 5,

            "signal": "Positivo",

            "reason":
                f"Receita crescendo {value:.2f}%, "
                "indicando crescimento positivo.",
        }

    if value >= 0:

        return {

            "points": 1,

            "signal": "Neutro",

            "reason":
                f"Receita crescendo {value:.2f}%, "
                "em ritmo moderado.",
        }

    if value >= -10:

        return {

            "points": -5,

            "signal": "Negativo",

            "reason":
                f"Receita recuando {abs(value):.2f}%.",
        }

    return {

        "points": -weight,

        "signal": "Muito negativo",

        "reason":
            f"Receita recuando {abs(value):.2f}%, "
            "indicando contração relevante.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - DÍVIDA / PATRIMÔNIO
# ==========================================================

def score_debt_to_equity(
    value,
):
    """
    Avalia o endividamento.

    O Yahoo Finance normalmente fornece
    Debt to Equity em percentual.

    Exemplo:

    50 = dívida equivalente a 50%
         do patrimônio.
    """

    weight = FUNDAMENTAL_WEIGHTS[
        "debt_to_equity"
    ]

    value = safe_float(
        value
    )

    if value is None:

        return {

            "points": 0,

            "signal": "Indisponível",

            "reason":
                "Dívida/Patrimônio não disponível.",
        }

    if value < 0:

        return {

            "points": -weight,

            "signal": "Negativo",

            "reason":
                "Indicador de endividamento inválido.",
        }

    if value <= 50:

        return {

            "points": weight,

            "signal": "Muito positivo",

            "reason":
                f"Dívida/Patrimônio de {value:.2f}%, "
                "indicando baixo endividamento.",
        }

    if value <= 100:

        return {

            "points": 8,

            "signal": "Positivo",

            "reason":
                f"Dívida/Patrimônio de {value:.2f}%, "
                "em nível administrável.",
        }

    if value <= 200:

        return {

            "points": 0,

            "signal": "Neutro",

            "reason":
                f"Dívida/Patrimônio de {value:.2f}%, "
                "em nível elevado.",
        }

    if value <= 400:

        return {

            "points": -8,

            "signal": "Negativo",

            "reason":
                f"Dívida/Patrimônio de {value:.2f}%, "
                "indicando endividamento alto.",
        }

    return {

        "points": -weight,

        "signal": "Muito negativo",

        "reason":
            f"Dívida/Patrimônio de {value:.2f}%, "
            "indicando endividamento muito elevado.",
    }


# ==========================================================
# SCORE FUNDAMENTALISTA - BREAKDOWN
# ==========================================================

def get_fundamental_score_breakdown(
    fundamentals,
):
    """
    Calcula o detalhamento completo
    do Score Fundamentalista.

    O Score inicia em 50 pontos.

    Os indicadores ajustam a pontuação
    conforme sua qualidade.

    Indicadores sem dados não penalizam
    nem beneficiam o ativo.
    """

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ======================================================
    # EXTRAÇÃO DOS INDICADORES
    # ======================================================

    price_to_earnings = get_data_value(
        fundamentals,
        "price_to_earnings",
        "p_e",
        "pe",
        "trailing_pe",
    )

    price_to_book = get_data_value(
        fundamentals,
        "price_to_book",
        "p_b",
        "pb",
    )

    return_on_equity = get_data_value(
        fundamentals,
        "return_on_equity",
        "roe",
    )

    dividend_yield = get_data_value(
        fundamentals,
        "dividend_yield",
        "dy",
    )

    profit_margin = get_data_value(
        fundamentals,
        "profit_margin",
        "profit_margins",
    )

    revenue_growth = get_data_value(
        fundamentals,
        "revenue_growth",
        "growth",
    )

    debt_to_equity = get_data_value(
        fundamentals,
        "debt_to_equity",
        "debt_equity",
    )

    # ======================================================
    # CÁLCULO INDIVIDUAL
    # ======================================================

    pe_data = score_price_to_earnings(
        price_to_earnings
    )

    pb_data = score_price_to_book(
        price_to_book
    )

    roe_data = score_return_on_equity(
        return_on_equity
    )

    dividend_data = score_dividend_yield(
        dividend_yield
    )

    margin_data = score_profit_margin(
        profit_margin
    )

    growth_data = score_revenue_growth(
        revenue_growth
    )

    debt_data = score_debt_to_equity(
        debt_to_equity
    )

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    base = FUNDAMENTAL_SCORE_BASE

    raw_score = (

        base

        + pe_data["points"]

        + pb_data["points"]

        + roe_data["points"]

        + dividend_data["points"]

        + margin_data["points"]

        + growth_data["points"]

        + debt_data["points"]

    )

    final_score = clamp_score(
        raw_score
    )

    # ======================================================
    # COBERTURA DOS DADOS
    # ======================================================

    indicators = {

        "price_to_earnings":
            price_to_earnings,

        "price_to_book":
            price_to_book,

        "return_on_equity":
            return_on_equity,

        "dividend_yield":
            dividend_yield,

        "profit_margin":
            profit_margin,

        "revenue_growth":
            revenue_growth,

        "debt_to_equity":
            debt_to_equity,
    }

    available_indicators = sum(

        1
        for value
        in indicators.values()
        if safe_float(value) is not None

    )

    total_indicators = len(
        indicators
    )

    coverage = (
        available_indicators
        / total_indicators
        * 100
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "base":
            base,

        "price_to_earnings":
            pe_data,

        "price_to_book":
            pb_data,

        "return_on_equity":
            roe_data,

        "dividend_yield":
            dividend_data,

        "profit_margin":
            margin_data,

        "revenue_growth":
            growth_data,

        "debt_to_equity":
            debt_data,

        "raw_score":
            raw_score,

        "score":
            final_score,

        "coverage":
            coverage,

        "available_indicators":
            available_indicators,

        "total_indicators":
            total_indicators,
    }


# ==========================================================
# SCORE FUNDAMENTALISTA PRINCIPAL
# ==========================================================

def calculate_fundamental_score(
    fundamentals,
):
    """
    Calcula o Score Fundamentalista
    InvestIA de 0 a 100.
    """

    breakdown = get_fundamental_score_breakdown(
        fundamentals
    )

    return breakdown[
        "score"
    ]


# ==========================================================
# CLASSIFICAÇÃO DO SCORE
# ==========================================================

def classify_score(score):
    """
    Classifica qualquer Score InvestIA.
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
# CLASSIFICAÇÃO FUNDAMENTALISTA
# ==========================================================

def classify_fundamental_score(
    score,
):
    """
    Classificação específica do
    Score Fundamentalista.
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "FUNDAMENTOS MUITO FORTES"

    if score >= 65:

        return "FUNDAMENTOS FORTES"

    if score >= 50:

        return "FUNDAMENTOS NEUTROS"

    if score >= 35:

        return "FUNDAMENTOS FRACOS"

    return "FUNDAMENTOS MUITO FRACOS"


# ==========================================================
# SINAL
# ==========================================================

def classify_signal(score):
    """
    Define o sinal baseado no Score.
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
    Retorna o Score Técnico completo
    com classificação e breakdown.
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown[
        "score"
    ]

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


# ==========================================================
# SCORE FUNDAMENTALISTA COMPLETO
# ==========================================================

def calculate_fundamental_score_details(
    fundamentals,
):
    """
    Retorna o Score Fundamentalista completo
    com classificação, sinal e explicabilidade.
    """

    breakdown = get_fundamental_score_breakdown(
        fundamentals
    )

    score = breakdown[
        "score"
    ]

    coverage = breakdown.get(
        "coverage",
        0,
    )

    return {

        "score":
            score,

        "classification":
            classify_fundamental_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),

        "coverage":
            coverage,

        "available_indicators":
            breakdown.get(
                "available_indicators",
                0,
            ),

        "total_indicators":
            breakdown.get(
                "total_indicators",
                0,
            ),

        "breakdown":
            breakdown,
    }


# ==========================================================
# SCORE INTEGRADO
# ==========================================================

def calculate_integrated_score(
    technical_score,
    fundamental_score,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Combina o Score Técnico e o
    Score Fundamentalista.

    Padrão:

        50% Técnico
        50% Fundamentalista

    Os pesos são normalizados para evitar
    problemas caso a soma seja diferente de 1.
    """

    technical_score = clamp_score(
        technical_score
    )

    fundamental_score = clamp_score(
        fundamental_score
    )

    technical_weight = safe_float(
        technical_weight,
        0.50,
    )

    fundamental_weight = safe_float(
        fundamental_weight,
        0.50,
    )

    if technical_weight < 0:

        technical_weight = 0

    if fundamental_weight < 0:

        fundamental_weight = 0

    total_weight = (

        technical_weight

        + fundamental_weight

    )

    if total_weight <= 0:

        technical_weight = 0.50

        fundamental_weight = 0.50

        total_weight = 1

    technical_weight = (
        technical_weight
        / total_weight
    )

    fundamental_weight = (
        fundamental_weight
        / total_weight
    )

    raw_score = (

        technical_score
        * technical_weight

        + fundamental_score
        * fundamental_weight

    )

    score = clamp_score(
        raw_score
    )

    return {

        "score":
            score,

        "technical_score":
            technical_score,

        "fundamental_score":
            fundamental_score,

        "technical_weight":
            technical_weight,

        "fundamental_weight":
            fundamental_weight,

        "classification":
            classify_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),
    }


# ==========================================================
# SCORE INTEGRADO COMPLETO
# ==========================================================

def calculate_integrated_score_details(
    technical_data,
    fundamentals,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Executa o fluxo completo:

    Dados Técnicos
        ↓
    Score Técnico

    Dados Fundamentalistas
        ↓
    Score Fundamentalista

    Ambos
        ↓
    Score Integrado
    """

    technical_details = calculate_score_details(
        technical_data
    )

    fundamental_details = (
        calculate_fundamental_score_details(
            fundamentals
        )
    )

    integrated_details = calculate_integrated_score(

        technical_score=
            technical_details["score"],

        fundamental_score=
            fundamental_details["score"],

        technical_weight=
            technical_weight,

        fundamental_weight=
            fundamental_weight,
    )

    return {

        "technical":
            technical_details,

        "fundamental":
            fundamental_details,

        "integrated":
            integrated_details,
    }
