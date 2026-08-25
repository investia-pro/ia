"""
InvestIA PRO
Módulo de Gráficos

Versão: v0.7.1
Fase: 3.0.6

Gráficos disponíveis:
- Evolução do preço
- Preço + MA21 + MA200
- Volume negociado
- Comparação dos Scores

Compatível com:
- market.py
- indicators.py
- analysis.py
- score.py
- app.py

Princípio:
Uma falha em um gráfico não deve interromper
a análise do ativo.
"""

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=None):
    """
    Converte valores para float com segurança.
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


def get_history(data):
    """
    Localiza o histórico de preços em diferentes
    estruturas utilizadas pelo projeto.

    Aceita:
    - DataFrame
    - Dicionário contendo history
    - Dicionário contendo data
    - Dicionário contendo histórico em outras chaves
    """

    # ------------------------------------------------------
    # DATAFRAME DIRETO
    # ------------------------------------------------------

    if isinstance(
        data,
        pd.DataFrame,
    ):

        if not data.empty:
            return data.copy()

        return pd.DataFrame()

    # ------------------------------------------------------
    # DICIONÁRIO
    # ------------------------------------------------------

    if isinstance(
        data,
        dict,
    ):

        possible_keys = [
            "history",
            "historical_data",
            "data",
            "prices",
            "price_history",
        ]

        for key in possible_keys:

            value = data.get(key)

            if isinstance(
                value,
                pd.DataFrame,
            ):

                if not value.empty:
                    return value.copy()

    return pd.DataFrame()


def find_column(
    dataframe,
    possible_names,
):
    """
    Localiza uma coluna sem diferenciar
    maiúsculas e minúsculas.
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):

        return None

    if dataframe.empty:
        return None

    normalized_columns = {
        str(column).lower(): column
        for column in dataframe.columns
    }

    for name in possible_names:

        normalized_name = str(name).lower()

        if normalized_name in normalized_columns:

            return normalized_columns[
                normalized_name
            ]

    return None


