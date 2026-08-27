"""
InvestIA PRO
Charts Module

Version: v3.1.3
Final Phase: 3.1.3

Responsibilities:
- Price chart with moving averages
- Volume chart
- RSI chart
- Score comparison chart
- Technical overview
- Fundamental overview
- Safe rendering helpers for Streamlit

Compatible with:
- market.py Phase 3.0.7
- indicators.py Phase 3.0.7
- score.py Phase 3.0.7
- analysis.py Phase 3.0.7
- app.py Phase 3.0.7
"""

import math

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# AUXILIARY FUNCTIONS
# ==========================================================

def safe_float(value, default=None):
    """
    Converts a value to float safely.
    """

    if value is None:
        return default

    try:
        value = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(value):
        return default

    return value


def safe_series(data, column):
    """
    Returns a column as a valid Pandas Series.
    """

    if not isinstance(data, pd.DataFrame):
        return pd.Series(dtype="float64")

    if column not in data.columns:
        return pd.Series(dtype="float64")

    series = pd.to_numeric(
        data[column],
        errors="coerce",
    )

    return series.dropna()


def get_history(data):
    """
    Extracts the price history from several supported structures.

    Supported:

    DataFrame

    {
        "history": DataFrame
    }

    {
        "data": DataFrame
    }
    """

    if isinstance(data, pd.DataFrame):
        return data.copy()

    if isinstance(data, dict):

        history = data.get("history")

        if isinstance(history, pd.DataFrame):
            return history.copy()

        history = data.get("data")

        if isinstance(history, pd.DataFrame):
            return history.copy()

    return pd.DataFrame()


def get_close_column(history):
    """
    Finds the most appropriate close-price column.
    """

    if not isinstance(history, pd.DataFrame):
        return None

    possible_columns = [
        "Close",
        "Adj Close",
        "close",
        "adj_close",
    ]

    for column in possible_columns:

        if column in history.columns:
            return column

    return None


def get_volume_column(history):
    """
    Finds the volume column.
    """

    if not isinstance(history, pd.DataFrame):
        return None

    possible_columns = [
        "Volume",
        "volume",
    ]

    for column in possible_columns:

        if column in history.columns:
            return column

    return None


def get_ma_column(history, period):
    """
    Finds an existing moving-average column.
    """

    if not isinstance(history, pd.DataFrame):
        return None

    possible_columns = [

        f"MA{period}",
        f"ma{period}",

        f"SMA{period}",
        f"sma{period}",

        f"ma_{period}",
        f"sma_{period}",

        f"MA_{period}",
        f"SMA_{period}",
    ]

    for column in possible_columns:

        if column in history.columns:
            return column

    return None


