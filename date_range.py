# date_range.py

import sys
from datetime import datetime, timedelta


def get_date_range():

    args = sys.argv[1:]

    # CASO 1: sin fechas → mes anterior completo
    if len(args) == 0:

        today = datetime.today()

        start = datetime(today.year, 1, 1)
        end = today - timedelta(days=1)

    # CASO 2: solo una fecha
    elif len(args) == 1:

        date = datetime.strptime(args[0], "%Y-%m-%d")

        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)

    # CASO 3: rango de fechas
    elif len(args) == 2:

        start = datetime.strptime(args[0], "%Y-%m-%d")
        end = datetime.strptime(args[1], "%Y-%m-%d") + timedelta(days=1)

        if start >= end:
            raise ValueError("La fecha inicial debe ser menor que la final")

    else:
        raise ValueError("Uso: python main.py [fecha_inicio] [fecha_fin]")

    start_str = start.strftime("%Y-%m-%dT00:00:00.000Z")
    end_str = end.strftime("%Y-%m-%dT00:00:00.000Z")

    return start_str, end_str