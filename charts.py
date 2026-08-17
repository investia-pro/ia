"""
InvestIA PRO
Gráficos

Versão: v0.6
Fase: 2.8.4 - Consolidação do Dashboard Executivo
"""

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# PREPARAÇÃO DO HISTÓRICO
# ==========================================================

def _prepare_history(history):
    """
    Prepara o histórico para utilização nos gráficos.

    Aceita:
        - pandas.DataFrame
        - dicionário contendo histórico
    """

    if history is None:
        return None

    # ------------------------------------------------------
    # DataFrame
    # ------------------------------------------------------

    if isinstance(
        history,
        pd.DataFrame,
    ):

        df = history.copy()

    # ------------------------------------------------------
    # Dicionário
    # ------------------------------------------------------

    elif isinstance(
        history,
        dict,
    ):

        try:

            df = pd.DataFrame(
                history
            )

        except Exception:

            return None

    else:

        return None

    # ------------------------------------------------------
    # Verificação
    # ------------------------------------------------------

    if df.empty:

        return None

    # ------------------------------------------------------
    # Índice
    # ------------------------------------------------------

    try:

        if not isinstance(
            df.index,
            pd.DatetimeIndex,
        ):

            df.index = pd.to_datetime(
                df.index,
                errors="coerce",
            )

    except Exception:

        pass

    # ------------------------------------------------------
    # Remover datas inválidas
    # ------------------------------------------------------

    if isinstance(
        df.index,
        pd.DatetimeIndex,
    ):

        df = df[
            ~df.index.isna()
        ]

    # ------------------------------------------------------
    # Ordenação
    # ------------------------------------------------------

    try:

        df = df.sort_index()

    except Exception:

        pass

    return df


# ==========================================================
# LOCALIZAÇÃO DE COLUNAS
# ==========================================================

def _find_column(
    dataframe,
    names,
):
    """
    Localiza uma coluna utilizando possíveis
    nomes alternativos.
    """

    if dataframe is None:

        return None

    columns = list(
        dataframe.columns
    )

    # ------------------------------------------------------
    # Correspondência exata
    # ------------------------------------------------------

    for name in names:

        if name in columns:

            return name

    # ------------------------------------------------------
    # Correspondência case insensitive
    # ------------------------------------------------------

    normalized = {
        str(column).lower(): column
        for column in columns
    }

    for name in names:

        key = str(
            name
        ).lower()

        if key in normalized:

            return normalized[key]

    return None


# ==========================================================
# GRÁFICO DE PREÇO
# ==========================================================

def create_price_chart(
    history,
):
    """
    Cria o gráfico principal de evolução do preço.

    O gráfico utiliza o fechamento do ativo.

    Retorno:
        plotly.graph_objects.Figure
        ou None quando não houver dados válidos.
    """

    # ======================================================
    # PREPARAÇÃO
    # ======================================================

    df = _prepare_history(
        history
    )

    if df is None:

        return None

    # ======================================================
    # COLUNA DE FECHAMENTO
    # ======================================================

    close_column = _find_column(
        df,
        [
            "Close",
            "close",
            "Adj Close",
            "adj close",
            "Preço",
            "price",
        ],
    )

    if close_column is None:

        return None

    # ======================================================
    # CONVERSÃO NUMÉRICA
    # ======================================================

    try:

        prices = pd.to_numeric(
            df[close_column],
            errors="coerce",
        )

    except Exception:

        return None

    valid = prices.notna()

    if not valid.any():

        return None

    prices = prices[
        valid
    ]

    # ======================================================
    # DATAS
    # ======================================================

    dates = prices.index

    if len(dates) == 0:

        return None

    # ======================================================
    # FIGURA
    # ======================================================

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode="lines",
            name="Preço",
            line={
                "width": 2,
            },
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>Preço: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(

        title={
            "text": "Evolução do preço",
            "x": 0.01,
        },

        xaxis_title="Data",

        yaxis_title="Preço (R$)",

        hovermode="x unified",

        template="plotly_white",

        height=450,

        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },

        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },

    )

    # ======================================================
    # EIXO X
    # ======================================================

    fig.update_xaxes(
        showgrid=True,
        rangeslider_visible=False,
    )

    # ======================================================
    # EIXO Y
    # ======================================================

    fig.update_yaxes(
        showgrid=True,
        tickprefix="R$ ",
        tickformat=",.2f",
    )

    return fig


