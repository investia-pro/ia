"""
InvestIA PRO
Módulo de Gráficos

Versão: v0.7
Fase: 3.0.5 - Evolução Histórica de Preço e Score

Responsabilidades:
- Gráfico de evolução do preço
- Médias móveis MA21 e MA200
- Gráfico histórico do Score Técnico
- Zonas de Score
- Identificação de sinais
- Gráfico integrado de análise
"""

import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def validate_dataframe(
    data,
):
    """
    Valida se o objeto é um DataFrame
    válido e possui dados.
    """

    if not isinstance(
        data,
        pd.DataFrame,
    ):

        return False

    if data.empty:

        return False

    return True


def get_column(
    dataframe,
    possible_names,
):
    """
    Procura uma coluna utilizando
    diferentes nomes possíveis.
    """

    if not validate_dataframe(
        dataframe
    ):

        return None

    for column in possible_names:

        if column in dataframe.columns:

            return column

    return None


def safe_numeric_series(
    dataframe,
    column,
):
    """
    Retorna uma série numérica limpa.
    """

    if (
        not validate_dataframe(
            dataframe
        )
        or column is None
        or column not in dataframe.columns
    ):

        return None

    series = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    return series


# ==========================================================
# GRÁFICO PRINCIPAL DE PREÇO
# ==========================================================

def create_price_chart(
    history,
):
    """
    Cria o gráfico principal de evolução
    do preço.

    Compatível com o histórico retornado
    pelo market.py.
    """

    if not validate_dataframe(
        history
    ):

        return None

    price_column = get_column(
        history,
        [
            "Close",
            "close",
            "price",
            "Preço",
        ],
    )

    if price_column is None:

        return None

    price_series = safe_numeric_series(
        history,
        price_column,
    )

    if (
        price_series is None
        or price_series.dropna().empty
    ):

        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=price_series,
            mode="lines",
            name="Preço",
            line={
                "width": 2,
            },
        )
    )

    fig.update_layout(
        title="Evolução do Preço",
        xaxis_title="Data",
        yaxis_title="Preço",
        hovermode="x unified",
        template="plotly_white",
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20,
        },
        height=450,
    )

    return fig


# ==========================================================
# GRÁFICO DE PREÇO COM MÉDIAS
# ==========================================================

def create_price_indicators_chart(
    historical_indicators,
):
    """
    Cria gráfico com:

    - Preço
    - MA21
    - MA200
    """

    if not validate_dataframe(
        historical_indicators
    ):

        return None

    price_column = get_column(
        historical_indicators,
        [
            "price",
            "Close",
            "close",
        ],
    )

    ma21_column = get_column(
        historical_indicators,
        [
            "ma21",
            "MA21",
        ],
    )

    ma200_column = get_column(
        historical_indicators,
        [
            "ma200",
            "MA200",
        ],
    )

    if price_column is None:

        return None

    price_series = safe_numeric_series(
        historical_indicators,
        price_column,
    )

    if (
        price_series is None
        or price_series.dropna().empty
    ):

        return None

    fig = go.Figure()

    # ======================================================
    # PREÇO
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=historical_indicators.index,
            y=price_series,
            mode="lines",
            name="Preço",
            line={
                "width": 2,
            },
        )
    )

    # ======================================================
    # MA21
    # ======================================================

    if ma21_column is not None:

        ma21_series = safe_numeric_series(
            historical_indicators,
            ma21_column,
        )

        if (
            ma21_series is not None
            and not ma21_series.dropna().empty
        ):

            fig.add_trace(
                go.Scatter(
                    x=historical_indicators.index,
                    y=ma21_series,
                    mode="lines",
                    name="MA21",
                    line={
                        "width": 1.5,
                    },
                )
            )

    # ======================================================
    # MA200
    # ======================================================

    if ma200_column is not None:

        ma200_series = safe_numeric_series(
            historical_indicators,
            ma200_column,
        )

        if (
            ma200_series is not None
            and not ma200_series.dropna().empty
        ):

            fig.add_trace(
                go.Scatter(
                    x=historical_indicators.index,
                    y=ma200_series,
                    mode="lines",
                    name="MA200",
                    line={
                        "width": 1.5,
                    },
                )
            )

    fig.update_layout(
        title="Preço e Médias Móveis",
        xaxis_title="Data",
        yaxis_title="Preço",
        hovermode="x unified",
        template="plotly_white",
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20,
        },
        height=500,
    )

    return fig


# ==========================================================
# GRÁFICO HISTÓRICO DO SCORE
# ==========================================================

