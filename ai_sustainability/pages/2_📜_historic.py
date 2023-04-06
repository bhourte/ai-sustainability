"""
This file is used to show the Historic page
"""
from typing import Optional

import streamlit as st
from decouple import config

from ai_sustainability.class_form_old import Form
from ai_sustainability.classes.class_historic import HistoricStreamlit
from ai_sustainability.classes.db_connection import DbConnection

# General variable, used to begin the main() function
FIRST_NODE_ID = "1"
BASE_MODIF_CRYPTED = False
N_BEST_AI = 5


def get_list_result(form: Form, node_answer: str) -> list:
    """
    Specific function used by the "Historic" page to get the list with all the previous answer for a previous form
    Parameters :
        - form (object) : the form create from class_form.py (used to made de link with the gremlin database)
        - node_answer (str) : the 'id' of the node of the first answer

    Return :
        - previous_answers (list) : list of all previous answer contained in the form
    """

    # We create a list with all previous answers
    previous_answers = []
    next_node_id = node_answer
    # we iterate over the full graph
    while next_node_id != "end" and next_node_id is not None:
        node_answer_label = form.run_gremlin_query("g.V('" + str(node_answer) + "').properties('label')")[0]["value"]
        # If we have reach the end :
        if node_answer_label == "end":
            break
        next_node_id = form.run_gremlin_query("g.V('" + str(node_answer) + "').properties('question_id')")[0]["value"]
        panswer = form.run_gremlin_query("g.V('" + str(node_answer) + "').outE().properties('answer')")
        previous_answer = []
        for i in panswer:
            previous_answer.append(i["value"])
        previous_answers.append(previous_answer)
        node_answer = form.run_gremlin_query("g.V('" + str(node_answer) + "').out().properties('id')")[0][
            "value"
        ]  # We go to the next vertice
    return previous_answers


def show_form(form: Form, node_answer: str) -> None:
    """
    Specific function used by the "Historic" page to show the form in the Admin section of the Historic page
    Parameters :
        - form (object) : the form create from class_form.py (used to made de link with the gremlin database)
        - node_answer (str) : the 'id' of the node of the first answer

    Return :
        - None
    """

    next_node_id = None
    list_bests_ais = form.run_gremlin_query("g.V('" + str(node_answer) + "').properties('list_bests_AIs')")[0]["value"]
    while next_node_id != "end":
        node_answer_label = form.run_gremlin_query("g.V('" + str(node_answer) + "').properties('label')")[0]["value"]
        # if we have reach the end
        if node_answer_label == "end":
            break
        question = form.run_gremlin_query("g.V('" + str(node_answer) + "').properties('question')")[0]["value"]
        panswer = form.run_gremlin_query("g.V('" + str(node_answer) + "').outE().properties('answer')")
        answers = ""
        for i in panswer:
            answers += i["value"] + "<br>"
        st.subheader(question + " :")
        st.caption(answers, unsafe_allow_html=True)
        node_answer = form.run_gremlin_query("g.V('" + str(node_answer) + "').out().properties('id')")[0][
            "value"
        ]  # We go to the next vertice
    form.show_best_ai(list_bests_ais)


