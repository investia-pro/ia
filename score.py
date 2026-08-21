"""
InvestIA PRO
Motor de Score

Versão: v0.7
Fase: 3.0.5 - Histórico e Evolução dos Scores

Responsabilidades:
- Calcular Score Técnico atual
- Calcular detalhamento do Score
- Classificar Score
- Definir sinal operacional
- Calcular Score Técnico histórico
- Identificar evolução do Score
"""

import pandas as pd

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

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

    if pd.isna(value):

        return default

    return value


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(
    score,
):
    """
    Mantém o Score entre 0 e 100.
    """

    score = safe_float(
        score,
        default=50,
    )

    return max(
        0,
        min(
            100,
            int(round(score)),
        ),
    )


# ==========================================================
# VALIDAÇÃO DOS DADOS
# ==========================================================

def validate_score_data(
    data,
):
    """
    Valida os dados necessários para
    cálculo do Score Técnico.
    """

    if not isinstance(
        data,
        dict,
    ):

        return False

    required_fields = [

        "price",
        "ma21",
        "ma200",
        "rsi",

    ]

    for field in required_fields:

        if field not in data:

            return False

        if safe_float(
            data.get(field)
        ) is None:

            return False

    return True


# ==========================================================
# CONTRIBUIÇÃO DOS INDICADORES
# ==========================================================

