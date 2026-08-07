"""
InvestIA PRO
Utilidades gerais

Versão: v0.5.3
"""


def validate_data(data):

    """
    Verifica se os dados recebidos
    possuem informações suficientes.
    """

    required_fields = [
        "price",
        "rsi",
        "ma21",
        "ma200"
    ]


    for field in required_fields:

        if field not in data:

            return False


        if data[field] is None:

            return False


    return True



def format_currency(value):

    """
    Formata valores monetários.
    """

    if value is None:

        return "N/A"


    return f"R$ {value:,.2f}".replace(
        ",",
        "X"
    ).replace(
        ".",
        ","
    ).replace(
        "X",
        "."
    )



def safe_number(value):

    """
    Evita erros com valores vazios.
    """

    try:

        return float(value)

    except:

        return 0



def risk_color(risk):

    """
    Retorna indicador visual de risco.
    """

    mapping = {

        "Baixo": "🟢",

        "Moderado": "🟡",

        "Alto": "🔴"

    }


    return mapping.get(
        risk,
        "⚪"
    )
