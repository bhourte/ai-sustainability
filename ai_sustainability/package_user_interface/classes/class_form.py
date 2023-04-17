"""
Class which contains the form composed of the different questions/answers
Streamlit class
"""
from typing import Optional

import streamlit as st

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import (
    Answer,
    AnswersList,
    Form,
    Question,
    Username,
)
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
)
from ai_sustainability.utils import check_if_name_ok, sanitize_text_input

EDIT_FORM_TEXT = (
    "If you want to change the name of the form, change it here (don't forget to press Enter to validate the name):"
)
INPUT_FORM_TEXT = "Give a name to your form here"
WARNING_FORM_ALREADY_EXIST = "You already have a form with this name, please pick an other name or change your previous form in the historic page."


class FormStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_question : select with methode use in function of the question label
        - show_open_question : show a Q_open question
        - show_qcm_question : show a Q_QCM and Q_QCM_Bool question
        - show_qrm_question : show a Q_QRM question
        - get_proposition_list : return a list[str] with all proposition of a question
        - check_name
        - input_form_name
        - error_name_already_taken
        - show_submission_button
        - set_locked : lock all the question of the form
        - show_best_ai
        - get_all_questions_and_answers
        - input_form_name_and_check
    """

    def __init__(self, app: Application) -> None:
        self.app = app
        self.username = check_user_connection()

    @property
    def locked(self) -> bool:
        return st.session_state.get("clicked", False)

    @locked.setter
    def locked(self, value: bool) -> None:
        st.session_state.clicked = value

    def ask_question_user(
        self, question: Question, previous_answers: Optional[AnswersList] = None
    ) -> Optional[AnswersList]:
        answers: Optional[AnswersList] = AnswersList([])
        if question.type == "Q_Open":
            answers = self.show_open_question(question, previous_answers)
        elif question.type in ("Q_QCM", "Q_QCM_Bool"):
            answers = self.show_qcm_question(question, previous_answers)
        elif question.type == "Q_QRM":
            answers = self.show_qrm_question(question, previous_answers)
        elif question.type == "end":  # This is the end (of the form)
            proposition_end = Answer(
                answer_id="end", text="end", help_text="", modif_crypted=False, list_coef=[]
            )  # TODO put this in a function
            return AnswersList([proposition_end])
        else:
            print("Error, question label no recognised")
        if not answers:
            st.session_state.last_form_name = None  # We put the variable to None because we detect that is a new form
            self.locked = False
        return answers

    def show_open_question(
        self, question: Question, previous_answers: Optional[AnswersList] = None
    ) -> Optional[AnswersList]:
        if previous_answers is None:  # If it has not to be auto-completed before
            previous_answers = [Answer(answer_id=question.answers[0].answer_id, text="")]
        # We show the question text area
        answer_text = sanitize_text_input(
            str(
                st.text_area(
                    label=question.text,
                    height=100,
                    label_visibility="visible",
                    value=previous_answers[0].text,
                    help=question.help_text,
                    disabled=self.locked,
                )
            )
        )
        previous_answers[0].text = answer_text
        return previous_answers if answer_text else None

    def show_qcm_question(
        self, question: Question, previous_answers: Optional[AnswersList] = None
    ) -> Optional[AnswersList]:
        previous_answer = (
            previous_answers[0] if previous_answers else None
        )  # TODO do the same for open_question + check if more than one elmt -> raise ValueError
        options = ["<Select an option>"] + self.get_answers_text_list(question)
        # If it has to be auto-completed before
        previous_index = options.index(previous_answer.text) if previous_answer is not None else 0
        # We show the question selectbox
        selected_answer_text = str(
            st.selectbox(
                label=question.text,
                options=options,
                index=previous_index,
                help=question.help_text,
                disabled=self.locked,
            )
        )
        if selected_answer_text == "<Select an option>":
            return None
        for answer in question.answers:
            if answer.text == selected_answer_text:
                return AnswersList([answer])
        raise RuntimeError("A non-existing answer can not be selected.")

    def show_qrm_question(
        self, question: Question, previous_answers: Optional[AnswersList] = None
    ) -> Optional[AnswersList]:
        # If it has to be auto-completed before
        previous_answers_text_list = [previous_answer.text for previous_answer in previous_answers or []]
        answers_text_list = st.multiselect(
            label=question.text,
            options=self.get_answers_text_list(question),
            default=previous_answers_text_list,
            help=question.help_text,
            disabled=self.locked,
        )
        if not answers_text_list:
            return None
        list_answers = []
        for answer in question.answers:
            if answer.text in answers_text_list:
                list_answers.append(answer)
        return list_answers

    def get_answers_text_list(self, question: Question) -> list[str]:
        return [answer.text for answer in question.answers]

    def check_name(self, form_name: str) -> str:
        dash, char = check_if_name_ok(form_name)
        if dash:
            st.warning(f"Please don't use the {char} character in your form name")
            return ""
        return sanitize_text_input(form_name)

    def show_input_form_name(self, previous_answer="") -> str:
        text = EDIT_FORM_TEXT if previous_answer else INPUT_FORM_TEXT
        form_name = st.text_input(text, previous_answer, disabled=self.locked)
        return self.check_name(form_name)

    def check_name_already_taken(self, form_name: str) -> bool:
        if st.session_state.last_form_name != form_name:
            st.warning(WARNING_FORM_ALREADY_EXIST)
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
        if not list_bests_ais:  # If no AI corresponding the the choices
            st.subheader(
                "There is no AI corresponding to your request, please make other choices in the form", anchor=None
            )
            return

        st.subheader(
            f"There is {len(list_bests_ais)} IA corresponding to your specifications, here they are in order of the most efficient to the least:",
            anchor=None,
        )
        for index, best_ai in enumerate(list_bests_ais):
            st.caption(f"{index + 1}) {best_ai}")

    def get_all_questions_and_answers(self, form: Optional[Form] = None) -> tuple[Form, bool]:
        """
        Function used to show the form to be completed by the user
        """
        print("ICIIIIIIIIIIIIIIIIIIIIII   1")
        if form is None:
            form = Form()
        keep_going = True
        question_number = 0
        while keep_going:  # While we are not in the last question node
            print("ICIIIIIIIIIIIIIIIIIIIIII   2")
            actual_question = self.app.get_next_question(form, question_number)
            previous_answer = (
                None
                if not form.question_list[question_number].answers_choosen
                else form.question_list[question_number].answers_choosen
            )
            print("ICIIIIIIIIIIIIIIIIIIIIII   3")
            question_number += 1
            selected_answer = self.ask_question_user(actual_question, previous_answer)
            if selected_answer is None:
                return form, False
            keep_going = actual_question.type != "end"
            if keep_going:
                form.add_answers(selected_answer, question_number)
            print("ICIIIIIIIIIIIIIIIIIIIIII   4")
        return form, True

    def input_form_name_and_check(self, previous_name: str = "") -> tuple[str, bool]:
        """
        Function used to show a box where the user can give a name to the form and check if the name is incorrect
        """
        form_name = self.show_input_form_name(previous_answer=previous_name)
        if not form_name:
            return "", True
        if self.app.check_form_exist(self.username, form_name):
            if self.check_name_already_taken(self.username):
                return "", True
        return form_name, False

    def render(self) -> None:
        form, is_ended = self.get_all_questions_and_answers()
        if not is_ended:
            return
        form_name, form_name_incorrect = self.input_form_name_and_check()
        if form_name_incorrect:
            return
        form.set_name(form_name)
        form.set_username(self.username)

        list_bests_ais = self.app.calcul_best_ais(form)
        if self.show_submission_button():  # show the submission button and return True if it's clicked
            self.show_best_ai(list_bests_ais)
            self.app.save_answers(form, list_bests_ais)
