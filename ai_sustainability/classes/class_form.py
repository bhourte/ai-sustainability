"""
Class which contains the form composed of the different questions/answers
Streamlit class
"""
from typing import Optional

import streamlit as st

from ai_sustainability.classes.utils import no_dash_in_my_text, validate_text_input
from ai_sustainability.classes.utils_streamlit import check_user_connection


class FormStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - set_atribute : set the page attributes
        - show_question : select with methode use in function of the question label
        - show_open_question : show a Q_open question
        - show_qcm_question : show a Q_QCM and Q_QCM_Bool question
        - show_qrm_question : show a Q_QRM question
        - check_name
        - input_form_name
        - error_name_already_taken
        - show_submission_button
        - set_state
        - show_best_ai
    """

    def __init__(self, database_link, set_page: bool = True) -> None:
        self.database_link = database_link
        if set_page:
            self.set_atribute()
        if "clicked" not in st.session_state:
            st.session_state.clicked = False

    def set_atribute(self) -> None:
        st.set_page_config(page_title="Form Page", page_icon="📝")
        st.title("📝Form")
        self.username = check_user_connection()

    def show_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        answer = [""]
        if dict_question["question_label"] == "Q_Open":
            answer = self.show_open_question(dict_question, previous_answer)
        elif dict_question["question_label"] == "Q_QCM" or dict_question["question_label"] == "Q_QCM_Bool":
            answer = self.show_qcm_question(dict_question, previous_answer)
        elif dict_question["question_label"] == "Q_QRM":
            answer = self.show_qrm_question(dict_question, previous_answer)
        elif dict_question["question_label"] == "end":  # This is the end (of the form)
            return ["end"]
        else:
            print("Error, question label no recognised")
        if answer == [""]:
            st.session_state.last_form_name = None  # We put the variable to None because we detect that is a new form
            st.session_state.clicked = False
        return answer

    def show_open_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        if previous_answer is None:  # If it has not to be auto-completed before
            previous_answer = [""]
        # We show the question text area
        answer = str(
            st.text_area(
                label=dict_question["question_text"],
                height=100,
                label_visibility="visible",
                value=previous_answer[0],
                help=dict_question["help_text"],
                disabled=st.session_state.clicked,
            )
        )
        # If no answer given, we return an empty string
        if not answer:
            st.session_state.clicked = False
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
                disabled=st.session_state.clicked,
            )
        )
        # If no answer given, we return an empty string
        return [answer] if answer != "<Select an option>" else [""]

    def show_qrm_question(self, dict_question: dict, previous_answer: Optional[list] = None) -> list[str]:
        default = []
        if previous_answer is not None:  # If it has to be auto-completed before
            default = previous_answer
        answers = st.multiselect(
            label=dict_question["question_text"],
            options=dict_question["answers"],
            default=default,
            help=dict_question["help_text"],
            disabled=st.session_state.clicked,
        )
        # If no answer given, we return None
        return [""] if not answers else answers

    def check_name(self, string: str) -> str:
        no_dash, char = no_dash_in_my_text(string)
        if no_dash:
            st.warning(f"""Please don't use the {char} character in your form name""")
            return ""
        return validate_text_input(string)

    def input_form_name(self, previous_answer: str = "") -> str:
        if previous_answer:
            text = "If you want to change the name of the form, change it here:"
        else:
            text = "Give a name to your form here"
        form_name = st.text_input(text, previous_answer, disabled=st.session_state.clicked)
        return self.check_name(form_name)

    def error_name_already_taken(self, form_name: str) -> bool:
        if st.session_state.last_form_name != form_name:
            st.warning(
                "You already have a form with this name, please pick an other name or change your previous form in the historic page."
            )
            return True
        return False

    def show_submission_button(self) -> bool:
        if st.button("Submit", on_click=self.set_state, disabled=st.session_state.clicked):
            st.write("Answers saved")
            st.session_state.last_form_name = None
            return True
        return False

    def set_state(self) -> None:
        st.session_state.clicked = True

    def show_best_ai(self, list_bests_ais: list) -> None:
        """
            Method used to show the n best AI obtained after the user has completed the Form
            The number of AI choosen is based on the nbai wanted by the user and
            the maximum of available AI for the use of the user
            (If there is only 3 AI possible, but the user asked for 5, only 3 will be shown)

        Parameters:
            - list_bests_ais (list): list of the n best AI

        Return:
            - None
        """
        if len(list_bests_ais) > 0:
            st.subheader(
                f"There is {str(len(list_bests_ais))} IA corresponding to your specifications, here they are in order of the most efficient to the least:",
                anchor=None,
            )
            for i, val_i in enumerate(list_bests_ais):
                st.caption(str(i + 1) + ") " + val_i)
        # If no AI corresponding the the choices
        else:
            st.subheader(
                "There is no AI corresponding to your request, please make other choices in the form", anchor=None
            )
