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
        - set_state : set the session_state.clicked to True
        - show_best_ai
    """

    page_title = "Form Page"
    form_title = "Form"
    page_icon = "📝"

    def __init__(self) -> None:
        st.title(f"{self.page_icon}{self.form_title}")
        st.set_page_config(page_title=self.page_title, page_icon=self.page_icon)
        self.username = check_user_connection()

    @property
    def locked(self) -> bool:
        return st.session_state.get("clicked", False)

    @locked.setter
    def locked(self, value: bool) -> None:
        st.session_state.clicked = value

    def show_question(self, question: dict[str, str], previous_answer: Optional[list] = None) -> list[str]:
        answer = [""]
        if question["question_label"] == "Q_Open":  # TODO : in type Question, change attribute label by type, ...
            answer = self.show_open_question(question, previous_answer)  # TODO:
        elif question["question_label"] == "Q_QCM" or question["question_label"] == "Q_QCM_Bool":
            answer = self.show_qcm_question(question, previous_answer)
        elif question["question_label"] == "Q_QRM":
            answer = self.show_qrm_question(question, previous_answer)
        elif question["question_label"] == "end":  # This is the end (of the form)
            return ["end"]
        else:
            print("Error, question label no recognised")
        if answer == [""]:
            st.session_state.last_form_name = None  # We put the variable to None because we detect that is a new form
            self.locked = False
        return answer

    # TODO : maybe create an other class UI question for each type of question or factory method -> really interesting

    def show_open_question(self, question: dict, previous_answer: Optional[list] = None) -> list[str]:
        if previous_answer is None:  # If it has not to be auto-completed before
            previous_answer = [""]
        # We show the question text area
        answer = str(
            st.text_area(
                label=question["question_text"],
                height=100,
                label_visibility="visible",
                value=previous_answer[0],
                help=question["help_text"],
                disabled=self.locked,
            )
        )
        return [validate_text_input(answer)]

    def show_qcm_question(self, question: dict, previous_answer: Optional[list] = None) -> list[str]:
        options = ["<Select an option>"] + question["answers"]
        # If it has to be auto-completed before
        previous_index = options.index(previous_answer[0]) if previous_answer is not None else 0
        # We show the question selectbox
        answer = str(
            st.selectbox(
                label=question["question_text"],
                options=options,
                index=previous_index,
                help=question["help_text"],
                disabled=self.locked,
            )
        )
        return [""] if answer == "<Select an option>" else [answer]  # TODO: change [""] by None

    def show_qrm_question(self, question: dict, previous_answer: Optional[list] = None) -> list[str]:
        # If it has to be auto-completed before
        default = previous_answer if previous_answer is not None else []
        answers = st.multiselect(
            label=question["question_text"],
            options=question["answers"],
            default=default,
            help=question["help_text"],
            disabled=self.locked,
        )
        return [""] if not answers else answers

    def check_name(self, string: str) -> str:
        dash, char = no_dash_in_my_text(string)
        if dash:
            st.warning(f"""Please don't use the {char} character in your form name""")
            return ""
        return validate_text_input(string)

    def show_form_name_input(self, previous_answer: str = "") -> str:  # TODO: change_name with a VERB
        if previous_answer:
            text = "If you want to change the name of the form, change it here (don't forget to press Enter to validate the name):"
        else:
            text = "Give a name to your form here"
        form_name = st.text_input(text, previous_answer, disabled=self.locked)
        return self.check_name(form_name)

    def check_name_already_taken(self, form_name: str) -> bool:
        if st.session_state.last_form_name != form_name:
            st.warning(
                "You already have a form with this name, please pick an other name or change your previous form in the historic page."
            )
            return True
        return False

    def set_locked(self) -> None:
        self.locked = True

    def show_submission_button(self) -> bool:
        if st.button("Submit", on_click=self.set_locked, disabled=self.locked):
            st.write("Answers saved")
            st.session_state.last_form_name = None
            return True
        return False

    def show_best_ai(self, list_bests_ais: list[str]) -> None:
        """
            Method used to show the n best AI obtained after the user has completed the Form
            The number of AI choosen is based on the nbai wanted by the user and
            the maximum of available AI for the use of the user
            (If there is only 3 AI possible, but the user asked for 5, only 3 will be shown)

        Parameters:
            - list_bests_ais (list): list of the n best AI
        """
        if len(list_bests_ais) > 0:
            st.subheader(
                f"There is {len(list_bests_ais)} IA corresponding to your specifications, here they are in order of the most efficient to the least:",
                anchor=None,
            )
            for index, best_ai in enumerate(list_bests_ais):
                st.caption(f"{index + 1}) {best_ai}")
        # If no AI corresponding the the choices
        else:
            st.subheader(
                "There is no AI corresponding to your request, please make other choices in the form", anchor=None
            )
