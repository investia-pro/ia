"""
===========================================
InvestIA PRO
config.py
Configurações gerais do sistema
===========================================
"""

# ==========================================
# Dados do Sistema
# ==========================================

APP_NAME = "InvestIA PRO"
VERSION = "0.5.2"

# ==========================================
# Configuração do Yahoo Finance
# ==========================================

DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"

# ==========================================
# Ativos B3
# ==========================================

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

# ==========================================
# Ações Americanas
# ==========================================

ACOES_USA = {
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "NVDA": "NVDA",
    "AMZN": "AMZN",
    "META": "META",
    "GOOGL": "GOOGL",
    "TSLA": "TSLA",
    "AMD": "AMD"
}

# ==========================================
# ETFs
# ==========================================

ETFS = {
    "SPY": "SPY",
    "QQQ": "QQQ",
    "DIA": "DIA",
    "IVV": "IVV",
    "VOO": "VOO"
}

# ==========================================
# FIIs
# ==========================================

FIIS = {
    "MXRF11": "MXRF11.SA",
    "HGLG11": "HGLG11.SA",
    "KNRI11": "KNRI11.SA",
    "XPLG11": "XPLG11.SA",
    "VISC11": "VISC11.SA"
}

# ==========================================
# Criptomoedas
# ==========================================

CRIPTOS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD"
}

# ==========================================
# Score
# ==========================================

SCORE_COMPRA_FORTE = 80
SCORE_COMPRA = 60
SCORE_NEUTRO = 40

# ==========================================
# Cache
# ==========================================

CACHE_MINUTES = 5
