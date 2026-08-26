"""
InvestIA PRO - Módulo de Visualização Gráfica Interativa com Plotly
"""
import plotly.graph_objects as go
import pandas as pd

def create_price_chart(analysis_result: dict) -> go.Figure:
    """
    Gera gráfico interativo com Preço, MA21 e MA200.
    """
    history = analysis_result.get("history")
    asset = analysis_result.get("asset", "Ativo")

    fig = go.Figure()

    if history is None or history.empty:
        fig.update_layout(title="Sem dados de histórico disponíveis para exibição.")
        return fig

    # Linha de Fechamento
    fig.add_trace(go.Scatter(
        x=history.index, 
        y=history['Close'], 
        mode='lines',
        name='Preço de Fechamento',
        line=dict(color='#00F0FF', width=2)
    ))

    # Média Móvel 21
    if len(history) >= 21:
        ma21 = history['Close'].rolling(window=21).mean()
        fig.add_trace(go.Scatter(
            x=history.index, 
            y=ma21, 
            mode='lines',
            name='MA 21',
            line=dict(color='#FFB800', width=1.5, dash='dash')
        ))

    # Média Móvel 200
    if len(history) >= 200:
        ma200 = history['Close'].rolling(window=200).mean()
        fig.add_trace(go.Scatter(
            x=history.index, 
            y=ma200, 
            mode='lines',
            name='MA 200',
            line=dict(color='#FF0055', width=1.5)
        ))

    fig.update_layout(
        title=f"Histórico de Preços e Médias Móveis — {asset}",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_scanner_summary_chart(df_scanner: pd.DataFrame) -> go.Figure:
    """
    Gera gráfico de barras ordenado para o Scanner de Mercado.
    """
    fig = go.Figure()
    if df_scanner.empty:
        return fig

    colors = ['#00E676' if s >= 65 else ('#FFD600' if s >= 45 else '#FF5252') for s in df_scanner['Score']]

    fig.add_trace(go.Bar(
        x=df_scanner['Ativo'],
        y=df_scanner['Score'],
        marker_color=colors,
        text=df_scanner['Score'].astype(str),
        textposition='auto'
    ))

    fig.update_layout(
        title="Comparativo de Score InvestIA — Scanner de Mercado",
        xaxis_title="Ativo",
        yaxis_title="Score (0 - 100)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig
