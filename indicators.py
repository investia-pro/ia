"""
InvestIA PRO
Indicadores Técnicos

Versão: v0.6
Fase: 2.9.4 - Validação de Consistência dos Indicadores
"""

import math

import pandas as pd


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

RSI_MIN = 0.0
RSI_MAX = 100.0

MIN_PRICE = 0.0
MIN_VOLATILITY = 0.0

MA21_PERIOD = 21
MA200_PERIOD = 200
RSI_PERIOD = 14


# ==========================================================
# CONVERSÃO NUMÉRICA
# ==========================================================

def _safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.

    Retorna default quando:
        - valor é None;
        - valor não é numérico;
        - valor é NaN;
        - valor é infinito.
    """

    try:

        if value is None:
            return default

        value = float(value)

        if not math.isfinite(
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
# VALIDAÇÃO NUMÉRICA
# ==========================================================

def _is_valid_number(
    value,
):
    """
    Verifica se um valor é numérico,
    finito e válido.
    """

    return (
        _safe_float(
            value
        )
        is not None
    )


# ==========================================================
# LIMPEZA DO HISTÓRICO
# ==========================================================

def _clean_history(
    history,
):
    """
    Limpa e valida o histórico de preços.

    Garante a existência da coluna Close
    e remove valores inválidos.
    """

    if history is None:

        return None

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:

        return None

    data = history.copy()

    # ------------------------------------------------------
    # NORMALIZAÇÃO DAS COLUNAS
    # ------------------------------------------------------

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    # ------------------------------------------------------
    # LOCALIZAÇÃO DO CLOSE
    # ------------------------------------------------------

    close_column = None

    for column in data.columns:

        if str(
            column
        ).lower() == "close":

            close_column = column

            break

    if close_column is None:

        return None

    # ------------------------------------------------------
    # CONVERSÃO
    # ------------------------------------------------------

    data["Close"] = pd.to_numeric(
        data[close_column],
        errors="coerce",
    )

    # ------------------------------------------------------
    # REMOÇÃO DE INFINITOS
    # ------------------------------------------------------

    data = data.replace(
        [
            float("inf"),
            float("-inf"),
        ],
        pd.NA,
    )

    # ------------------------------------------------------
    # REMOÇÃO DE CLOSE INVÁLIDO
    # ------------------------------------------------------

    data = data.dropna(
        subset=[
            "Close"
        ]
    )

    # ------------------------------------------------------
    # PREÇOS POSITIVOS
    # ------------------------------------------------------

    data = data[
        data["Close"] > 0
    ]

    # ------------------------------------------------------
    # VERIFICAÇÃO FINAL
    # ------------------------------------------------------

    if data.empty:

        return None

    # ------------------------------------------------------
    # ORDENAÇÃO
    # ------------------------------------------------------

    try:

        data = data.sort_index()

    except Exception:

        pass

    return data


# ==========================================================
# MÉDIA MÓVEL
# ==========================================================

def _calculate_moving_average(
    close,
    window,
):
    """
    Calcula a Média Móvel Simples (SMA).

    Retorna None quando não existem dados
    suficientes.
    """

    if close is None:

        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        )

        series = series.dropna()

        if len(series) < window:

            return None

        result = series.rolling(
            window=window,
            min_periods=window,
        ).mean()

        value = result.iloc[-1]

        return _safe_float(
            value
        )

    except Exception:

        return None


# ==========================================================
# RSI
# ==========================================================

def _calculate_rsi(
    close,
    period=RSI_PERIOD,
):
    """
    Calcula o RSI.

    O resultado é limitado entre 0 e 100.
    """

    if close is None:

        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        ).dropna()

        # --------------------------------------------------
        # DADOS INSUFICIENTES
        # --------------------------------------------------

        if len(series) < period + 1:

            return None

        delta = series.diff()

        gains = delta.clip(
            lower=0
        )

        losses = -delta.clip(
            upper=0
        )

        average_gain = gains.rolling(
            window=period,
            min_periods=period,
        ).mean()

        average_loss = losses.rolling(
            window=period,
            min_periods=period,
        ).mean()

        gain = _safe_float(
            average_gain.iloc[-1]
        )

        loss = _safe_float(
            average_loss.iloc[-1]
        )

        if gain is None:

            return None

        if loss is None:

            return None

        # --------------------------------------------------
        # MERCADO SEM PERDAS
        # --------------------------------------------------

        if loss == 0:

            if gain > 0:

                return 100.0

            return 50.0

        relative_strength = (
            gain / loss
        )

        rsi = (
            100
            - (
                100
                / (
                    1
                    + relative_strength
                )
            )
        )

        rsi = _safe_float(
            rsi
        )

        if rsi is None:

            return None

        # --------------------------------------------------
        # LIMITAÇÃO DE SEGURANÇA
        # --------------------------------------------------

        return max(
            RSI_MIN,
            min(
                RSI_MAX,
                rsi,
            ),
        )

    except Exception:

        return None


# ==========================================================
# VOLATILIDADE
# ==========================================================

def _calculate_volatility(
    close,
):
    """
    Calcula a volatilidade histórica
    através do desvio padrão dos
    retornos percentuais.
    """

    if close is None:

        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        ).dropna()

        if len(series) < 2:

            return None

        returns = series.pct_change()

        returns = returns.replace(
            [
                float("inf"),
                float("-inf"),
            ],
            pd.NA,
        )

        returns = returns.dropna()

        if returns.empty:

            return None

        volatility = returns.std()

        volatility = _safe_float(
            volatility
        )

        if volatility is None:

            return None

        if volatility < MIN_VOLATILITY:

            return 0.0

        return volatility

    except Exception:

        return None


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def _get_last_price(
    close,
):
    """
    Obtém o último preço válido.
    """

    if close is None:

        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        ).dropna()

        if series.empty:

            return None

        value = _safe_float(
            series.iloc[-1]
        )

        if value is None:

            return None

        if value <= MIN_PRICE:

            return None

        return value

    except Exception:

        return None


# ==========================================================
# VALIDAÇÃO DE CONSISTÊNCIA
# ==========================================================

def validate_indicator_consistency(
    indicators,
):
    """
    Valida a consistência dos indicadores
    técnicos calculados.

    Regras:

        Preço:
            > 0

        MA21:
            > 0

        MA200:
            > 0

        RSI:
            entre 0 e 100

        Volatilidade:
            >= 0
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return {

            "valid": False,

            "status": "INCONSISTENTE",

            "status_icon": "🔴",

            "invalid": [
                "estrutura"
            ],

            "warnings": [],

            "message":
                "Estrutura dos indicadores inválida.",

        }

    invalid = []
    warnings = []

    # ======================================================
    # PREÇO
    # ======================================================

    price = indicators.get(
        "price"
    )

    if not _is_valid_number(
        price
    ):

        invalid.append(
            "price"
        )

    elif float(price) <= 0:

        invalid.append(
            "price"
        )

    # ======================================================
    # MA21
    # ======================================================

    ma21 = indicators.get(
        "ma21"
    )

    if ma21 is None:

        warnings.append(
            "ma21"
        )

    elif not _is_valid_number(
        ma21
    ):

        invalid.append(
            "ma21"
        )

    elif float(ma21) <= 0:

        invalid.append(
            "ma21"
        )

    # ======================================================
    # MA200
    # ======================================================

    ma200 = indicators.get(
        "ma200"
    )

    if ma200 is None:

        warnings.append(
            "ma200"
        )

    elif not _is_valid_number(
        ma200
    ):

        invalid.append(
            "ma200"
        )

    elif float(ma200) <= 0:

        invalid.append(
            "ma200"
        )

    # ======================================================
    # RSI
    # ======================================================

    rsi = indicators.get(
        "rsi"
    )

    if rsi is None:

        invalid.append(
            "rsi"
        )

    elif not _is_valid_number(
        rsi
    ):

        invalid.append(
            "rsi"
        )

    else:

        rsi = float(
            rsi
        )

        if (
            rsi < RSI_MIN
            or rsi > RSI_MAX
        ):

            invalid.append(
                "rsi"
            )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    volatility = indicators.get(
        "volatility"
    )

    if volatility is None:

        invalid.append(
            "volatility"
        )

    elif not _is_valid_number(
        volatility
    ):

        invalid.append(
            "volatility"
        )

    elif float(volatility) < 0:

        invalid.append(
            "volatility"
        )

    # ======================================================
    # CONSISTÊNCIA PREÇO x MÉDIAS
    # ======================================================

    if (
        _is_valid_number(price)
        and _is_valid_number(ma21)
        and float(price) <= 0
    ):

        invalid.append(
            "price"
        )

    if (
        _is_valid_number(price)
        and _is_valid_number(ma200)
        and float(price) <= 0
    ):

        invalid.append(
            "price"
        )

    # ======================================================
    # REMOÇÃO DE DUPLICADOS
    # ======================================================

    invalid = list(
        dict.fromkeys(
            invalid
        )
    )

    warnings = list(
        dict.fromkeys(
            warnings
        )
    )

    # ======================================================
    # STATUS
    # ======================================================

    if invalid:

        return {

            "valid": False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "invalid":
                invalid,

            "warnings":
                warnings,

            "message":
                (
                    "Foram encontrados "
                    "indicadores com valores "
                    "inconsistentes: "
                    + ", ".join(
                        invalid
                    )
                    + "."
                ),

        }

    if warnings:

        return {

            "valid": True,

            "status":
                "PARCIAL",

            "status_icon":
                "🟡",

            "invalid":
                [],

            "warnings":
                warnings,

            "message":
                (
                    "Os indicadores principais "
                    "estão válidos, porém alguns "
                    "indicadores não estão disponíveis: "
                    + ", ".join(
                        warnings
                    )
                    + "."
                ),

        }

    return {

        "valid": True,

        "status":
            "CONSISTENTE",

        "status_icon":
            "🟢",

        "invalid":
            [],

        "warnings":
            [],

        "message":
            (
                "Todos os indicadores "
                "foram validados com sucesso."
            ),

    }


