"""
File used to show a Form
"""
from typing import Optional, Tuple, Union

import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import (
    Answer,
    AnswersList,
    Form,
    Question,
    Username,
)
from ai_sustainability.utils import check_if_name_ok, sanitize_text_input

EDIT_FORM_TEXT = (
    "If you want to change the name of the form, change it here (don't forget to press Enter to validate the name):"
)
INPUT_FORM_TEXT = "Give a name to your form here"
WARNING_FORM_ALREADY_EXIST = "You already have a form with this name, please pick an other name or change your previous form in the historic page."

END_TYPE = config("END_TYPE")


class FormRender:
    """
    Class used to show a Form in any page

    Property :
        - locked ; used to lock all question of a form, to be sure the user can not edit it after the submission

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - ask_question_user : select with methode use in function of the question label
        - show_open_question :
        - show_qcm_question :
        - show_qrm_question :
        - get_all_questions_and_answers
        - input_form_name_and_check
        - check_name
        - show_input_form_name
        - check_name_already_taken
        - render
        - render_as_text
    """

    def __init__(self, username: Username, app: Application) -> None:
        self.app = app
        self.username = username

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
        elif question.type == END_TYPE:  # This is the end (of the form)
            proposition_end = Answer.create_end_answer()
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
        if previous_answers and len(previous_answers) > 1:
            raise ValueError("A previous Answer of a open question can not have multiples values")
        previous_answer = (
            previous_answers[0]
            if previous_answers
            else Answer(answer_id=question.possible_answers[0].answer_id, text="")
        )
        # We show the question text area
        answer_text = sanitize_text_input(
            str(
                st.text_area(
                    label=question.text,
                    height=100,
                    label_visibility="visible",
                    value=previous_answer.text,
                    help=question.help_text,
                    disabled=self.locked,
                )
            )
        )
        previous_answer.text = answer_text
        return AnswersList([previous_answer]) if answer_text else None

    def show_qcm_question(
        self, question: Question, previous_answers: Optional[AnswersList] = None
    ) -> Optional[AnswersList]:
        if previous_answers and len(previous_answers) > 1:
            raise ValueError("A previous Answer of a QCM question can not have multiples values")
        previous_answer = previous_answers[0] if previous_answers else None
        options = ["<Select an option>"] + [answer.text for answer in question.possible_answers]
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
        for answer in question.possible_answers:
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
            options=[answer.text for answer in question.possible_answers],
            default=previous_answers_text_list,
            help=question.help_text,
            disabled=self.locked,
        )
        if not answers_text_list:
            return None
        list_answers = []
        for answer in question.possible_answers:
            if answer.text in answers_text_list:
                list_answers.append(answer)
        return list_answers

    def get_all_questions_and_answers(self, form: Optional[Form] = None) -> tuple[Form, bool]:
        """
        Function used to show the form to be completed by the user
        """
        if form is None:
            form = Form()
        keep_going = True
        question_number = 0
        while keep_going:  # While we are not in the last question node
            actual_question = self.app.get_next_question(form, question_number)
            previous_answer = (
                None
                if not form.question_list[question_number].choosen_answers
                else form.question_list[question_number].choosen_answers
            )
            question_number += 1
            selected_answer = self.ask_question_user(actual_question, previous_answer)
            if selected_answer is None:
                return form, False
            keep_going = actual_question.type != END_TYPE
            if keep_going:
                form.add_answers(selected_answer, question_number)
        return form, True

    def input_form_name_and_check(self, previous_name: str = "") -> tuple[str, bool]:
        """
        Function used to show a box where the user can give a name to the form and check if the name is incorrect
        """
        form_name = self.show_input_form_name(previous_name=previous_name)
        if not form_name:
            return "", True
        if form_name != previous_name and self.app.form_exist(self.username, form_name):
            if self.check_name_already_taken(self.username):
                return "", True
        return form_name, False

    def check_name(self, form_name: str) -> str:
        dash, char = check_if_name_ok(form_name)
        if dash:
            st.warning(f"Please don't use the {char} character in your form name")
            return ""
        return sanitize_text_input(form_name)

    def show_input_form_name(self, previous_name="") -> str:
        text = EDIT_FORM_TEXT if previous_name else INPUT_FORM_TEXT
        form_name = st.text_input(text, value=previous_name, disabled=self.locked)
        return self.check_name(form_name)

    def check_name_already_taken(self, form_name: str) -> bool:
        if st.session_state.last_form_name != form_name:
            st.warning(WARNING_FORM_ALREADY_EXIST)
            return True
        return False

    def render(self, form: Optional[Form] = None) -> Tuple[Optional[Form], str]:
        form, is_ended = self.get_all_questions_and_answers(form)
        if not is_ended:
            return None, ""
        form_name, form_name_incorrect = self.input_form_name_and_check(form.form_name)
        if form_name_incorrect:
            return None, ""
        return form, form_name

    def render_as_text(self, form: Form) -> None:
        """
        Show a previous answered question with the admin view
        """
        actual_question = 0
        while form.question_list[actual_question].type != END_TYPE:
            answers = ""
            for previous_answer in form.question_list[actual_question].choosen_answers:
                answers += f"{previous_answer.text} <br>"
            st.subheader(f"{form.question_list[actual_question].text} :")
            st.caption(answers, unsafe_allow_html=True)
            actual_question += 1

    def show_best_ai(self, list_bests_ais: Union[list[Tuple[str, float]], list[str]]) -> None:
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
            st.caption(
                f"{index + 1}) {best_ai}" if isinstance(list_bests_ais[0], str) else f"{index + 1}) {best_ai[0]}"
            )

    def show_best_ai_graph(self, list_best_ais: list[Tuple[str, float]]) -> None:
        if list_best_ais:
            labels = [i[0] for i in list_best_ais]
            values = [i[1] for i in list_best_ais]
            fig = go.Figure(
                data=[
                    go.Pie(labels=labels, values=values, hovertemplate="%{label}<br>Score: %{value:.2f}<extra></extra>")
                ]
            )
            st.plotly_chart(fig)
