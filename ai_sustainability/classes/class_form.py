"""
Class which contains the form composed of the different questions/answers
Streamlit class

methods:
    - display_question
    - display_answer
    - ...

    ONE QUESTION :
    return : dict {
            1: question_text
            2: answers
            3: help_text
            4: question_label
        }
    
    A chaque réponse de l'utilisateur, retourner le texte de celle-ci ainsi que les anciennes réponses (list(str))
    Pour Q_QRM, list dans list (list(list(str)))
    Pour Q_NEXT, Q_QCM, str answer    
"""
import streamlit as st

from ai_sustainability.classes.utils_streamlit import check_user_connected


class FormStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
    """

    def __init__(self, database_link) -> None:
        self.database_link = database_link

        st.set_page_config(page_title="Form Page", page_icon="📝")
        st.title("📝Form")
        self.username = check_user_connected()