def get_score_breakdown(
    data,
):
    """
    Calcula a contribuição individual
    dos indicadores para o Score.

    Estrutura do Score:

    Base:
        50 pontos

    MA21:
        +10 / -10 / 0

    MA200:
        +20 / -20 / 0

    RSI:
        +10 / -10 / 0
    """

    if not validate_score_data(
        data
    ):

        raise ValueError(
            "Dados insuficientes para "
            "calcular o Score Técnico."
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

    # ======================================================
    # SCORE BASE
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
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(
    data,
):
    """
    Calcula o Score Técnico InvestIA
    entre 0 e 100.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown[
        "score"
    ]


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(
    score,
):
    """
    Classifica o Score Técnico.
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
# SINAL
# ==========================================================

def classify_signal(
    score,
):
    """
    Define o sinal operacional
    do Score.
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
# NÍVEL DO SINAL
# ==========================================================

def get_signal_level(
    score,
):
    """
    Define a intensidade do sinal.
    """

    score = clamp_score(
        score
    )

    if score >= 85:

        return "Muito forte"

    if score >= BUY_SCORE:

        return "Forte"

    if score > SELL_SCORE:

        return "Moderado"

    if score <= 15:

        return "Muito forte"

    return "Forte"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    signal,
):
    """
    Retorna um ícone visual
    para o sinal.
    """

    signal = str(
        signal
    ).upper()

    if signal == "POSITIVO":

        return "🟢"

    if signal == "NEGATIVO":

        return "🔴"

    return "🟡"


# ==========================================================
# SCORE COMPLETO
# ==========================================================

def calculate_score_details(
    data,
):
    """
    Retorna o Score completo
    com classificação, sinal
    e detalhamento.
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown[
        "score"
    ]

    signal = classify_signal(
        score
    )

    return {

        "score": score,

        "technical_score": score,

        "classification":
            classify_score(
                score
            ),

        "signal":
            signal,

        "qualified_signal":
            signal,

        "signal_level":
            get_signal_level(
                score
            ),

        "signal_icon":
            get_signal_icon(
                signal
            ),

        "breakdown":
            breakdown,
    }


# ==========================================================
# SCORE HISTÓRICO - LINHA INDIVIDUAL
# ==========================================================

def calculate_historical_score_row(
    row,
):
    """
    Calcula o Score Técnico para
    uma linha do histórico.

    A linha precisa possuir:

    - price
    - ma21
    - ma200
    - rsi
    """

    if row is None:

        return None

    if isinstance(
        row,
        pd.Series,
    ):

        data = row.to_dict()

    elif isinstance(
        row,
        dict,
    ):

        data = row

    else:

        return None

    if not validate_score_data(
        data
    ):

        return None

    try:

        details = calculate_score_details(
            data
        )

    except Exception:

        return None

    return details


# ==========================================================
# SCORE TÉCNICO HISTÓRICO
# ==========================================================

def calculate_historical_scores(
    historical_indicators,
):
    """
    Calcula o Score Técnico para
    cada ponto do histórico.

    Espera um DataFrame contendo:

    - price
    - ma21
    - ma200
    - rsi

    Retorna DataFrame com:

    - price
    - technical_score
    - classification
    - signal
    """

    if not isinstance(
        historical_indicators,
        pd.DataFrame,
    ):

        return pd.DataFrame()

    if historical_indicators.empty:

        return pd.DataFrame()

    required_columns = [

        "price",
        "ma21",
        "ma200",
        "rsi",

    ]

    for column in required_columns:

        if column not in historical_indicators.columns:

            return pd.DataFrame()

    results = []

    for index, row in historical_indicators.iterrows():

        details = calculate_historical_score_row(
            row
        )

        if details is None:

            continue

        results.append({

            "date":
                index,

            "price":
                safe_float(
                    row.get(
                        "price"
                    )
                ),

            "technical_score":
                details["score"],

            "classification":
                details["classification"],

            "signal":
                details["signal"],

            "signal_level":
                details["signal_level"],

        })

    if not results:

        return pd.DataFrame()

    score_history = pd.DataFrame(
        results
    )

    score_history = score_history.set_index(
        "date"
    )

    return score_history


# ==========================================================
# VARIAÇÃO DO SCORE
# ==========================================================

def get_score_variation(
    score_history,
    periods=21,
):
    """
    Calcula a variação do Score
    em relação a um período anterior.

    Por padrão:
    21 períodos úteis.
    """

    if not isinstance(
        score_history,
        pd.DataFrame,
    ):

        return None

    if score_history.empty:

        return None

    if "technical_score" not in score_history.columns:

        return None

    scores = (
        score_history[
            "technical_score"
        ]
        .dropna()
    )

    if len(scores) < 2:

        return None

    current_score = safe_float(
        scores.iloc[-1]
    )

    reference_position = max(
        0,
        len(scores) - 1 - periods,
    )

    previous_score = safe_float(
        scores.iloc[
            reference_position
        ]
    )

    if (
        current_score is None
        or previous_score is None
    ):

        return None

    return current_score - previous_score


# ==========================================================
# DIREÇÃO DA EVOLUÇÃO
# ==========================================================

def classify_score_evolution(
    variation,
):
    """
    Classifica a direção da evolução
    do Score.
    """

    variation = safe_float(
        variation
    )

    if variation is None:

        return "SEM DADOS"

    if variation >= 10:

        return "MELHORANDO FORTE"

    if variation > 0:

        return "MELHORANDO"

    if variation <= -10:

        return "PIORANDO FORTE"

    if variation < 0:

        return "PIORANDO"

    return "ESTÁVEL"


# ==========================================================
# MUDANÇA DE SINAL
# ==========================================================

def get_signal_change(
    score_history,
    periods=21,
):
    """
    Verifica se ocorreu mudança
    de sinal durante o período.
    """

    if not isinstance(
        score_history,
        pd.DataFrame,
    ):

        return None

    if score_history.empty:

        return None

    if "signal" not in score_history.columns:

        return None

    signals = (
        score_history[
            "signal"
        ]
        .dropna()
    )

    if len(signals) < 2:

        return None

    current_signal = str(
        signals.iloc[-1]
    )

    reference_position = max(
        0,
        len(signals) - 1 - periods,
    )

    previous_signal = str(
        signals.iloc[
            reference_position
        ]
    )

    return {

        "changed":
            current_signal != previous_signal,

        "previous":
            previous_signal,

        "current":
            current_signal,
    }


# ==========================================================
# CONSISTÊNCIA DO SCORE
# ==========================================================

def calculate_score_consistency(
    score_history,
    periods=21,
):
    """
    Mede a consistência do Score.

    Quanto menor a oscilação,
    maior a consistência.
    """

    if not isinstance(
        score_history,
        pd.DataFrame,
    ):

        return {

            "level": "SEM DADOS",
            "std": None,
        }

    if score_history.empty:

        return {

            "level": "SEM DADOS",
            "std": None,
        }

    if "technical_score" not in score_history.columns:

        return {

            "level": "SEM DADOS",
            "std": None,
        }

    scores = (
        score_history[
            "technical_score"
        ]
        .dropna()
        .tail(
            periods
        )
    )

    if len(scores) < 2:

        return {

            "level": "SEM DADOS",
            "std": None,
        }

    std = safe_float(
        scores.std()
    )

    if std is None:

        return {

            "level": "SEM DADOS",
            "std": None,
        }

    if std <= 5:

        level = "ALTA"

    elif std <= 10:

        level = "MÉDIA"

    else:

        level = "BAIXA"

    return {

        "level": level,

        "std": std,
    }


# ==========================================================
# RESUMO DA EVOLUÇÃO
# ==========================================================

def analyze_score_history(
    score_history,
    periods=21,
):
    """
    Gera um resumo executivo
    da evolução histórica do Score.
    """

    if not isinstance(
        score_history,
        pd.DataFrame,
    ):

        return {}

    if score_history.empty:

        return {}

    if "technical_score" not in score_history.columns:

        return {}

    scores = (
        score_history[
            "technical_score"
        ]
        .dropna()
    )

    if scores.empty:

        return {}

    current_score = safe_float(
        scores.iloc[-1]
    )

    previous_score = None

    if len(scores) >= 2:

        previous_score = safe_float(
            scores.iloc[-2]
        )

    variation = get_score_variation(
        score_history,
        periods=periods,
    )

    evolution = classify_score_evolution(
        variation
    )

    signal_change = get_signal_change(
        score_history,
        periods=periods,
    )

    consistency = calculate_score_consistency(
        score_history,
        periods=periods,
    )

    return {

        "current_score":
            current_score,

        "previous_score":
            previous_score,

        "variation":
            variation,

        "evolution":
            evolution,

        "signal_change":
            signal_change,

        "consistency":
            consistency.get(
                "level"
            ),

        "score_std":
            consistency.get(
                "std"
            ),

        "maximum_score":
            safe_float(
                scores.tail(
                    periods
                ).max()
            ),

        "minimum_score":
            safe_float(
                scores.tail(
                    periods
                ).min()
            ),

        "average_score":
            safe_float(
                scores.tail(
                    periods
                ).mean()
            ),
    }


# ==========================================================
# PIPELINE COMPLETO DO HISTÓRICO
# ==========================================================

def calculate_historical_score_analysis(
    historical_indicators,
    periods=21,
):
    """
    Executa o pipeline completo
    de análise histórica.

    Retorna:

    {
        "history": DataFrame,
        "summary": {...}
    }
    """

    score_history = calculate_historical_scores(
        historical_indicators
    )

    if score_history.empty:

        return {

            "history":
                pd.DataFrame(),

            "summary":
                {},
        }

    summary = analyze_score_history(
        score_history,
        periods=periods,
    )

    return {

        "history":
            score_history,

        "summary":
            summary,
    }