# ==========================================================
# CÁLCULO PRINCIPAL
# ==========================================================

def calculate_indicators(
    market,
):
    """
    Calcula os indicadores técnicos
    utilizados pelo InvestIA PRO.
    """

    # ======================================================
    # VALIDAÇÃO DO MARKET
    # ======================================================

    if market is None:

        raise ValueError(
            "Dados de mercado não fornecidos."
        )

    if not isinstance(
        market,
        dict,
    ):

        raise ValueError(
            "Formato dos dados de mercado inválido."
        )

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = market.get(
        "history"
    )

    if history is None:

        raise ValueError(
            "Histórico do mercado não encontrado."
        )

    # ======================================================
    # LIMPEZA
    # ======================================================

    history = _clean_history(
        history
    )

    if history is None:

        raise ValueError(
            "Histórico de preços inválido ou vazio."
        )

    # ======================================================
    # CLOSE
    # ======================================================

    close = history[
        "Close"
    ]

    if close.empty:

        raise ValueError(
            "A série de fechamento está vazia."
        )

    # ======================================================
    # PREÇO
    # ======================================================

    price = _get_last_price(
        close
    )

    if price is None:

        raise ValueError(
            "Não foi possível determinar "
            "um preço válido."
        )

    # ======================================================
    # MA21
    # ======================================================

    ma21 = _calculate_moving_average(
        close,
        MA21_PERIOD,
    )

    # ======================================================
    # MA200
    # ======================================================

    ma200 = _calculate_moving_average(
        close,
        MA200_PERIOD,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi = _calculate_rsi(
        close,
        RSI_PERIOD,
    )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    volatility = _calculate_volatility(
        close
    )

    # ======================================================
    # ATIVO
    # ======================================================

    asset = market.get(
        "asset"
    )

    if asset is None:

        asset = market.get(
            "ticker"
        )

    if asset is None:

        asset = ""

    asset = str(
        asset
    ).strip().upper()

    # ======================================================
    # RESULTADO
    # ======================================================

    indicators = {

        "asset":
            asset,

        "price":
            price,

        "ma21":
            ma21,

        "ma200":
            ma200,

        "rsi":
            rsi,

        "volatility":
            volatility,

        "history":
            history,

    }

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    consistency = validate_indicator_consistency(
        indicators
    )

    indicators[
        "consistency"
    ] = consistency

    indicators[
        "indicators_valid"
    ] = consistency[
        "valid"
    ]

    indicators[
        "indicators_status"
    ] = consistency[
        "status"
    ]

    indicators[
        "indicators_status_icon"
    ] = consistency[
        "status_icon"
    ]

    indicators[
        "invalid_indicators"
    ] = consistency[
        "invalid"
    ]

    indicators[
        "indicator_warnings"
    ] = consistency[
        "warnings"
    ]

    return indicators


# ==========================================================
# VALIDAÇÃO GERAL
# ==========================================================

def validate_indicators(
    indicators,
):
    """
    Verifica se os indicadores essenciais
    possuem valores válidos.

    MA21 e MA200 podem ser None quando
    não existe histórico suficiente.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return False

    # ------------------------------------------------------
    # PREÇO
    # ------------------------------------------------------

    price = indicators.get(
        "price"
    )

    if not _is_valid_number(
        price
    ):

        return False

    if float(price) <= 0:

        return False

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    rsi = indicators.get(
        "rsi"
    )

    if not _is_valid_number(
        rsi
    ):

        return False

    rsi = float(
        rsi
    )

    if (
        rsi < RSI_MIN
        or rsi > RSI_MAX
    ):

        return False

    # ------------------------------------------------------
    # VOLATILIDADE
    # ------------------------------------------------------

    volatility = indicators.get(
        "volatility"
    )

    if not _is_valid_number(
        volatility
    ):

        return False

    if float(volatility) < 0:

        return False

    # ------------------------------------------------------
    # CONSISTÊNCIA
    # ------------------------------------------------------

    consistency = validate_indicator_consistency(
        indicators
    )

    return consistency[
        "valid"
    ]


# ==========================================================
# STATUS DOS INDICADORES
# ==========================================================

def get_indicator_status(
    indicators,
):
    """
    Retorna o status detalhado
    dos indicadores.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return {

            "valid":
                False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "price":
                False,

            "ma21":
                False,

            "ma200":
                False,

            "rsi":
                False,

            "volatility":
                False,

            "invalid":
                [
                    "estrutura"
                ],

            "warnings":
                [],

        }

    consistency = (
        indicators.get(
            "consistency"
        )
    )

    if not isinstance(
        consistency,
        dict,
    ):

        consistency = validate_indicator_consistency(
            indicators
        )

    return {

        "valid":
            consistency.get(
                "valid",
                False,
            ),

        "status":
            consistency.get(
                "status",
                "INCONSISTENTE",
            ),

        "status_icon":
            consistency.get(
                "status_icon",
                "🔴",
            ),

        "price":
            _is_valid_number(
                indicators.get(
                    "price"
                )
            ),

        "ma21":
            _is_valid_number(
                indicators.get(
                    "ma21"
                )
            ),

        "ma200":
            _is_valid_number(
                indicators.get(
                    "ma200"
                )
            ),

        "rsi":
            _is_valid_number(
                indicators.get(
                    "rsi"
                )
            ),

        "volatility":
            _is_valid_number(
                indicators.get(
                    "volatility"
                )
            ),

        "invalid":
            consistency.get(
                "invalid",
                [],
            ),

        "warnings":
            consistency.get(
                "warnings",
                [],
            ),

        "message":
            consistency.get(
                "message",
                "",
            ),

    }
