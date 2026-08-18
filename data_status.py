"""
InvestIA PRO
Status e Qualidade dos Dados

Versão: v0.6
Fase: 2.9.2 - Status Operacional da Análise
"""

from datetime import datetime

import pandas as pd


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _is_valid_dataframe(data):
    """
    Verifica se o objeto é um DataFrame válido
    e possui registros.
    """

    return (
        isinstance(data, pd.DataFrame)
        and not data.empty
    )


def _get_history(data):
    """
    Obtém o histórico a partir dos dados de mercado.
    """

    if not isinstance(data, dict):
        return None

    history = data.get("history")

    if not _is_valid_dataframe(history):
        return None

    return history


def _format_date(value):
    """
    Converte uma data para o formato brasileiro.
    """

    if value is None:
        return "N/A"

    try:

        timestamp = pd.Timestamp(value)

        return timestamp.strftime(
            "%d/%m/%Y"
        )

    except Exception:

        return "N/A"


# ==========================================================
# STATUS DO HISTÓRICO
# ==========================================================

def get_history_status(market_data):
    """
    Avalia a disponibilidade do histórico.

    Retorna informações sobre:
        - existência;
        - quantidade de registros;
        - primeira data;
        - última data.
    """

    history = _get_history(
        market_data
    )

    if history is None:

        return {

            "available": False,

            "rows": 0,

            "first_date": None,

            "last_date": None,

            "first_date_formatted": "N/A",

            "last_date_formatted": "N/A",

        }

    rows = len(history)

    first_date = None
    last_date = None

    try:

        first_date = history.index.min()
        last_date = history.index.max()

    except Exception:

        pass

    return {

        "available": True,

        "rows": rows,

        "first_date": first_date,

        "last_date": last_date,

        "first_date_formatted":
            _format_date(
                first_date
            ),

        "last_date_formatted":
            _format_date(
                last_date
            ),

    }


# ==========================================================
# STATUS DOS INDICADORES
# ==========================================================

def get_data_quality_status(
    market_data,
    indicators=None,
):
    """
    Avalia a qualidade geral dos dados
    utilizados pela análise.
    """

    history_status = get_history_status(
        market_data
    )

    # ------------------------------------------------------
    # INDICADORES ESPERADOS
    # ------------------------------------------------------

    required_indicators = [

        "price",

        "ma21",

        "ma200",

        "rsi",

        "volatility",

    ]

    available_indicators = []
    missing_indicators = []

    if isinstance(
        indicators,
        dict,
    ):

        for indicator in required_indicators:

            value = indicators.get(
                indicator
            )

            if value is None:

                missing_indicators.append(
                    indicator
                )

            else:

                try:

                    if pd.isna(value):

                        missing_indicators.append(
                            indicator
                        )

                    else:

                        available_indicators.append(
                            indicator
                        )

                except Exception:

                    missing_indicators.append(
                        indicator
                    )

    else:

        missing_indicators = (
            required_indicators.copy()
        )

    # ------------------------------------------------------
    # CLASSIFICAÇÃO
    # ------------------------------------------------------

    if not history_status["available"]:

        status = "INDISPONÍVEL"

        status_icon = "🔴"

        message = (
            "Não foi possível obter "
            "o histórico do ativo."
        )

    elif len(missing_indicators) == 0:

        status = "COMPLETO"

        status_icon = "🟢"

        message = (
            "Todos os dados necessários "
            "para a análise estão disponíveis."
        )

    else:

        status = "PARCIAL"

        status_icon = "🟡"

        message = (
            "Alguns indicadores não estão "
            "disponíveis para o período selecionado."
        )

    return {

        "status": status,

        "status_icon": status_icon,

        "message": message,

        "history_available":
            history_status["available"],

        "rows":
            history_status["rows"],

        "first_date":
            history_status["first_date_formatted"],

        "last_date":
            history_status["last_date_formatted"],

        "available_indicators":
            available_indicators,

        "missing_indicators":
            missing_indicators,

        "total_indicators":
            len(required_indicators),

        "available_count":
            len(available_indicators),

        "missing_count":
            len(missing_indicators),

    }


# ==========================================================
# STATUS OPERACIONAL
# ==========================================================

def get_operational_status(
    market_data,
    indicators=None,
):
    """
    Retorna o status operacional completo
    da análise.
    """

    quality = get_data_quality_status(
        market_data,
        indicators,
    )

    # ------------------------------------------------------
    # DADOS ATUALIZADOS
    # ------------------------------------------------------

    last_date = quality.get(
        "last_date"
    )

    data_available = (
        quality["history_available"]
    )

    # ------------------------------------------------------
    # STATUS PRINCIPAL
    # ------------------------------------------------------

    if not data_available:

        operational = "OFFLINE"

        operational_icon = "🔴"

    elif quality["status"] == "COMPLETO":

        operational = "ONLINE"

        operational_icon = "🟢"

    else:

        operational = "PARCIAL"

        operational_icon = "🟡"

    return {

        "operational":
            operational,

        "operational_icon":
            operational_icon,

        "quality":
            quality,

        "last_market_date":
            quality["last_date"],

        "last_market_date_formatted":
            quality["last_date"],

    }


# ==========================================================
# TEXTO DO STATUS
# ==========================================================

def get_status_message(
    market_data,
    indicators=None,
):
    """
    Gera uma mensagem pronta para
    apresentação no Dashboard.
    """

    status = get_operational_status(
        market_data,
        indicators,
    )

    quality = status["quality"]

    if status["operational"] == "OFFLINE":

        return (
            "🔴 **Dados indisponíveis:** "
            "não foi possível obter o histórico "
            "necessário para a análise."
        )

    if status["operational"] == "PARCIAL":

        missing = quality.get(
            "missing_indicators",
            [],
        )

        if missing:

            missing_text = ", ".join(
                missing
            )

            return (
                "🟡 **Dados parciais:** "
                "alguns indicadores não estão "
                f"disponíveis ({missing_text})."
            )

        return (
            "🟡 **Dados parciais:** "
            "a análise possui limitações "
            "de dados."
        )

    return (
        "🟢 **Dados disponíveis:** "
        "todos os indicadores necessários "
        "foram calculados com sucesso."
    )


# ==========================================================
# RESUMO OPERACIONAL
# ==========================================================

def get_operational_summary(
    market_data,
    indicators=None,
):
    """
    Retorna um resumo simples para o Dashboard.
    """

    status = get_operational_status(
        market_data,
        indicators,
    )

    quality = status["quality"]

    return {

        "status":
            status["operational"],

        "icon":
            status["operational_icon"],

        "message":
            get_status_message(
                market_data,
                indicators,
            ),

        "records":
            quality["rows"],

        "last_date":
            quality["last_date"],

        "available_indicators":
            quality["available_count"],

        "total_indicators":
            quality["total_indicators"],

    }
