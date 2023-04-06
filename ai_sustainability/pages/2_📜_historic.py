"""
This file is used to show the Historic page
"""
from ai_sustainability.classes.class_historic import HistoricStreamlit
from ai_sustainability.classes.db_connection import DbConnection

# General variable, used to begin the main() function
FIRST_NODE_ID = "1"
BASE_MODIF_CRYPTED = False
N_BEST_AI = 5


def main() -> None:
    """
    This is the code used to show the previous form completed by an User
    Different usage if User or Admin
    """

    database = DbConnection()
    st_historic = HistoricStreamlit(database)
    database.make_connection()
    username = st_historic.username
    if not username:
        return

    # Connected as an User
    if username != "Admin":
        list_answered_form = database.get_all_forms(username)
        selected_form = st_historic.show_choice_form(list_answered_form)
        if not selected_form:  # if none form selected, don't show the rest
            return
        form_name = selected_form.rsplit("-", maxsplit=1)[-1]

        # get the list with all previous answers contained in the form
        previous_answers = database.get_list_answers(selected_form)

        end = True
        list_answers: list[list[str]] = []
        previous_answers += [["end"]]
        i = 0
        while end:
            dict_question = database.get_one_question(list_answers)
            selected_answer = st_historic.show_question(dict_question, previous_answers[len(list_answers)])
            if not selected_answer[0]:
                return
            if dict_question["question_label"] == "end":
                end = False
            else:
                list_answers.append(selected_answer)
                if previous_answers[0] is not None and list_answers[i] != previous_answers[i]:
                    previous_answers = [None] * len(previous_answers)
            i += 1
            if i >= len(previous_answers):
                previous_answers.append(None)

        # If the form is not finish, we continue to show it with a new question
        if dict_question["question_label"] != "end":
            return

        new_form_name = st_historic.input_form_name(form_name)
        if not new_form_name:
            return
        if database.check_form_exist(username, new_form_name) and new_form_name != form_name:
            if st_historic.error_name_already_taken(username):
                return
        list_bests_ais = database.calcul_best_ais(N_BEST_AI, list_answers)
        st_historic.show_best_ai(list_bests_ais)
        if st_historic.show_submission(list_answers):
            database.change_answers(list_answers, username, form_name, new_form_name)
            print(list_answers)

    # Connected as an Admin
    else:
        list_username = database.get_all_users()

        # The admin select an user
        choosen_user = st_historic.show_choice_user(list_username)
        if not choosen_user:  # if none user selected, don't show the rest
            return

        # The admin select a form of the choosen user
        list_answered_form = database.get_all_forms(choosen_user)
        selected_form = st_historic.show_choice_form(list_answered_form, is_admin=True)
        if not selected_form:  # if none form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        previous_answers = database.get_list_answers(selected_form)

        end = True
        previous_answers += [["end"]]
        i = 0
        while end:
            list_answers = previous_answers[:i]
            dict_question = database.get_one_question(list_answers)
            st_historic.show_question_as_admin(dict_question, previous_answers[i])
            if dict_question["question_label"] == "end":
                end = False
            i += 1
        list_bests_ais = database.calcul_best_ais(N_BEST_AI, previous_answers[:-1])
        st_historic.show_best_ai(list_bests_ais)


if __name__ == "__main__":
    main()
