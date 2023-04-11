"""
This file is used to show the From page
"""
from ai_sustainability.classes.class_form import FormStreamlit
from ai_sustainability.database.db_connection import DbConnection

# General variable, used to begin the main() function
N_BEST_AI = 5  # TODO : put this in a config file or env variable


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    # Connection to the online gremlin database via db_connection.py
    database = DbConnection()
    st_form = FormStreamlit()
    database.make_connection()
    username = st_form.username
    if not username:
        return

    end = False  # TODO : change this variable name in continue = True
    list_answers: list[list[str]] = []
    while not end:  # While we are not in the last question node
        dict_question = database.get_one_question(list_answers)
        selected_answer = st_form.show_question(dict_question)  # TODO : change function name ask_question_user
        if not selected_answer[0]:
            return
        end = dict_question["question_label"] == "end"
        if not end:
            list_answers.append(
                selected_answer
            )  # TODO : all this block (25 to 34) can be a function get_all_questions_and_answers return 2: answers and end (bool)

    form_name = st_form.show_form_name_input(previous_answer="")
    if not form_name:
        return
    if database.check_form_exist(username, form_name):
        if st_form.check_name_already_taken(username):
            return  # TODO : function (36, 41) can be a function check_form_name_exist return bool

    list_bests_ais = database.calcul_best_ais(N_BEST_AI, list_answers)
    if st_form.show_submission_button():  # show the submission button and return True if it's clicked
        st_form.show_best_ai(list_bests_ais)
        database.save_answers(username, form_name, list_answers)  # TODO : this can be a function


if __name__ == "__main__":
    main()