# ==========================================================
# GRÁFICO COM MÉDIAS MÓVEIS
# ==========================================================

def create_price_ma_chart(
    history,
):
    """
    Cria gráfico de preço com MA21 e MA200.

    Função preparada para utilização nas
    próximas evoluções do Dashboard.
    """

    df = _prepare_history(
        history
    )

    if df is None:

        return None

    close_column = _find_column(
        df,
        [
            "Close",
            "close",
            "Adj Close",
            "adj close",
        ],
    )

    if close_column is None:

        return None

    try:

        df["__close__"] = pd.to_numeric(
            df[close_column],
            errors="coerce",
        )

    except Exception:

        return None

    df = df[
        df["__close__"].notna()
    ]

    if df.empty:

        return None

    # ======================================================
    # MÉDIAS
    # ======================================================

    df["__ma21__"] = (
        df["__close__"]
        .rolling(
            window=21,
            min_periods=1,
        )
        .mean()
    )

    df["__ma200__"] = (
        df["__close__"]
        .rolling(
            window=200,
            min_periods=1,
        )
        .mean()
    )

    # ======================================================
    # FIGURA
    # ======================================================

    fig = go.Figure()

    # ------------------------------------------------------
    # PREÇO
    # ------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["__close__"],
            mode="lines",
            name="Preço",
            line={
                "width": 2,
            },
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>Preço: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["__ma21__"],
            mode="lines",
            name="MA21",
            line={
                "width": 1.5,
                "dash": "dot",
            },
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>MA21: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["__ma200__"],
            mode="lines",
            name="MA200",
            line={
                "width": 1.5,
            },
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>MA200: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(

        title={
            "text": "Preço x Médias Móveis",
            "x": 0.01,
        },

        xaxis_title="Data",

        yaxis_title="Preço (R$)",

        hovermode="x unified",

        template="plotly_white",

        height=450,

        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },

        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },

    )

    fig.update_xaxes(
        showgrid=True,
        rangeslider_visible=False,
    )

    fig.update_yaxes(
        showgrid=True,
        tickprefix="R$ ",
        tickformat=",.2f",
    )

    return fig


# ==========================================================
# GRÁFICO DE VOLUME
# ==========================================================

def create_volume_chart(
    history,
):
    """
    Cria gráfico de volume negociado.

    Retorna None caso o histórico não contenha
    volume válido.
    """

    df = _prepare_history(
        history
    )

    if df is None:

        return None

    volume_column = _find_column(
        df,
        [
            "Volume",
            "volume",
        ],
    )

    if volume_column is None:

        return None

    try:

        volume = pd.to_numeric(
            df[volume_column],
            errors="coerce",
        )

    except Exception:

        return None

    valid = volume.notna()

    if not valid.any():

        return None

    volume = volume[
        valid
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=volume.index,
            y=volume,
            name="Volume",
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>Volume: %{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(

        title={
            "text": "Volume negociado",
            "x": 0.01,
        },

        xaxis_title="Data",

        yaxis_title="Volume",

        template="plotly_white",

        height=350,

        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },

    )

    fig.update_xaxes(
        showgrid=True,
    )

    fig.update_yaxes(
        showgrid=True,
    )

    return fig


# ==========================================================
# GRÁFICO PRINCIPAL DO DASHBOARD
# ==========================================================

def create_dashboard_chart(
    history,
):
    """
    Alias do gráfico principal.

    Mantém compatibilidade para futuras versões
    do app.py.
    """

    return create_price_chart(
        history
    )


# ==========================================================
# VALIDAÇÃO DO GRÁFICO
# ==========================================================

def validate_chart_data(
    history,
):
    """
    Verifica se existe histórico utilizável
    para geração dos gráficos.
    """

    df = _prepare_history(
        history
    )

    if df is None:

        return False

    close_column = _find_column(
        df,
        [
            "Close",
            "close",
            "Adj Close",
            "adj close",
        ],
    )

    if close_column is None:

        return False

    try:

        close = pd.to_numeric(
            df[close_column],
            errors="coerce",
        )

    except Exception:

        return False

    return close.notna().any()
