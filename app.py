"""
InvestIA PRO — Aplicação Principal Streamlit (Fase 3.0.7 - Scanner Expandido)
"""
import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Garantia de path para subpastas no Streamlit Cloud
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from config import APP_TITLE, PAGE_ICON
    from market import fetch_asset_data
    from analysis import analyze_asset
    from charts import create_price_chart, create_scanner_summary_chart
    from utils import format_currency, format_percent
except ImportError:
    from .config import APP_TITLE, PAGE_ICON
    from .market import fetch_asset_data
    from .analysis import analyze_asset
    from .charts import create_price_chart, create_scanner_summary_chart
    from .utils import format_currency, format_percent

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Listas Pré-configuradas para Varredura Completa do Mercado
PRESET_LISTS = {
    "🔥 Principais Ações B3 (Top 30 Liquidez)": [
        "PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "ABEV3", "WEGE3", "PRIO3", "RENT3", "SUZB3",
        "B3SA3", "EQTL3", "ELET3", "RADL3", "RDOR3", "VBBR3", "VAMO3", "GGBR4", "CSAN3", "RAIZ4",
        "HAPV3", "CPLE6", "CMIG4", "UGPA3", "SANB11", "KLBN11", "EMBR3", "ALOS3", "MULT3", "TOTS3"
    ],
    "🏢 Fundos Imobiliários (FIIs)": [
        "HGLG11", "KNCR11", "MXRF11", "XPML11", "BTLG11", "VISC11", "TGAR11", "KNR111", "CPTS11", "IRDM11"
    ],
    "🇺🇸 BDRs / Big Techs EUA": [
        "AAPL34", "MSFT34", "GOGL34", "AMZO34", "NVDC34", "TSLA34", "MELI34"
    ]
}

st.title("📈 InvestIA PRO — Análise de Mercado & Scanner")
st.caption("Fase 3.0.7 — Scanner Automático do Mercado (Ações, FIIs e BDRs)")

menu = st.sidebar.radio("Navegação", ["Dashboard Executivo", "Scanner de Mercado", "Sobre o Projeto"])

if menu == "Dashboard Executivo":
    st.subheader("🔍 Análise Individual de Ativo")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Digite o Ticker do Ativo (ex: PETR4, VALE3, ITUB4):", value="PETR4")
    with col_btn:
        st.write("")
        st.write("")
        btn_analyze = st.button("ANALISAR", type="primary", use_container_width=True)

    if btn_analyze or ticker_input:
        with st.spinner(f"Coletando dados e analisando {ticker_input}..."):
            mkt_data = fetch_asset_data(ticker_input)
            
            if not mkt_data["is_valid"]:
                st.error(f"Erro: {mkt_data['error']}")
            else:
                res = analyze_asset(mkt_data)
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Preço Atual", format_currency(res["price"]), delta=format_percent(res["change_percent"]))
                c2.metric("Score InvestIA", f"{res['score']} / 100", delta=res["signal"])
                c3.metric("Classificação", res["classification"])
                c4.metric("Tendência", res["trend"])
                c5.metric("Nível de Risco", res["risk"])

                st.markdown("---")

                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown("### 📋 Resumo Executivo")
                    st.info(res["executive_summary"])
                    st.markdown(f"**Recomendação:** {res['recommendation']}")

                    st.markdown("#### Justificativas do Sinal:")
                    for r in res["reasons"]:
                        st.write(f"• {r}")

                with col_right:
                    st.markdown("### 📊 Decomposição do Score")
                    b = res["breakdown"]
                    st.write(f"• **Tendência:** {b['trend_score']} / 40 pts")
                    st.write(f"• **RSI:** {b['rsi_score']} / 35 pts")
                    st.write(f"• **Volatilidade/Risco:** {b['volatility_score']} / 25 pts")
                    
                    st.markdown("#### Detalhes Técnicos:")
                    st.write(f"• **RSI (14):** {res['rsi']} ({res['rsi_status']})")
                    st.write(f"• **MA 21:** {format_currency(res['ma21'])}")
                    st.write(f"• **MA 200:** {format_currency(res['ma200'])}")
                    st.write(f"• **Volatilidade Anual:** {res['volatility']:.2f}%")

                st.markdown("---")
                st.plotly_chart(create_price_chart(res), use_container_width=True)

elif menu == "Scanner de Mercado":
    st.subheader("🎯 Scanner de Oportunidades Automático")
    st.write("Varra o mercado em busca dos ativos com melhor Score InvestIA em tempo real.")

    # Filtros do Scanner
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        preset_choice = st.selectbox("Selecione o Grupo de Ativos para Varredura:", list(PRESET_LISTS.keys()))
        selected_preset = PRESET_LISTS[preset_choice]
    
    with col_sel2:
        top_n = st.slider("Exibir Top N Melhores:", min_value=5, max_value=len(selected_preset), value=10)

    # Permitir personalização manual da lista se o usuário quiser
    with st.expander("🛠️ Personalizar Lista de Ativos do Scan"):
        assets_to_scan = st.multiselect("Ativos incluídos na varredura:", options=selected_preset, default=selected_preset)

    if st.button("🚀 INICIAR VARREDURA DO MERCADO", type="primary"):
        results_list = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(assets_to_scan):
            status_text.text(f"Analisando {symbol} ({i+1}/{len(assets_to_scan)})...")
            m_data = fetch_asset_data(symbol)
            if m_data["is_valid"]:
                analysis = analyze_asset(m_data)
                results_list.append({
                    "Ativo": analysis["asset"],
                    "Preço (R$)": analysis["price"],
                    "Var. (%)": analysis["change_percent"],
                    "Score": analysis["score"],
                    "Sinal": f"{analysis['signal_icon']} {analysis['signal']}",
                    "Classificação": analysis["classification"],
                    "Tendência": analysis["trend"],
                    "Risco": analysis["risk"],
                    "RSI": analysis["rsi"]
                })
            progress_bar.progress((i + 1) / len(assets_to_scan))
            time.sleep(0.05)  # Pequena pausa estratégica

        status_text.text("Varredura concluída com sucesso!")
        
        if results_list:
            df_res = pd.DataFrame(results_list)
            df_res = df_res.sort_values(by="Score", ascending=False).reset_index(drop=True)
            df_top = df_res.head(top_n)

            st.markdown(f"### 🏆 Top {top_n} Maiores Pontuações no Mercado")
            st.dataframe(df_top, use_container_width=True)

            st.plotly_chart(create_scanner_summary_chart(df_top), use_container_width=True)
        else:
            st.warning("Não foi possível coletar dados para a lista selecionada.")

elif menu == "Sobre o Projeto":
    st.subheader("🚀 Sobre o InvestIA PRO")
    st.markdown("""
    O **InvestIA PRO** é um sistema modular em desenvolvimento para análise quantitativa e qualitativa do mercado financeiro.
    """)
