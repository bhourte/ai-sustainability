"""
NO DB/NO STREAMLIT

function usefull for the project

method:
    - check_if_name_ok 
    - validate_text_input
"""


from typing import Tuple


def check_if_name_ok(text: str) -> tuple:
    """
    Check if there is a special character in the name

    Parameters:
        - text (str): text to check

    Return:
        - bool: True if there is a special character (" ' - or backslash), False otherwise
    """
    if "-" in text:
        return True, "-"
    if "\\" in text:
        return True, "\\\\"
    if '"' in text:
        return True, '"'
    if "'" in text:
        return True, "'"
    return False, ""


def sanitize_text_input(text: str) -> str:
    """
    Validate the answer to avoid errors in the gremlin query (if there is ' in the text for now on)

    Parameters :
        - text : the answer to validate (string)

    Return :
        - text : the validated answer (string)
    """
    text = text.replace('"', '\\"')
    return text.replace("'", "\\'")


def select_n_best_ais(nb_ai: int, list_ai_coef: list[Tuple[str, int]]) -> list[str]:
    list_ai_coef.sort(key=lambda x: x[1], reverse=True)
    list_best_ais: list[str] = []
    for _ in range(nb_ai):
        best_ai = list_ai_coef.pop(1)
        if best_ai[1] > 0:
            list_best_ais.append(best_ai[0])
    return list_best_ais
