"""Translate a given number into letters."""
from typing import Set

UNITS: Set[str] = {
    "1": "yiris",
    "2": "päräꞌ",
    "3": "chibin",
    "4": "vajpedyeꞌ",
    "5": "ĉanamꞌ",
    "6": "jäbän",
    "7": "yävätidyeꞌ",
    "8": "quencan",
    "9": "arajtac",
}

VALUE_ERROR: str = "Numbers greather than 99 are taken from spanish, and are not taken into account here."

def number_to_letters(number: str) -> str:
    """
    This function will translate a given number into letters.

    Parameters
    ----------
    - number: str
        The number to translate into letters. Must be between 1 and 99.
    
    Returns
    -------
    - str:
        The given number translated into letters.
    
    Raises
    ------
    - ValueError:
        When the given number is greather than 99.
    """
    if int(number) > 99:
        raise ValueError(VALUE_ERROR)
    # the number is in range [1, 9]
    if int(number) in range(1, 10):
        return UNITS[number]
    # the number is in range [10, 99]
    unit = UNITS.get(number[1], "")
    if unit:
        unit = f"{unit} jiyiꞌ"
    # exception for the number between 10 and 19.
    if number[0] == "1":
        return f"yiriꞌ tac {unit}".strip()
    # number between 20 and 99 in Tsimane.
    return f"{UNITS[number[0]]} qui tac {unit}".strip()