def create_score_history_chart(
    score_history,
):
    """
    Cria o gráfico de evolução
    do Score Técnico.

    Espera um DataFrame com:

    - technical_score
    - signal
    """

    if not validate_dataframe(
        score_history
    ):

        return None

    score_column = get_column(
        score_history,
        [
            "technical_score",
            "score",
        ],
    )

    if score_column is None:

        return None

    score_series = safe_numeric_series(
        score_history,
        score_column,
    )

    if (
        score_series is None
        or score_series.dropna().empty
    ):

        return None

    fig = go.Figure()

    # ======================================================
    # ZONAS DE SCORE
    # ======================================================

    fig.add_hrect(
        y0=80,
        y1=100,
        line_width=0,
        fillcolor="green",
        opacity=0.08,
        annotation_text="Forte",
        annotation_position="top left",
    )

    fig.add_hrect(
        y0=65,
        y1=80,
        line_width=0,
        fillcolor="lightgreen",
        opacity=0.08,
        annotation_text="Bom",
        annotation_position="top left",
    )

    fig.add_hrect(
        y0=50,
        y1=65,
        line_width=0,
        fillcolor="gold",
        opacity=0.08,
        annotation_text="Neutro",
        annotation_position="top left",
    )

    fig.add_hrect(
        y0=35,
        y1=50,
        line_width=0,
        fillcolor="orange",
        opacity=0.08,
        annotation_text="Fraco",
        annotation_position="top left",
    )

    fig.add_hrect(
        y0=0,
        y1=35,
        line_width=0,
        fillcolor="red",
        opacity=0.08,
        annotation_text="Muito fraco",
        annotation_position="top left",
    )

    # ======================================================
    # LINHA DO SCORE
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=score_history.index,
            y=score_series,
            mode="lines+markers",
            name="Score Técnico",
            line={
                "width": 2,
            },
            marker={
                "size": 4,
            },
        )
    )

    # ======================================================
    # LINHAS DE REFERÊNCIA
    # ======================================================

    fig.add_hline(
        y=80,
        line_dash="dash",
        annotation_text="FORTE",
    )

    fig.add_hline(
        y=65,
        line_dash="dash",
        annotation_text="BOM",
    )

    fig.add_hline(
        y=50,
        line_dash="dash",
        annotation_text="NEUTRO",
    )

    fig.add_hline(
        y=35,
        line_dash="dash",
        annotation_text="FRACO",
    )

    fig.update_layout(
        title="Evolução do Score Técnico",
        xaxis_title="Data",
        yaxis_title="Score",
        yaxis={
            "range": [
                0,
                100,
            ],
        },
        hovermode="x unified",
        template="plotly_white",
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20,
        },
        height=450,
    )

    return fig


# ==========================================================
# MARCADORES DE SINAL
# ==========================================================

def add_signal_markers(
    fig,
    score_history,
):
    """
    Adiciona marcadores de sinal
    no gráfico.

    Positivo
    Neutro
    Negativo
    """

    if fig is None:

        return fig

    if not validate_dataframe(
        score_history
    ):

        return fig

    if (
        "signal" not in score_history.columns
        or "technical_score"
        not in score_history.columns
    ):

        return fig

    signal_map = {

        "POSITIVO": {
            "symbol": "triangle-up",
            "name": "Sinal Positivo",
        },

        "NEGATIVO": {
            "symbol": "triangle-down",
            "name": "Sinal Negativo",
        },

        "NEUTRO": {
            "symbol": "circle",
            "name": "Sinal Neutro",
        },

    }

    for signal, settings in signal_map.items():

        filtered = score_history[
            score_history["signal"]
            .astype(str)
            .str.upper()
            == signal
        ]

        if filtered.empty:

            continue

        fig.add_trace(
            go.Scatter(
                x=filtered.index,
                y=filtered[
                    "technical_score"
                ],
                mode="markers",
                name=settings[
                    "name"
                ],
                marker={
                    "symbol":
                        settings["symbol"],

                    "size":
                        8,
                },
            )
        )

    return fig


# ==========================================================
# GRÁFICO COMPLETO DO SCORE
# ==========================================================

def create_score_evolution_chart(
    score_history,
):
    """
    Cria o gráfico completo
    da evolução do Score Técnico
    com marcadores de sinal.
    """

    fig = create_score_history_chart(
        score_history
    )

    if fig is None:

        return None

    fig = add_signal_markers(
        fig,
        score_history,
    )

    fig.update_layout(
        title=(
            "Evolução do Score Técnico "
            "e Sinais"
        ),
    )

    return fig


# ==========================================================
# GRÁFICO INTEGRADO
# ==========================================================

