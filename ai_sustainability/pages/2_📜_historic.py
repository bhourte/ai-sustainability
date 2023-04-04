"""
This file is used to show the Historic page
"""
import streamlit as st
from decouple import config

from ai_sustainability.class_form import Form

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
    st.set_page_config(page_title="Historic Page", page_icon="📜")
    st.title("📜Historic")
    if (
        "username" not in st.session_state or st.session_state.username == ""
    ):  # User not connected, don't show the historics, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    # Connection to the online gremlin database via class_from.py
    form = Form(
        endpoint="questions-db.gremlin.cosmos.azure.com",
        database_name="graphdb",
        container_name=config("DATABASENAME"),
        primary_key=config("PRIMARYKEY"),
    )
    # Connected as an User
    if username != "Admin":
        st.caption("✅ Connected as " + str(username))

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
        st.caption("🔑 Connected as an Admin")
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


if __name__ == "__main__":
    main()
