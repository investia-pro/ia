# ==========================================
# InvestIA PRO
# Configurações Gerais
# ==========================================

APP_NAME = "InvestIA PRO"

DEFAULT_PERIOD = "6mo"

DEFAULT_INTERVAL = "1d"

# ------------------------------------------
# Mercados
# ------------------------------------------

ATIVOS_B3 = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "BBAS3": "BBAS3.SA",
    "BBDC4": "BBDC4.SA",
    "ABEV3": "ABEV3.SA",
    "WEGE3": "WEGE3.SA",
    "RENT3": "RENT3.SA",
    "PRIO3": "PRIO3.SA",
    "SUZB3": "SUZB3.SA"
}

ACOES_USA = {
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "NVDA": "NVDA",
    "AMZN": "AMZN",
    "META": "META",
    "GOOGL": "GOOGL",
    "TSLA": "TSLA"
}

CRIPTOS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "XRP": "XRP-USD"
}

# ------------------------------------------
# Pesos do Score
# ------------------------------------------

PESOS = {

    "tendencia":25,

    "rsi":20,

    "macd":20,

    "medias":20,

    "volume":10,

    "volatilidade":5

}

# ------------------------------------------
# Cores
# ------------------------------------------

COR_COMPRA = "#16a34a"

COR_NEUTRO = "#f59e0b"

COR_VENDA = "#dc2626"

# ------------------------------------------
# Timeframes
# ------------------------------------------

PERIODOS = [
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y"
]
