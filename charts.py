"""
InvestIA PRO
Módulo de Gráficos

Versão: v0.6
Fase: 2.9.7 - Gráficos Robustos
"""

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MA21_PERIOD = 21
MA200_PERIOD = 200


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def get_history(history):
    """
    Valida e retorna uma cópia do histórico.
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

    return history.copy()


def normalize_chart_columns(history):
    """
    Normaliza as colunas utilizadas nos gráficos.

    Trata retornos com MultiIndex e diferenças
    na nomenclatura das colunas.
    """

    if history is None:
        return None

    data = history.copy()

    # ======================================================
    # MULTIINDEX
    # ======================================================

    if isinstance(
        data.columns,
        pd.MultiIndex,
    ):

        try:

            data.columns = [
                (
                    str(column[0])
                    if isinstance(
                        column,
                        tuple,
                    )
                    else str(column)
                )
                for column in data.columns
            ]

        except Exception:

            return None

    # ======================================================
    # NORMALIZAÇÃO DOS NOMES
    # ======================================================

    rename_map = {}

    for column in data.columns:

        column_name = str(
            column
        ).strip()

        normalized = (
            column_name
            .lower()
            .replace(
                "_",
                " ",
            )
        )

        if normalized == "close":

            rename_map[column] = "Close"

        elif normalized == "adj close":

            rename_map[column] = "Adj Close"

        elif normalized == "open":

            rename_map[column] = "Open"

        elif normalized == "high":

            rename_map[column] = "High"

        elif normalized == "low":

            rename_map[column] = "Low"

        elif normalized == "volume":

            rename_map[column] = "Volume"

    if rename_map:

        data = data.rename(
            columns=rename_map
        )

    return data


def get_close_series(history):
    """
    Retorna a série de preços de fechamento.
    """

    if history is None:
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

        return close

    except Exception:

        return None


def prepare_chart_history(history):
    """
    Prepara o histórico para utilização
    nos gráficos.
    """

    data = get_history(
        history
    )

    if data is None:
        return None

    data = normalize_chart_columns(
        data
    )

    if data is None:
        return None

    if "Close" not in data.columns:
        return None

    try:

        data["Close"] = pd.to_numeric(
            data["Close"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["Close"]
        )

        data = data.sort_index()

        data = data[
            ~data.index.duplicated(
                keep="last"
            )
        ]

    except Exception:

        return None

    if data.empty:
        return None

    return data


# ==========================================================
# MÉDIAS MÓVEIS PARA GRÁFICOS
# ==========================================================

def add_moving_averages(history):
    """
    Adiciona MA21 e MA200 ao DataFrame
    utilizado para os gráficos.
    """

    data = prepare_chart_history(
        history
    )

    if data is None:
        return None

    try:

        data["MA21"] = (
            data["Close"]
            .rolling(
                window=MA21_PERIOD,
                min_periods=1,
            )
            .mean()
        )

        data["MA200"] = (
            data["Close"]
            .rolling(
                window=MA200_PERIOD,
                min_periods=1,
            )
            .mean()
        )

    except Exception:

        return data

    return data


# ==========================================================
# GRÁFICO PRINCIPAL
# ==========================================================

def create_price_chart(
    history,
):
    """
    Cria o gráfico principal de evolução
    do preço com MA21 e MA200.

    Retorna um objeto Plotly Figure ou None.
    """

    data = add_moving_averages(
        history
    )

    if data is None:
        return None

    if data.empty:
        return None

    try:

        fig = go.Figure()

        # ==================================================
        # PREÇO
        # ==================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name="Preço",
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}"
                    "<br>Preço: R$ %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

        # ==================================================
        # MA21
        # ==================================================

        if "MA21" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA21"],
                    mode="lines",
                    name="MA21",
                    hovertemplate=(
                        "Data: %{x|%d/%m/%Y}"
                        "<br>MA21: R$ %{y:,.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        # ==================================================
        # MA200
        # ==================================================

        if "MA200" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA200"],
                    mode="lines",
                    name="MA200",
                    hovertemplate=(
                        "Data: %{x|%d/%m/%Y}"
                        "<br>MA200: R$ %{y:,.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        # ==================================================
        # LAYOUT
        # ==================================================

        fig.update_layout(
            title="Evolução do preço",
            xaxis_title="Data",
            yaxis_title="Preço (R$)",
            hovermode="x unified",
            template="plotly_white",
            height=500,
            margin={
                "l": 20,
                "r": 20,
                "t": 60,
                "b": 20,
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )

        fig.update_xaxes(
            showgrid=True,
        )

        fig.update_yaxes(
            tickprefix="R$ ",
            separatethousands=True,
            showgrid=True,
        )

        return fig

    except Exception:

        return None


# ==========================================================
# GRÁFICO SIMPLES DE PREÇO
# ==========================================================

def create_simple_price_chart(
    history,
):
    """
    Cria um gráfico simples contendo
    apenas a evolução do preço.
    """

    data = prepare_chart_history(
        history
    )

    if data is None:
        return None

    try:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name="Preço",
            )
        )

        fig.update_layout(
            title="Evolução do preço",
            xaxis_title="Data",
            yaxis_title="Preço (R$)",
            template="plotly_white",
            height=400,
        )

        return fig

    except Exception:

        return None


# ==========================================================
# GRÁFICO DE VOLUME
# ==========================================================

def create_volume_chart(
    history,
):
    """
    Cria o gráfico de volume negociado.
    """

    data = prepare_chart_history(
        history
    )

    if data is None:
        return None

    if "Volume" not in data.columns:
        return None

    try:

        volume = pd.to_numeric(
            data["Volume"],
            errors="coerce",
        ).fillna(0)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=volume,
                name="Volume",
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}"
                    "<br>Volume: %{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            title="Volume negociado",
            xaxis_title="Data",
            yaxis_title="Volume",
            template="plotly_white",
            height=300,
            margin={
                "l": 20,
                "r": 20,
                "t": 60,
                "b": 20,
            },
        )

        return fig

    except Exception:

        return None


# ==========================================================
# RSI
# ==========================================================

def calculate_rsi_series(
    close,
    period=14,
):
    """
    Calcula a série completa do RSI
    para utilização em gráfico.
    """

    if close is None:
        return None

    try:

        if len(close) < period + 1:
            return None

        delta = close.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = (
            gain
            .rolling(
                window=period,
                min_periods=period,
            )
            .mean()
        )

        avg_loss = (
            loss
            .rolling(
                window=period,
                min_periods=period,
            )
            .mean()
        )

        rs = avg_gain / avg_loss.replace(
            0,
            float("nan"),
        )

        rsi = (
            100
            - (
                100
                / (
                    1
                    + rs
                )
            )
        )

        return rsi

    except Exception:

        return None


# ==========================================================
# GRÁFICO DO RSI
# ==========================================================

def create_rsi_chart(
    history,
):
    """
    Cria o gráfico do RSI.
    """

    data = prepare_chart_history(
        history
    )

    if data is None:
        return None

    close = get_close_series(
        data
    )

    if close is None:
        return None

    rsi = calculate_rsi_series(
        close
    )

    if rsi is None:
        return None

    try:

        fig = go.Figure()

        # RSI

        fig.add_trace(
            go.Scatter(
                x=rsi.index,
                y=rsi,
                mode="lines",
                name="RSI",
            )
        )

        # Sobrecompra

        fig.add_hline(
            y=70,
            line_dash="dash",
            annotation_text="Sobrecompra",
            annotation_position="top left",
        )

        # Neutro

        fig.add_hline(
            y=50,
            line_dash="dot",
        )

        # Sobrevenda

        fig.add_hline(
            y=30,
            line_dash="dash",
            annotation_text="Sobrevenda",
            annotation_position="bottom left",
        )

        fig.update_layout(
            title="Índice de Força Relativa (RSI)",
            xaxis_title="Data",
            yaxis_title="RSI",
            template="plotly_white",
            height=300,
            yaxis={
                "range": [0, 100],
            },
            margin={
                "l": 20,
                "r": 20,
                "t": 60,
                "b": 20,
            },
        )

        return fig

    except Exception:

        return None


# ==========================================================
# GRÁFICO DE PERFORMANCE
# ==========================================================

def create_performance_chart(
    history,
):
    """
    Cria gráfico de performance percentual
    acumulada desde o início do período.
    """

    data = prepare_chart_history(
        history
    )

    if data is None:
        return None

    close = get_close_series(
        data
    )

    if close is None:
        return None

    try:

        initial_price = close.iloc[0]

        if initial_price == 0:
            return None

        performance = (
            (
                close
                / initial_price
            )
            - 1
        ) * 100

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=performance.index,
                y=performance,
                mode="lines",
                name="Performance",
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}"
                    "<br>Performance: %{y:.2f}%"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_hline(
            y=0,
            line_dash="dot",
        )

        fig.update_layout(
            title="Performance no período",
            xaxis_title="Data",
            yaxis_title="Retorno (%)",
            template="plotly_white",
            height=400,
            margin={
                "l": 20,
                "r": 20,
                "t": 60,
                "b": 20,
            },
        )

        fig.update_yaxes(
            ticksuffix="%",
        )

        return fig

    except Exception:

        return None
