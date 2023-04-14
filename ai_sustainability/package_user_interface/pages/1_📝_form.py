"""
This file is used to show the From page
"""
from decouple import config

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import FormAnswers, Username
from ai_sustainability.package_user_interface.classes.class_form import FormStreamlit


def get_all_questions_and_answers(st_form: FormStreamlit, app: Application) -> tuple[FormAnswers, bool]:
    """
    Function used to show the form to be completed by the user
    """
    keep_going = True
    list_answers: FormAnswers = []
    while keep_going:  # While we are not in the last question node
        actuel_question = app.get_next_question(list_answers)
        selected_answer = st_form.ask_question_user(actuel_question)
        if selected_answer is None:
            return list_answers, False
        keep_going = actuel_question.type != "end"
        if keep_going:
            list_answers.append(selected_answer)
    return list_answers, True


def input_form_name_and_check(username: Username, st_form: FormStreamlit, app: Application) -> tuple[str, bool]:
    """
    Function used to show a box where the user can give a name to the form and check if the name is incorrect
    """
    form_name = st_form.show_input_form_name(previous_answer="")
    if not form_name:
        return "", True
    if app.check_form_exist(username, form_name):
        if st_form.check_name_already_taken(username):
            return "", True
    return form_name, False


# TODO put the 2 function in class_form


def main() -> None:
    # TODO put all in class_form
    """
    This is the code used to show the form and used by the user to fill it
    """
    # Connection to the online gremlin database via db_connection.py
    st_form = FormStreamlit()
    app = Application()
    n_best_ai = int(config("NBEST_AI"))  # TODO put that in Application.py

    username = st_form.username
    if not username:
        return

    list_answers, is_ended = get_all_questions_and_answers(st_form, app)
    if not is_ended:
        return

    form_name, form_name_incorrect = input_form_name_and_check(username, st_form, app)
    if form_name_incorrect:
        return

    list_bests_ais = app.calcul_best_ais(n_best_ai, list_answers)
    if st_form.show_submission_button():  # show the submission button and return True if it's clicked
        st_form.show_best_ai(list_bests_ais)
        app.save_answers(username, form_name, list_answers, list_bests_ais)


if __name__ == "__main__":
    main()