def prepare_history(data):
    """
    Standardizes the historical DataFrame.

    Adds calculated moving averages when necessary.
    """

    history = get_history(data)

    if history.empty:
        return pd.DataFrame()

    history = history.copy()

    if not isinstance(
        history.index,
        pd.DatetimeIndex,
    ):

        try:

            history.index = pd.to_datetime(
                history.index,
                errors="coerce",
            )

        except Exception:
            pass

    close_column = get_close_column(history)

    if close_column is None:
        return pd.DataFrame()

    history["__close__"] = pd.to_numeric(
        history[close_column],
        errors="coerce",
    )

    history = history.dropna(
        subset=["__close__"]
    )

    if history.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    ma21_column = get_ma_column(
        history,
        21,
    )

    if ma21_column is not None:

        history["__ma21__"] = pd.to_numeric(
            history[ma21_column],
            errors="coerce",
        )

    else:

        history["__ma21__"] = (
            history["__close__"]
            .rolling(
                window=21,
                min_periods=1,
            )
            .mean()
        )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    ma200_column = get_ma_column(
        history,
        200,
    )

    if ma200_column is not None:

        history["__ma200__"] = pd.to_numeric(
            history[ma200_column],
            errors="coerce",
        )

    else:

        history["__ma200__"] = (
            history["__close__"]
            .rolling(
                window=200,
                min_periods=1,
            )
            .mean()
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    rsi_column = None

    for column in [
        "RSI",
        "rsi",
        "RSI14",
        "rsi14",
        "RSI_14",
        "rsi_14",
    ]:

        if column in history.columns:

            rsi_column = column
            break

    if rsi_column is not None:

        history["__rsi__"] = pd.to_numeric(
            history[rsi_column],
            errors="coerce",
        )

    else:

        history["__rsi__"] = calculate_rsi(
            history["__close__"]
        )

    return history


# ==========================================================
# RSI CALCULATION
# ==========================================================

def calculate_rsi(
    series,
    period=14,
):
    """
    Calculates the Relative Strength Index.
    """

    if not isinstance(
        series,
        pd.Series,
    ):

        return pd.Series(
            dtype="float64"
        )

    series = pd.to_numeric(
        series,
        errors="coerce",
    )

    delta = series.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    average_gain = gain.rolling(
        window=period,
        min_periods=period,
    ).mean()

    average_loss = loss.rolling(
        window=period,
        min_periods=period,
    ).mean()

    rs = average_gain / average_loss.replace(
        0,
        pd.NA,
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


# ==========================================================
# EMPTY FIGURE
# ==========================================================

def create_empty_figure(
    message="Dados não disponíveis.",
    height=400,
):
    """
    Creates a standard empty chart.
    """

    figure = go.Figure()

    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={
            "size": 16,
        },
    )

    figure.update_layout(
        height=height,
        template="plotly_white",
        margin={
            "l": 30,
            "r": 30,
            "t": 40,
            "b": 30,
        },
    )

    return figure


# ==========================================================
# PRICE CHART
# ==========================================================

def create_price_chart(
    data,
    asset=None,
    show_ma21=True,
    show_ma200=True,
):
    """
    Creates the main price chart.
    """

    history = prepare_history(
        data
    )

    if history.empty:

        return create_empty_figure(
            "Histórico de preços não disponível."
        )

    figure = go.Figure()

    # ------------------------------------------------------
    # PRICE
    # ------------------------------------------------------

    figure.add_trace(
        go.Scatter(
            x=history.index,
            y=history["__close__"],
            mode="lines",
            name="Preço",
            line={
                "width": 2,
            },
            hovertemplate=(
                "<b>Data:</b> %{x|%d/%m/%Y}"
                "<br>"
                "<b>Preço:</b> R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if (
        show_ma21
        and "__ma21__" in history.columns
    ):

        figure.add_trace(
            go.Scatter(
                x=history.index,
                y=history["__ma21__"],
                mode="lines",
                name="MA21",
                line={
                    "width": 1.5,
                    "dash": "dash",
                },
                hovertemplate=(
                    "<b>MA21:</b> R$ %{y:.2f}"
                    "<extra></extra>"
                ),
            )
        )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    if (
        show_ma200
        and "__ma200__" in history.columns
    ):

        figure.add_trace(
            go.Scatter(
                x=history.index,
                y=history["__ma200__"],
                mode="lines",
                name="MA200",
                line={
                    "width": 1.5,
                    "dash": "dot",
                },
                hovertemplate=(
                    "<b>MA200:</b> R$ %{y:.2f}"
                    "<extra></extra>"
                ),
            )
        )

    title = "Evolução do Preço"

    if asset:
        title = f"Evolução do Preço — {asset}"

    figure.update_layout(
        title=title,
        template="plotly_white",
        height=450,
        hovermode="x unified",
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
            "xanchor": "right",
            "x": 1,
        },
    )

    figure.update_xaxes(
        title=None,
        showgrid=True,
    )

    figure.update_yaxes(
        title="Preço (R$)",
        tickprefix="R$ ",
        showgrid=True,
    )

    return figure


# ==========================================================
# VOLUME CHART
# ==========================================================

def create_volume_chart(
    data,
    asset=None,
):
    """
    Creates the trading-volume chart.
    """

    history = get_history(
        data
    )

    if history.empty:

        return create_empty_figure(
            "Dados de volume não disponíveis.",
            height=300,
        )

    volume_column = get_volume_column(
        history
    )

    if volume_column is None:

        return create_empty_figure(
            "O ativo não possui dados de volume disponíveis.",
            height=300,
        )

    volume = pd.to_numeric(
        history[volume_column],
        errors="coerce",
    )

    valid_data = pd.DataFrame(
        {
            "volume": volume,
        },
        index=history.index,
    ).dropna()

    if valid_data.empty:

        return create_empty_figure(
            "Dados de volume inválidos.",
            height=300,
        )

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=valid_data.index,
            y=valid_data["volume"],
            name="Volume",
            hovertemplate=(
                "<b>Data:</b> %{x|%d/%m/%Y}"
                "<br>"
                "<b>Volume:</b> %{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    title = "Volume Negociado"

    if asset:
        title = f"Volume Negociado — {asset}"

    figure.update_layout(
        title=title,
        template="plotly_white",
        height=300,
        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },
        showlegend=False,
    )

    figure.update_yaxes(
        title="Volume"
    )

    return figure


# ==========================================================
# RSI CHART
# ==========================================================

def create_rsi_chart(
    data,
    asset=None,
):
    """
    Creates the RSI chart.
    """

    history = prepare_history(
        data
    )

    if history.empty:

        return create_empty_figure(
            "Dados insuficientes para calcular o RSI.",
            height=300,
        )

    if "__rsi__" not in history.columns:

        return create_empty_figure(
            "RSI não disponível.",
            height=300,
        )

    rsi = pd.to_numeric(
        history["__rsi__"],
        errors="coerce",
    )

    valid_data = pd.DataFrame(
        {
            "rsi": rsi,
        },
        index=history.index,
    ).dropna()

    if valid_data.empty:

        return create_empty_figure(
            "Dados insuficientes para calcular o RSI.",
            height=300,
        )

    figure = go.Figure()

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    figure.add_trace(
        go.Scatter(
            x=valid_data.index,
            y=valid_data["rsi"],
            mode="lines",
            name="RSI",
            line={
                "width": 2,
            },
            hovertemplate=(
                "<b>Data:</b> %{x|%d/%m/%Y}"
                "<br>"
                "<b>RSI:</b> %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ------------------------------------------------------
    # OVERBOUGHT
    # ------------------------------------------------------

    figure.add_hline(
        y=70,
        line_dash="dash",
        annotation_text="Sobrecompra",
        annotation_position="top right",
    )

    # ------------------------------------------------------
    # OVERSOLD
    # ------------------------------------------------------

    figure.add_hline(
        y=30,
        line_dash="dash",
        annotation_text="Sobrevenda",
        annotation_position="bottom right",
    )

    # ------------------------------------------------------
    # NEUTRAL
    # ------------------------------------------------------

    figure.add_hline(
        y=50,
        line_dash="dot",
    )

    title = "RSI — Índice de Força Relativa"

    if asset:
        title = f"RSI — {asset}"

    figure.update_layout(
        title=title,
        template="plotly_white",
        height=320,
        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },
        showlegend=False,
    )

    figure.update_yaxes(
        title="RSI",
        range=[
            0,
            100,
        ],
    )

    return figure


# ==========================================================
# SCORE COMPARISON
# ==========================================================

def create_score_chart(
    analysis,
):
    """
    Creates a comparison chart for the three InvestIA scores.
    """

    if not isinstance(
        analysis,
        dict,
    ):

        return create_empty_figure(
            "Dados de Score não disponíveis.",
            height=350,
        )

    technical_score = safe_float(
        analysis.get(
            "technical_score"
        ),
        0,
    )

    fundamental_score = safe_float(
        analysis.get(
            "fundamental_score"
        ),
        0,
    )

    integrated_score = safe_float(
        analysis.get(
            "integrated_score",
            analysis.get(
                "score"
            ),
        ),
        0,
    )

    labels = [
        "Técnico",
        "Fundamentalista",
        "Integrado",
    ]

    values = [
        technical_score,
        fundamental_score,
        integrated_score,
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=labels,
            y=values,
            text=[
                f"{value:.0f}"
                for value in values
            ],
            textposition="auto",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Score: %{y:.2f}/100"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Comparação dos Scores InvestIA",
        template="plotly_white",
        height=380,
        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },
        showlegend=False,
    )

    figure.update_yaxes(
        title="Score",
        range=[
            0,
            100,
        ],
    )

    return figure


# ==========================================================
# TECHNICAL OVERVIEW
# ==========================================================

def create_technical_overview_chart(
    indicators,
):
    """
    Creates a radar chart for the main technical indicators.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return create_empty_figure(
            "Indicadores técnicos não disponíveis.",
            height=400,
        )

    # ------------------------------------------------------
    # RSI SCORE
    # ------------------------------------------------------

    rsi = safe_float(
        indicators.get(
            "rsi"
        )
    )

    if rsi is None:

        rsi_score = 50

    elif 45 <= rsi <= 65:

        rsi_score = 85

    elif 35 <= rsi <= 70:

        rsi_score = 65

    elif rsi < 30:

        rsi_score = 55

    else:

        rsi_score = 40

    # ------------------------------------------------------
    # PRICE VS MA21
    # ------------------------------------------------------

    distance_ma21 = safe_float(
        indicators.get(
            "distance_ma21"
        )
    )

    if distance_ma21 is None:

        ma21_score = 50

    else:

        distance_percent = (
            distance_ma21 * 100
            if abs(distance_ma21) <= 1
            else distance_ma21
        )

        ma21_score = max(
            0,
            min(
                100,
                50 + distance_percent * 5,
            ),
        )

    # ------------------------------------------------------
    # PRICE VS MA200
    # ------------------------------------------------------

    distance_ma200 = safe_float(
        indicators.get(
            "distance_ma200"
        )
    )

    if distance_ma200 is None:

        ma200_score = 50

    else:

        distance_percent = (
            distance_ma200 * 100
            if abs(distance_ma200) <= 1
            else distance_ma200
        )

        ma200_score = max(
            0,
            min(
                100,
                50 + distance_percent * 3,
            ),
        )

    # ------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------

    relative_volume = safe_float(
        indicators.get(
            "relative_volume"
        )
    )

    if relative_volume is None:

        volume_score = 50

    elif relative_volume >= 1.5:

        volume_score = 85

    elif relative_volume >= 1:

        volume_score = 70

    elif relative_volume >= 0.7:

        volume_score = 50

    else:

        volume_score = 35

    # ------------------------------------------------------
    # RANGE POSITION
    # ------------------------------------------------------

    range_position = safe_float(
        indicators.get(
            "range_position"
        )
    )

    if range_position is None:

        range_score = 50

    else:

        if 0 <= range_position <= 1:
            range_score = range_position * 100
        else:
            range_score = max(
                0,
                min(
                    100,
                    range_position,
                ),
            )

    labels = [
        "RSI",
        "MA21",
        "MA200",
        "Volume",
        "Posição",
    ]

    values = [
        rsi_score,
        ma21_score,
        ma200_score,
        volume_score,
        range_score,
    ]

    labels_closed = (
        labels
        + [labels[0]]
    )

    values_closed = (
        values
        + [values[0]]
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            name="Técnico",
            hovertemplate=(
                "<b>%{theta}</b>"
                "<br>"
                "Score: %{r:.1f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Panorama Técnico",
        template="plotly_white",
        height=420,
        margin={
            "l": 50,
            "r": 50,
            "t": 60,
            "b": 40,
        },
        showlegend=False,
        polar={
            "radialaxis": {
                "visible": True,
                "range": [
                    0,
                    100,
                ],
            },
        },
    )

    return figure


# ==========================================================
# FUNDAMENTAL OVERVIEW
# ==========================================================

def create_fundamental_chart(
    fundamentals,
):
    """
    Creates a fundamental overview chart.

    The chart only includes numeric metrics
    available in the fundamental data.
    """

    if not isinstance(
        fundamentals,
        dict,
    ):

        return create_empty_figure(
            "Dados fundamentalistas não disponíveis.",
            height=400,
        )

    metrics = []

    metric_map = {

        "trailingPE": "P/L",

        "forwardPE": "P/L Futuro",

        "priceToBook": "P/VP",

        "returnOnEquity": "ROE",

        "profitMargins": "Margem",

        "operatingMargins": "Margem Operacional",

        "revenueGrowth": "Crescimento Receita",

        "earningsGrowth": "Crescimento Lucro",

        "debtToEbitda": "Dívida/EBITDA",

        "dividendYield": "Dividend Yield",
    }

    for key, label in metric_map.items():

        value = safe_float(
            fundamentals.get(
                key
            )
        )

        if value is None:
            continue

        # --------------------------------------------------
        # NORMALIZATION FOR VISUALIZATION
        # --------------------------------------------------

        if key in (
            "returnOnEquity",
            "profitMargins",
            "operatingMargins",
            "revenueGrowth",
            "earningsGrowth",
            "dividendYield",
        ):

            if abs(value) <= 1:
                normalized_value = value * 100
            else:
                normalized_value = value

        else:

            normalized_value = value

        metrics.append(
            (
                label,
                normalized_value,
            )
        )

    if not metrics:

        return create_empty_figure(
            "Não há indicadores fundamentalistas numéricos disponíveis.",
            height=400,
        )

    labels = [
        item[0]
        for item in metrics
    ]

    values = [
        item[1]
        for item in metrics
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=labels,
            y=values,
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Valor: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Indicadores Fundamentalistas",
        template="plotly_white",
        height=400,
        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 80,
        },
        showlegend=False,
    )

    return figure


# ==========================================================
# PRICE PERFORMANCE
# ==========================================================

def create_price_performance_chart(
    data,
    asset=None,
):
    """
    Creates a normalized price-performance chart.

    The first available price becomes the 100 base.
    """

    history = prepare_history(
        data
    )

    if history.empty:

        return create_empty_figure(
            "Histórico de desempenho não disponível.",
            height=350,
        )

    close = history[
        "__close__"
    ].dropna()

    if close.empty:

        return create_empty_figure(
            "Dados insuficientes para calcular desempenho.",
            height=350,
        )

    first_price = safe_float(
        close.iloc[0]
    )

    if (
        first_price is None
        or first_price == 0
    ):

        return create_empty_figure(
            "Não foi possível normalizar os preços.",
            height=350,
        )

    normalized = (
        close
        / first_price
        * 100
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized,
            mode="lines",
            name="Desempenho",
            line={
                "width": 2,
            },
            hovertemplate=(
                "<b>Data:</b> %{x|%d/%m/%Y}"
                "<br>"
                "<b>Índice:</b> %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.add_hline(
        y=100,
        line_dash="dash",
    )

    title = "Desempenho Acumulado"

    if asset:
        title = f"Desempenho Acumulado — {asset}"

    figure.update_layout(
        title=title,
        template="plotly_white",
        height=350,
        margin={
            "l": 40,
            "r": 30,
            "t": 60,
            "b": 40,
        },
        showlegend=False,
    )

    figure.update_yaxes(
        title="Base 100",
    )

    return figure


# ==========================================================
# DASHBOARD FIGURES
# ==========================================================

def create_dashboard_charts(
    prepared_data,
    indicators,
    analysis,
    asset=None,
):
    """
    Creates all main charts used by the dashboard.

    Returns a dictionary containing Plotly figures.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        indicators = {}

    if not isinstance(
        analysis,
        dict,
    ):

        analysis = {}

    fundamentals = analysis.get(
        "fundamentals",
        {}
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    return {

        "price": create_price_chart(
            data=prepared_data,
            asset=asset,
        ),

        "volume": create_volume_chart(
            data=prepared_data,
            asset=asset,
        ),

        "rsi": create_rsi_chart(
            data=prepared_data,
            asset=asset,
        ),

        "scores": create_score_chart(
            analysis=analysis,
        ),

        "technical": create_technical_overview_chart(
            indicators=indicators,
        ),

        "fundamentals": create_fundamental_chart(
            fundamentals=fundamentals,
        ),

        "performance": create_price_performance_chart(
            data=prepared_data,
            asset=asset,
        ),
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    import numpy as np

    print("=" * 60)
    print("InvestIA PRO")
    print("Charts.py")
    print("Phase 3.0.7")
    print("=" * 60)

    dates = pd.date_range(
        end=pd.Timestamp.today(),
        periods=250,
        freq="B",
    )

    prices = (
        30
        + np.cumsum(
            np.random.normal(
                0,
                0.8,
                len(dates),
            )
        )
    )

    history = pd.DataFrame(
        {
            "Close": prices,
            "Volume": np.random.randint(
                500000,
                5000000,
                len(dates),
            ),
        },
        index=dates,
    )

    test_indicators = {

        "rsi": 58.4,

        "distance_ma21": 0.03,

        "distance_ma200": 0.10,

        "relative_volume": 1.20,

        "range_position": 0.72,
    }

    test_analysis = {

        "technical_score": 68,

        "fundamental_score": 74,

        "integrated_score": 71,

        "fundamentals": {

            "trailingPE": 8.5,

            "priceToBook": 1.2,

            "returnOnEquity": 0.18,

            "profitMargins": 0.15,

            "revenueGrowth": 0.12,

            "debtToEbitda": 1.8,

            "dividendYield": 0.06,
        },
    }

    charts = create_dashboard_charts(
        prepared_data={
            "history": history
        },
        indicators=test_indicators,
        analysis=test_analysis,
        asset="TESTE.SA",
    )

    print()

    for chart_name in charts:

        print(
            f"✓ Chart generated: {chart_name}"
        )

    print()
    print("Charts module test completed successfully.")
