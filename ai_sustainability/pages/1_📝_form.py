"""
This file is used to show the From page
"""
from ai_sustainability.classes.class_form import FormStreamlit
from ai_sustainability.classes.db_connection import DbConnection

# General variable, used to begin the main() function
FIRST_NODE_ID = "1"
BASE_MODIF_CRYPTED = False
N_BEST_AI = 5


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    # Connection to the online gremlin database via db_connection.py
    database = DbConnection()
    st_form = FormStreamlit(database)
    database.make_connection()
    username = st_form.username
    if not username:
        return

    end = True
    list_answers: list[list[str]] = []
    while end:  # While we are not in the last question node
        dict_question = database.get_one_question(list_answers)
        selected_answer = st_form.show_question(dict_question)
        if not selected_answer[0]:
            return
        if dict_question["question_label"] == "end":
            end = False
        else:
            list_answers.append(selected_answer)

    form_name = st_form.input_form_name()
    if not form_name:
        return
    if database.check_form_exist(username, form_name):
        if st_form.error_name_already_taken(username):
            return

    list_bests_ais = database.calcul_best_ais(N_BEST_AI, list_answers)
    if st_form.show_submission(list_answers):
        st_form.show_best_ai(list_bests_ais)
        database.save_answers(username, form_name, list_answers)
        print(list_answers)


if __name__ == "__main__":
    main()
