"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 1.6

Responsável por consolidar os indicadores técnicos
e o Score InvestIA 2.0.

A fonte oficial do Score é o módulo score.py.
"""

from typing import Any

from score import calculate_investia_score


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

MIN_SCORE = 0
MAX_SCORE = 100


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def get_recommendation(
    score: float,
) -> str:
    """
    Converte o Score InvestIA 2.0 em uma recomendação.

    80–100  = Compra Forte
    70–79   = Compra
    60–69   = Compra Moderada
    45–59   = Aguardar
    30–44   = Venda Moderada
    0–29    = Venda
    """

    score = _clamp(
        _safe_float(score)
    )

    if score >= 80:

        return "Compra Forte"

    if score >= 70:

        return "Compra"

    if score >= 60:

        return "Compra Moderada"

    if score >= 45:

        return "Aguardar"

    if score >= 30:

        return "Venda Moderada"

    return "Venda"


# ==========================================================
# TENDÊNCIA
# ==========================================================

def get_trend(
    trend_score: float,
) -> str:
    """
    Interpreta o score de tendência.

    70+       = Positiva
    55–69     = Moderadamente Positiva
    45–54     = Neutra
    30–44     = Moderadamente Negativa
    <30       = Negativa
    """

    trend_score = _clamp(
        _safe_float(
            trend_score,
            50.0,
        )
    )

    if trend_score >= 70:

        return "Positiva"

    if trend_score >= 55:

        return "Moderadamente Positiva"

    if trend_score >= 45:

        return "Neutra"

    if trend_score >= 30:

        return "Moderadamente Negativa"

    return "Negativa"


# ==========================================================
# CLASSIFICAÇÃO DE RISCO
# ==========================================================

def get_risk(
    risk_score: float,
) -> str:
    """
    Interpreta o Score de Risco.

    IMPORTANTE:
    Quanto maior o risk_score, melhor o controle
    de volatilidade.

    80+       = Baixo
    60–79     = Moderado
    40–59     = Elevado
    <40       = Alto
    """

    risk_score = _clamp(
        _safe_float(
            risk_score,
            50.0,
        )
    )

    if risk_score >= 80:

        return "Baixo"

    if risk_score >= 60:

        return "Moderado"

    if risk_score >= 40:

        return "Elevado"

    return "Alto"


# ==========================================================
# CONSOLIDAÇÃO DOS INDICADORES
# ==========================================================

def _prepare_indicators(
    data: dict,
) -> dict:

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            "Os dados da análise devem ser um dicionário."
        )

    required_fields = [
        "price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
    ]

    missing = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing:

        raise ValueError(
            "Indicadores ausentes: "
            + ", ".join(missing)
        )

    return {

        "price": _safe_float(
            data["price"]
        ),

        "ma21": _safe_float(
            data["ma21"]
        ),

        "ma200": _safe_float(
            data["ma200"]
        ),

        "rsi": _safe_float(
            data["rsi"]
        ),

        "volatility": _safe_float(
            data["volatility"]
        ),
    }


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data: dict,
) -> dict:
    """
    Executa a análise completa do ativo.

    O cálculo quantitativo é delegado ao score.py.

    Retorna um dicionário padronizado para o app.py.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    indicators = _prepare_indicators(
        data
    )

    # ======================================================
    # SCORE INVESTIA 2.0
    # ======================================================

    score_result = calculate_investia_score(
        indicators
    )

    # ======================================================
    # SCORE PRINCIPAL
    # ======================================================

    score = _clamp(
        _safe_float(
            score_result.get(
                "score",
                50.0,
            )
        )
    )

    # ======================================================
    # SCORES INDIVIDUAIS
    # ======================================================

    rsi_score = _clamp(
        _safe_float(
            score_result.get(
                "rsi",
                50.0,
            )
        )
    )

    ma21_score = _clamp(
        _safe_float(
            score_result.get(
                "ma21",
                50.0,
            )
        )
    )

    ma200_score = _clamp(
        _safe_float(
            score_result.get(
                "ma200",
                50.0,
            )
        )
    )

    trend_score = _clamp(
        _safe_float(
            score_result.get(
                "trend",
                50.0,
            )
        )
    )

    risk_score = _clamp(
        _safe_float(
            score_result.get(
                "risk",
                50.0,
            )
        )
    )

    technical_score = _clamp(
        _safe_float(
            score_result.get(
                "technical",
                50.0,
            )
        )
    )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    classification = score_result.get(
        "classification",
        "INDEFINIDO",
    )

    signal = score_result.get(
        "signal",
        "INDEFINIDO",
    )

    # ======================================================
    # INTERPRETAÇÕES
    # ======================================================

    trend = get_trend(
        trend_score
    )

    risk = get_risk(
        risk_score
    )

    recommendation = get_recommendation(
        score
    )

    # ======================================================
    # FUNDAMENTAÇÃO
    # ======================================================

    reasons = score_result.get(
        "reasons",
        [],
    )

    if not isinstance(
        reasons,
        list,
    ):

        reasons = []

    # ======================================================
    # RESULTADO CONSOLIDADO
    # ======================================================

    return {

        # --------------------------------------------------
        # Score principal
        # --------------------------------------------------

        "score": round(
            score,
            2,
        ),

        "classification": classification,

        "signal": signal,

        "recommendation": recommendation,

        # --------------------------------------------------
        # Tendência
        # --------------------------------------------------

        "trend": trend,

        "trend_score": round(
            trend_score,
            2,
        ),

        # --------------------------------------------------
        # Risco
        # --------------------------------------------------

        "risk": risk,

        "risk_score": round(
            risk_score,
            2,
        ),

        # --------------------------------------------------
        # Componentes do Score
        # --------------------------------------------------

        "rsi_score": round(
            rsi_score,
            2,
        ),

        "ma21_score": round(
            ma21_score,
            2,
        ),

        "ma200_score": round(
            ma200_score,
            2,
        ),

        "technical": round(
            technical_score,
            2,
        ),

        "technical_score": round(
            technical_score,
            2,
        ),

        # --------------------------------------------------
        # Indicadores originais
        # --------------------------------------------------

        "price": indicators["price"],

        "ma21": indicators["ma21"],

        "ma200": indicators["ma200"],

        "rsi": indicators["rsi"],

        "volatility": indicators["volatility"],

        # --------------------------------------------------
        # Fundamentação
        # --------------------------------------------------

        "reasons": reasons,

        "justificativas": reasons,
    }
