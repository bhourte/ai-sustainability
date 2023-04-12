"""
NO DB/NO STREAMLIT

function usefull for the project

method:
    - no_dash_in_my_text 
    - validate_text_input
"""


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


def validate_text_input(text: str) -> str:
    """
    Validate the answer to avoid errors in the gremlin query (if there is ' in the text for now on)

    Parameters :
        - text : the answer to validate (string)

    Return :
        - text : the validated answer (string)
    """
    text = text.replace('"', '\\"')
    return text.replace("'", "\\'")
