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


def get_n_best(n_best: int, list_names_and_values: list[Tuple[str, int]]) -> list[str]:
    """Method used to get the n_best higher value in a Tuple[name, value]"""
    list_names_and_values.sort(key=lambda x: x[1], reverse=True)
    best_name = []
    for name, value in list_names_and_values:
        if value > 0:
            best_name.append(name)
    return best_name[:n_best]
