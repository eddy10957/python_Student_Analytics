import math
from datetime import datetime

def _truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

def _timestampToPeriod(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    dt_object = dt_object.replace(hour=1, minute=1, second=1)
    return int(datetime.timestamp(dt_object))
  
def adjust(number) -> str:
    return _timestampToPeriod(_truncate(number))