def get_x_axis(dataframe):
    """
    Obtém o eixo X do gráfico.

    Prioridade:
    1. Índice datetime
    2. Coluna Date
    3. Coluna Datetime
    4. Índice padrão
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):

        return None

    if dataframe.empty:
        return None

    if isinstance(
        dataframe.index,
        pd.DatetimeIndex,
    ):

        return dataframe.index

    date_column = find_column(
        dataframe,
        [
            "Date",
            "Datetime",
            "date",
            "datetime",
        ],
    )

    if date_column is not None:

        return dataframe[
            date_column
        ]

    return dataframe.index


def empty_figure(
    title="Dados não disponíveis",
):
    """
    Retorna uma figura vazia com mensagem.
    """

    figure = go.Figure()

    figure.add_annotation(
        text=title,
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
        height=350,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20,
        ),
    )

    return figure


def prepare_history(data):
    """
    Prepara o histórico para os gráficos.
    """

    history = get_history(data)

    if history.empty:
        return history

    history = history.copy()

    # Remove colunas totalmente vazias
    history = history.dropna(
        axis=1,
        how="all",
    )

    return history


# ==========================================================
# GRÁFICO DE PREÇO
# ==========================================================

def create_price_chart(
    data,
    asset=None,
):
    """
    Cria gráfico simples da evolução do preço.

    Parâmetros:
    ----------
    data : dict ou DataFrame
        Dados contendo o histórico.

    asset : str
        Código do ativo.

    Retorno:
    --------
    plotly.graph_objects.Figure
    """

    try:

        history = prepare_history(
            data
        )

        if history.empty:

            return empty_figure(
                "Histórico de preços não disponível."
            )

        close_column = find_column(
            history,
            [
                "Close",
                "Adj Close",
                "close",
                "adj_close",
            ],
        )

        if close_column is None:

            return empty_figure(
                "Coluna de preço não encontrada."
            )

        x_axis = get_x_axis(
            history
        )

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=x_axis,
                y=history[
                    close_column
                ],
                mode="lines",
                name="Preço",
            )
        )

        title = (
            f"Evolução do Preço - {asset}"
            if asset
            else "Evolução do Preço"
        )

        figure.update_layout(
            title=title,
            xaxis_title="Data",
            yaxis_title="Preço",
            hovermode="x unified",
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        return figure

    except Exception:

        return empty_figure(
            "Não foi possível gerar o gráfico de preço."
        )


# ==========================================================
# GRÁFICO DE PREÇO + MÉDIAS MÓVEIS
# ==========================================================

def create_technical_chart(
    data,
    asset=None,
):
    """
    Cria gráfico técnico contendo:

    - Preço
    - Média móvel de 21 períodos
    - Média móvel de 200 períodos

    As médias são calculadas diretamente no gráfico
    quando não estiverem disponíveis no DataFrame.
    """

    try:

        history = prepare_history(
            data
        )

        if history.empty:

            return empty_figure(
                "Histórico técnico não disponível."
            )

        close_column = find_column(
            history,
            [
                "Close",
                "Adj Close",
                "close",
                "adj_close",
            ],
        )

        if close_column is None:

            return empty_figure(
                "Coluna de preço não encontrada."
            )

        history = history.copy()

        price_series = pd.to_numeric(
            history[
                close_column
            ],
            errors="coerce",
        )

        if price_series.dropna().empty:

            return empty_figure(
                "Não há preços válidos para análise."
            )

        x_axis = get_x_axis(
            history
        )

        # --------------------------------------------------
        # MA21
        # --------------------------------------------------

        ma21_column = find_column(
            history,
            [
                "MA21",
                "ma21",
                "MA_21",
                "ma_21",
            ],
        )

        if ma21_column is not None:

            ma21 = pd.to_numeric(
                history[
                    ma21_column
                ],
                errors="coerce",
            )

        else:

            ma21 = price_series.rolling(
                window=21,
                min_periods=1,
            ).mean()

        # --------------------------------------------------
        # MA200
        # --------------------------------------------------

        ma200_column = find_column(
            history,
            [
                "MA200",
                "ma200",
                "MA_200",
                "ma_200",
            ],
        )

        if ma200_column is not None:

            ma200 = pd.to_numeric(
                history[
                    ma200_column
                ],
                errors="coerce",
            )

        else:

            ma200 = price_series.rolling(
                window=200,
                min_periods=1,
            ).mean()

        # --------------------------------------------------
        # FIGURA
        # --------------------------------------------------

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=x_axis,
                y=price_series,
                mode="lines",
                name="Preço",
            )
        )

        figure.add_trace(
            go.Scatter(
                x=x_axis,
                y=ma21,
                mode="lines",
                name="MA21",
            )
        )

        figure.add_trace(
            go.Scatter(
                x=x_axis,
                y=ma200,
                mode="lines",
                name="MA200",
            )
        )

        title = (
            f"Análise Técnica - {asset}"
            if asset
            else "Análise Técnica"
        )

        figure.update_layout(
            title=title,
            xaxis_title="Data",
            yaxis_title="Preço",
            hovermode="x unified",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            margin=dict(
                l=20,
                r=20,
                t=80,
                b=20,
            ),
        )

        return figure

    except Exception:

        return empty_figure(
            "Não foi possível gerar o gráfico técnico."
        )


# ==========================================================
# GRÁFICO DE VOLUME
# ==========================================================

def create_volume_chart(
    data,
    asset=None,
):
    """
    Cria gráfico do volume negociado.
    """

    try:

        history = prepare_history(
            data
        )

        if history.empty:

            return empty_figure(
                "Dados de volume não disponíveis."
            )

        volume_column = find_column(
            history,
            [
                "Volume",
                "volume",
            ],
        )

        if volume_column is None:

            return empty_figure(
                "Coluna de volume não encontrada."
            )

        volume = pd.to_numeric(
            history[
                volume_column
            ],
            errors="coerce",
        )

        if volume.dropna().empty:

            return empty_figure(
                "Não há dados de volume válidos."
            )

        x_axis = get_x_axis(
            history
        )

        figure = go.Figure()

        figure.add_trace(
            go.Bar(
                x=x_axis,
                y=volume,
                name="Volume",
            )
        )

        title = (
            f"Volume Negociado - {asset}"
            if asset
            else "Volume Negociado"
        )

        figure.update_layout(
            title=title,
            xaxis_title="Data",
            yaxis_title="Volume",
            height=350,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        return figure

    except Exception:

        return empty_figure(
            "Não foi possível gerar o gráfico de volume."
        )


# ==========================================================
# GRÁFICO DOS SCORES
# ==========================================================

def create_score_chart(
    technical_score=None,
    fundamental_score=None,
    integrated_score=None,
):
    """
    Cria gráfico comparativo dos três Scores.

    Scores:
    - Técnico
    - Fundamentalista
    - Integrado
    """

    try:

        technical_score = safe_float(
            technical_score,
            0,
        )

        fundamental_score = safe_float(
            fundamental_score,
            0,
        )

        integrated_score = safe_float(
            integrated_score,
            0,
        )

        technical_score = max(
            0,
            min(
                100,
                technical_score,
            ),
        )

        fundamental_score = max(
            0,
            min(
                100,
                fundamental_score,
            ),
        )

        integrated_score = max(
            0,
            min(
                100,
                integrated_score,
            ),
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
                name="Score",
            )
        )

        figure.update_layout(
            title="Comparativo dos Scores",
            yaxis=dict(
                title="Pontuação",
                range=[
                    0,
                    100,
                ],
            ),
            height=400,
            showlegend=False,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        return figure

    except Exception:

        return empty_figure(
            "Não foi possível gerar o gráfico dos Scores."
        )


# ==========================================================
# GRÁFICO COMPARATIVO COMPLETO
# ==========================================================

def create_dashboard_charts(
    prepared_data,
    asset=None,
    technical_score=None,
    fundamental_score=None,
    integrated_score=None,
):
    """
    Cria todos os gráficos principais do dashboard.

    Retorna um dicionário contendo:

    {
        "price_chart": Figure,
        "technical_chart": Figure,
        "volume_chart": Figure,
        "score_chart": Figure,
    }
    """

    charts = {}

    try:

        charts[
            "price_chart"
        ] = create_price_chart(
            prepared_data,
            asset,
        )

    except Exception:

        charts[
            "price_chart"
        ] = empty_figure(
            "Erro no gráfico de preço."
        )

    try:

        charts[
            "technical_chart"
        ] = create_technical_chart(
            prepared_data,
            asset,
        )

    except Exception:

        charts[
            "technical_chart"
        ] = empty_figure(
            "Erro no gráfico técnico."
        )

    try:

        charts[
            "volume_chart"
        ] = create_volume_chart(
            prepared_data,
            asset,
        )

    except Exception:

        charts[
            "volume_chart"
        ] = empty_figure(
            "Erro no gráfico de volume."
        )

    try:

        charts[
            "score_chart"
        ] = create_score_chart(
            technical_score,
            fundamental_score,
            integrated_score,
        )

    except Exception:

        charts[
            "score_chart"
        ] = empty_figure(
            "Erro no gráfico dos Scores."
        )

    return charts


# ==========================================================
# COMPATIBILIDADE COM VERSÕES ANTERIORES
# ==========================================================

def plot_price_chart(
    data,
    asset=None,
):
    """
    Alias para create_price_chart().
    """

    return create_price_chart(
        data,
        asset,
    )


def plot_technical_chart(
    data,
    asset=None,
):
    """
    Alias para create_technical_chart().
    """

    return create_technical_chart(
        data,
        asset,
    )


def plot_volume_chart(
    data,
    asset=None,
):
    """
    Alias para create_volume_chart().
    """

    return create_volume_chart(
        data,
        asset,
    )


def plot_score_chart(
    technical_score=None,
    fundamental_score=None,
    integrated_score=None,
):
    """
    Alias para create_score_chart().
    """

    return create_score_chart(
        technical_score,
        fundamental_score,
        integrated_score,
    )
