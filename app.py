import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

from market import obter_ranking

st.set_page_config(
    page_title='InvestIA PRO',
    page_icon='📈',
    layout='wide'
)

st.title('📈 InvestIA PRO')

if st.button('🔄 Atualizar'):
    st.rerun()

st.divider()

ranking = obter_ranking()

if len(ranking):

    st.subheader('🏆 Top Oportunidades')

    top = ranking.head(3)

    c1, c2, c3 = st.columns(3)

    colunas = [c1, c2, c3]

    for i in range(len(top)):

        linha = top.iloc[i]

        with colunas[i]:

            st.metric(
                linha['Ativo'],
                f'Score {linha["Score"]}',
                linha['Recomendação']
            )

st.divider()

st.subheader('📊 Ranking do Mercado')

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

st.divider()

ativo = st.text_input(
    '🔍 Pesquisar ativo',
    placeholder='PETR4, VALE3, AAPL, NVDA, BTC-USD...'
)

if ativo:

    ticker = ativo.upper()

    if ticker in ['PETR4', 'VALE3', 'ITUB4']:
        ticker += '.SA'

    try:

        dados = yf.Ticker(ticker)

        hist = dados.history(period='6mo')

        info = dados.info

        st.header(f'📈 {ativo.upper()}')

        atual = hist['Close'].iloc[-1]
        anterior = hist['Close'].iloc[-2]

        variacao = ((atual - anterior) / anterior) * 100

        moeda = 'R$' if ticker.endswith('.SA') else 'US$'

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                'Preço Atual',
                f'{moeda} {atual:,.2f}'
            )

        with c2:
            st.metric(
                'Variação',
                f'{variacao:.2f}%'
            )

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=ativo
            )
        )

        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            margin=dict(l=5, r=5, t=20, b=5)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader('📋 Resumo')

        r1, r2, r3 = st.columns(3)

        with r1:
            st.metric(
                'Máxima do dia',
                f'{moeda} {info.get("dayHigh", "-")}'
            )

        with r2:
            st.metric(
                'Mínima do dia',
                f'{moeda} {info.get("dayLow", "-")}'
            )

        with r3:
            st.metric(
                'Volume',
                info.get('volume', '-')
            )

    except Exception as erro:

        st.error('Ativo não encontrado')
        st.write(erro)
