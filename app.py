def get_current_price_safe(
    prepared_data,
    indicators,
):
    """
    Obtém o preço atual do ativo com
    compatibilidade entre diferentes
    versões dos módulos.
    """

    # ------------------------------------------------------
    # PROCURA NOS INDICADORES
    # ------------------------------------------------------

    if isinstance(indicators, dict):

        possible_keys = [

            "price",

            "current_price",

            "close",

            "last_price",
        ]

        for key in possible_keys:

            value = indicators.get(key)

            if value is not None:

                value = safe_float(value)

                if value is not None:

                    return value

    # ------------------------------------------------------
    # PROCURA NOS DADOS PREPARADOS
    # ------------------------------------------------------

    if isinstance(prepared_data, dict):

        possible_keys = [

            "price",

            "current_price",

            "close",

            "last_price",
        ]

        for key in possible_keys:

            value = prepared_data.get(key)

            if value is not None:

                value = safe_float(value)

                if value is not None:

                    return value

    # ------------------------------------------------------
    # PROCURA NO HISTÓRICO
    # ------------------------------------------------------

    history = None

    if isinstance(prepared_data, dict):

        history = prepared_data.get(
            "history"
        )

    if history is not None:

        if hasattr(history, "empty"):

            if not history.empty:

                possible_columns = [

                    "Close",

                    "Adj Close",

                    "close",

                    "adj_close",
                ]

                for column in possible_columns:

                    if column in history.columns:

                        value = history[
                            column
                        ].iloc[-1]

                        value = safe_float(
                            value
                        )

                        if value is not None:

                            return value

    return None