def main() -> None:
    """
    This is the code used to show the previous form completed by an User
    Different usage if User or Admin
    """

    database = DbConnection()
    st_form = HistoricStreamlit(database)
    username = st_form.username
    if not username:
        return

    # Connection to the online gremlin database via class_from.py
    form = Form(
        endpoint="questions-db.gremlin.cosmos.azure.com",
        database_name="graphdb",
        container_name=config("DATABASENAME"),
        primary_key=config("PRIMARYKEY"),
    )
    # Connected as an User
    if username != "Admin":
        node_answer = form.add_qcm_select_form(username)
        if node_answer is None:  # if none form selected, don't show the rest
            return
        form_name = node_answer.split("-")[-1]
        next_node_id = node_answer

        previous_answers = get_list_result(
            form, node_answer
        )  # get the list with all previous answers contained in the form

        next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED, previous_answers[0])
        label_next_node = form.run_gremlin_query("g.V('" + str(next_node_id) + "').properties('label')")[0]["value"]
        answers = [answer]
        i = 1
        while label_next_node != "end" and next_node_id is not None:
            next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted, previous_answers[i])
            if answer is not None and len(answer) != 0:
                label_next_node = form.run_gremlin_query("g.V('" + str(next_node_id) + "').properties('label')")[0][
                    "value"
                ]
                answers.append(answer)
                if previous_answers[i] is not None and answer[0]["text"] != previous_answers[i][0]:
                    previous_answers = [None] * len(previous_answers)
            i += 1
            if i == len(previous_answers):
                previous_answers.append(None)

        # If the form is not finish, we continue to show it with a new question
        if label_next_node != "end":
            return

        # We ask the user if he want to change the name of his form
        new_form_name = st.text_input("If you want to change the name of the form, change it here:", form_name)
        if new_form_name == "":  # The name can not be empty
            return

        if not form.no_dash_in_my_text(new_form_name):  # No - in the name
            st.warning("The name of the form can't contain a dash.")
            return

        print(form_name)
        print(new_form_name)
        if (
            form.run_gremlin_query("g.V('" + username + "-answer1-" + new_form_name + "')")
            and new_form_name != form_name
        ):
            st.warning(
                "You already have a form with this name, please pick an other name or select it above if you want to change it."
            )
            return

        list_bests_ais = form.calcul_best_ais(N_BEST_AI, answers)  # get the N best AI (5 for now)
        form.show_best_ai(list_bests_ais)  # We show the N best AI to the user (5 for now)
        if st.button(
            "Save Change",
            on_click=form.change_answers,
            args=(answers, username, list_bests_ais, form_name, new_form_name),
        ):
            st.session_state.clicked = False  # Put to False to be sure it does not bug in the Form page
            print("best AIs : " + str(list_bests_ais))
            st.write("Change saved")
            st.write(answers)

    # Connected as an Admin
    else:
        all_user = ["<Select an User>"] + form.run_gremlin_query("g.V().haslabel('user')")
        i = 1
        for i in range(1, len(all_user)):
            all_user[i] = all_user[i]["id"]

        # The admin select an user
        user = st.selectbox(label="Select an user", options=all_user)
        if user == "<Select an User>":
            return

        all_form = ["<Select a Form>"] + form.run_gremlin_query("g.V('" + str(user) + "').out().haslabel('Answer')")
        # Shaping of the texts
        for i in range(1, len(all_form)):
            all_form[i] = all_form[i]["id"].split("-")[-1]
            i += 1

        # The admin select a form of the choosen user
        form_name = str(st.selectbox(label="Select a Form", options=all_form))
        if form_name == "<Select a Form>":
            return

        first_node = str(user) + "-answer1-" + str(form_name)
        show_form(form, first_node)  # We show the form below the selection boxes


def main_new() -> None:
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

    previous_answers: list[list[str]] = [
        ["Test"],
        ["No"],
        ["Text"],
        ["Classify texts"],
        ["Higher speed"],
        ["No"],
        ["Child"],
        ["Tables"],
    ]
    list_answered_form = ["form1", "form2"]

    # Connected as an User
    if username != "Admin":
        # list_answered_form = database.get_all_forms(username)
        selected_form = st_historic.show_choice_form(list_answered_form)
        if not selected_form:  # if none form selected, don't show the rest
            return
        form_name = selected_form.rsplit("-", maxsplit=1)[-1]

        # get the list with all previous answers contained in the form
        # previous_answers = database.get_list_answers(selected_form)

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
        if database.check_form_exist(username, new_form_name):
            if st_historic.error_name_already_taken(username):
                return
        list_bests_ais = database.calcul_best_ais(N_BEST_AI, list_answers)
        if st_historic.show_submission(list_answers):
            st_historic.show_best_ai(list_bests_ais)
            # database.change_answers(list_answers, username, form_name, new_form_name)
            print(list_answers)

    # Connected as an Admin
    else:
        list_username = database.get_all_users()

        # The admin select an user
        choosen_user = st_historic.show_choice_user(list_username)
        if not choosen_user:  # if none user selected, don't show the rest
            return

        # The admin select a form of the choosen user
        # list_answered_form = database.get_all_forms(choosen_user)
        selected_form = st_historic.show_choice_form(list_answered_form, admin=True)
        if not selected_form:  # if none form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        # previous_answers = database.get_list_answers(selected_form)

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


if __name__ == "__main__":
    main_new()
