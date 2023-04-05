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
from typing import Optional

import streamlit as st

from ai_sustainability.classes.utils import validate_text_input
from ai_sustainability.classes.utils_streamlit import check_user_connection


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
        self.username = check_user_connection()

    def show_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        if dict_question["label"] == "Q_Open":
            return self.show_open_question(dict_question, previous_answer)
        if dict_question["label"] == "Q_QCM" or dict_question["label"] == "Q_QCM_Bool":
            return self.show_qcm_question(dict_question, previous_answer)
        if dict_question["label"] == "Q_QRM":
            return self.show_qrm_question(dict_question, previous_answer)
        if dict_question["label"] == "end":
            return [""]
        print("Error, question label no recognised")
        return [""]

    def show_open_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        if previous_answer is None:  # If it has to be auto-completed before
            previous_answer = [""]
        # We show the question text area
        answer = str(
            st.text_area(
                label=dict_question["question_text"],
                height=100,
                label_visibility="visible",
                value=previous_answer[0],
                help=dict_question["help_text"],
            )
        )
        # If no answer given, we return None
        if not answer:
            return [""]

        validated_answer = validate_text_input(answer)
        return [validated_answer]

    def show_qcm_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        options = ["<Select an option>"] + dict_question["answers"]
        previous_index = 0
        if previous_answer is not None:  # If it has to be auto-completed before
            previous_index = options.index(previous_answer[0])
        # We show the question selectbox
        answer = str(
            st.selectbox(
                label=dict_question["question_text"],
                options=options,
                index=previous_index,
                help=dict_question["help_text"],
            )
        )
        # If no answer given, we return None
        if answer == "<Select an option>":
            return [""]
        return [answer]

    def show_qrm_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        default = []
        if previous_answer is not None:  # If it has to be auto-completed before
            default = previous_answer
        answers = st.multiselect(
            label=dict_question["question_text"],
            options=dict_question["answers"],
            default=default,
            help=dict_question["help_text"],
        )
        # If no answer given, we return None
        if not answers:
            return [""]
        return answers