def create_integrated_analysis_chart(
    historical_indicators,
    score_history,
):
    """
    Cria um gráfico integrado
    com dois painéis:

    Painel 1:
    - Preço
    - MA21
    - MA200

    Painel 2:
    - Score Técnico
    """

    if (
        not validate_dataframe(
            historical_indicators
        )
        and not validate_dataframe(
            score_history
        )
    ):

        return None

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(

            "Preço e Médias Móveis",

            "Evolução do Score Técnico",

        ),
        row_heights=[
            0.6,
            0.4,
        ],
    )

    # ======================================================
    # PAINEL DE PREÇO
    # ======================================================

    if validate_dataframe(
        historical_indicators
    ):

        price_column = get_column(
            historical_indicators,
            [
                "price",
                "Close",
                "close",
            ],
        )

        if price_column is not None:

            price_series = safe_numeric_series(
                historical_indicators,
                price_column,
            )

            if (
                price_series is not None
                and not price_series.dropna().empty
            ):

                fig.add_trace(
                    go.Scatter(
                        x=historical_indicators.index,
                        y=price_series,
                        mode="lines",
                        name="Preço",
                    ),
                    row=1,
                    col=1,
                )

        ma21_column = get_column(
            historical_indicators,
            [
                "ma21",
                "MA21",
            ],
        )

        if ma21_column is not None:

            ma21_series = safe_numeric_series(
                historical_indicators,
                ma21_column,
            )

            if (
                ma21_series is not None
                and not ma21_series.dropna().empty
            ):

                fig.add_trace(
                    go.Scatter(
                        x=historical_indicators.index,
                        y=ma21_series,
                        mode="lines",
                        name="MA21",
                    ),
                    row=1,
                    col=1,
                )

        ma200_column = get_column(
            historical_indicators,
            [
                "ma200",
                "MA200",
            ],
        )

        if ma200_column is not None:

            ma200_series = safe_numeric_series(
                historical_indicators,
                ma200_column,
            )

            if (
                ma200_series is not None
                and not ma200_series.dropna().empty
            ):

                fig.add_trace(
                    go.Scatter(
                        x=historical_indicators.index,
                        y=ma200_series,
                        mode="lines",
                        name="MA200",
                    ),
                    row=1,
                    col=1,
                )

    # ======================================================
    # PAINEL DO SCORE
    # ======================================================

    if validate_dataframe(
        score_history
    ):

        score_column = get_column(
            score_history,
            [
                "technical_score",
                "score",
            ],
        )

        if score_column is not None:

            score_series = safe_numeric_series(
                score_history,
                score_column,
            )

            if (
                score_series is not None
                and not score_series.dropna().empty
            ):

                fig.add_trace(
                    go.Scatter(
                        x=score_history.index,
                        y=score_series,
                        mode="lines+markers",
                        name="Score Técnico",
                    ),
                    row=2,
                    col=1,
                )

        # Linhas de referência do Score

        fig.add_hline(
            y=80,
            line_dash="dash",
            row=2,
            col=1,
        )

        fig.add_hline(
            y=65,
            line_dash="dash",
            row=2,
            col=1,
        )

        fig.add_hline(
            y=50,
            line_dash="dash",
            row=2,
            col=1,
        )

        fig.add_hline(
            y=35,
            line_dash="dash",
            row=2,
            col=1,
        )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_yaxes(
        title_text="Preço",
        row=1,
        col=1,
    )

    fig.update_yaxes(
        title_text="Score",
        range=[
            0,
            100,
        ],
        row=2,
        col=1,
    )

    fig.update_xaxes(
        title_text="Data",
        row=2,
        col=1,
    )

    fig.update_layout(
        title="Análise Histórica Integrada",
        hovermode="x unified",
        template="plotly_white",
        height=750,
        margin={
            "l": 20,
            "r": 20,
            "t": 80,
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

    return fig


# ==========================================================
# GRÁFICO DE COMPARAÇÃO DOS SCORES
# ==========================================================

def create_scores_comparison_chart(
    technical_score,
    fundamental_score,
    integrated_score,
):
    """
    Cria gráfico de barras para
    comparar os três Scores atuais.

    - Score Técnico
    - Score Fundamentalista
    - Score Integrado
    """

    scores = []

    names = []

    if technical_score is not None:

        names.append(
            "Técnico"
        )

        scores.append(
            float(
                technical_score
            )
        )

    if fundamental_score is not None:

        names.append(
            "Fundamentalista"
        )

        scores.append(
            float(
                fundamental_score
            )
        )

    if integrated_score is not None:

        names.append(
            "Integrado"
        )

        scores.append(
            float(
                integrated_score
            )
        )

    if not scores:

        return None

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=names,
            y=scores,
            text=[
                f"{score:.0f}"
                for score in scores
            ],
            textposition="auto",
            name="Score",
        )
    )

    fig.update_layout(
        title="Comparação dos Scores",
        yaxis={
            "range": [
                0,
                100,
            ],
        },
        xaxis_title="Tipo de Score",
        yaxis_title="Pontuação",
        template="plotly_white",
        height=400,
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20,
        },
    )

    return fig
