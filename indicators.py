"""
InvestIA PRO
Indicadores Técnicos

Versão: v0.6
Fase: 2.9.1 - Tratamento Robusto de Dados
"""

import math

import pandas as pd


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _safe_float(value, default=None):
    """
    Converte um valor para float com segurança.

    Retorna default quando o valor é:
    - None
    - NaN
    - infinito
    - não numérico
    """

    try:

        if value is None:
            return default

        value = float(value)

        if not math.isfinite(value):
            return default

        return value

    except (
        TypeError,
        ValueError,
    ):

        return default


def _clean_history(history):
    """
    Limpa e valida o histórico de preços.

    Mantém somente linhas válidas e garante
    que a coluna Close seja numérica.
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
    # PROCURA DA COLUNA CLOSE
    # ------------------------------------------------------

    close_column = None

    for column in data.columns:

        if str(column).lower() == "close":

            close_column = column

            break

    if close_column is None:
        return None

    # ------------------------------------------------------
    # CONVERSÃO DO CLOSE
    # ------------------------------------------------------

    data["Close"] = pd.to_numeric(
        data[close_column],
        errors="coerce",
    )

    # ------------------------------------------------------
    # REMOÇÃO DE VALORES INVÁLIDOS
    # ------------------------------------------------------

    data = data.replace(
        [
            float("inf"),
            float("-inf"),
        ],
        pd.NA,
    )

    data = data.dropna(
        subset=["Close"]
    )

    # ------------------------------------------------------
    # VALIDAÇÃO FINAL
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
    Calcula média móvel simples (SMA).

    Retorna None caso não existam dados
    suficientes para o cálculo.
    """

    if close is None:
        return None

    if len(close) < window:
        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        )

        series = series.dropna()

        if len(series) < window:
            return None

        value = series.rolling(
            window=window,
            min_periods=window,
        ).mean().iloc[-1]

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
    period=14,
):
    """
    Calcula o RSI utilizando o método
    tradicional de ganhos e perdas médias.

    Retorna None quando não existem dados
    suficientes.
    """

    if close is None:
        return None

    try:

        series = pd.to_numeric(
            close,
            errors="coerce",
        ).dropna()

        # --------------------------------------------------
        # RSI necessita de pelo menos period + 1 preços
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

        gain = average_gain.iloc[-1]
        loss = average_loss.iloc[-1]

        gain = _safe_float(
            gain
        )

        loss = _safe_float(
            loss
        )

        if gain is None:
            return None

        if loss is None:
            return None

        # --------------------------------------------------
        # Casos extremos
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
        # Limitação de segurança
        # --------------------------------------------------

        return max(
            0.0,
            min(
                100.0,
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
    utilizando o desvio padrão dos
    retornos percentuais diários.

    O resultado é decimal.

    Exemplo:

        0.02 = 2%
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

        return _safe_float(
            volatility
        )

    except Exception:

        return None


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def _get_last_price(
    close,
):
    """
    Obtém o último preço válido
    do histórico.
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

        return _safe_float(
            series.iloc[-1]
        )

    except Exception:

        return None


# ==========================================================
# CÁLCULO PRINCIPAL
# ==========================================================

def calculate_indicators(
    market,
):
    """
    Calcula os principais indicadores
    técnicos utilizados pelo InvestIA PRO.

    Indicadores:

        - preço
        - MA21
        - MA200
        - RSI
        - volatilidade

    O retorno mantém as chaves esperadas
    pelo restante da aplicação.
    """

    # ======================================================
    # VALIDAÇÃO INICIAL
    # ======================================================

    if market is None:

        raise ValueError(
            "Dados de mercado não fornecidos."
        )

    # ======================================================
    # COMPATIBILIDADE
    # ======================================================
    #
    # O módulo espera um dicionário contendo
    # o histórico em:
    #
    #     market["history"]
    #
    # Mantemos essa estrutura para compatibilidade
    # com market.py e app.py.
    #

    if not isinstance(
        market,
        dict,
    ):

        raise ValueError(
            "Formato dos dados de mercado inválido. "
            "Esperado um dicionário."
        )

    history = market.get(
        "history"
    )

    if history is None:

        raise ValueError(
            "Histórico do mercado não encontrado."
        )

    # ======================================================
    # LIMPEZA DO HISTÓRICO
    # ======================================================

    history = _clean_history(
        history
    )

    if history is None:

        raise ValueError(
            "Histórico de preços inválido ou vazio."
        )

    # ======================================================
    # SÉRIE DE FECHAMENTO
    # ======================================================

    close = history["Close"]

    if close is None:

        raise ValueError(
            "Coluna de fechamento não encontrada."
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
            "o preço atual."
        )

    # ======================================================
    # MA21
    # ======================================================

    ma21 = _calculate_moving_average(
        close,
        21,
    )

    # ======================================================
    # MA200
    # ======================================================

    ma200 = _calculate_moving_average(
        close,
        200,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi = _calculate_rsi(
        close,
        14,
    )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    volatility = _calculate_volatility(
        close
    )

    # ======================================================
    # DADOS DE IDENTIFICAÇÃO
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
    # RETORNO
    # ======================================================

    return {

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


# ==========================================================
# VALIDAÇÃO DOS INDICADORES
# ==========================================================

def validate_indicators(
    indicators,
):
    """
    Verifica se os indicadores principais
    possuem valores numéricos válidos.

    MA21 e MA200 podem ser None caso
    o histórico seja insuficiente.
    """

    if not isinstance(
        indicators,
        dict,
    ):
        return False

    required = [
        "price",
        "rsi",
        "volatility",
    ]

    for field in required:

        value = indicators.get(
            field
        )

        if _safe_float(
            value
        ) is None:

            return False

    return True


# ==========================================================
# STATUS DOS INDICADORES
# ==========================================================

def get_indicator_status(
    indicators,
):
    """
    Retorna um resumo da disponibilidade
    dos indicadores técnicos.

    Útil para o Dashboard e para futuras
    fases de monitoramento.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return {

            "valid": False,

            "price": False,

            "ma21": False,

            "ma200": False,

            "rsi": False,

            "volatility": False,

        }

    return {

        "valid":
            validate_indicators(
                indicators
            ),

        "price":
            _safe_float(
                indicators.get(
                    "price"
                )
            )
            is not None,

        "ma21":
            _safe_float(
                indicators.get(
                    "ma21"
                )
            )
            is not None,

        "ma200":
            _safe_float(
                indicators.get(
                    "ma200"
                )
            )
            is not None,

        "rsi":
            _safe_float(
                indicators.get(
                    "rsi"
                )
            )
            is not None,

        "volatility":
            _safe_float(
                indicators.get(
                    "volatility"
                )
            )
            is not None,

    }
