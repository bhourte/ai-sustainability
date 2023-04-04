"""
This file is used to show the From page
"""
import streamlit as st
from decouple import config

from ai_sustainability.class_form import Form
from ai_sustainability.utils import checkcheck_username

# General variable, used to begin the main() function
FIRST_NODE_ID = "1"
BASE_MODIF_CRYPTED = False
N_BEST_AI = 5


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    st.set_page_config(page_title="Form Page", page_icon="📝")
    st.title("📝Form")
    if (
        "username" not in st.session_state or st.session_state.username == ""
    ):  # User not connected, don't show the form, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return
    username = st.session_state.username
    st.caption("✅ Connected as " + str(username))
    # Connection to the online gremlin database via class_from.py
    form = Form(
        endpoint="questions-db.gremlin.cosmos.azure.com",
        database_name="graphdb",
        container_name=config("DATABASENAME"),
        primary_key=config("PRIMARYKEY"),
    )

    # We show the first question here, in order to get the id of the next node
    next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED)
    answers = [answer]  # List of all aswers
    # And we iterate from the id of the first node to the last
    while next_node_id != "end" and next_node_id is not None:
        next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted)
        if answer is not None:
            answers.append(answer)

    # If the form is not finish and simply wait the user to put answer, we continue to show it with a the last question
    if next_node_id != "end":
        st.session_state.last_form_name = None  # We put the variable to None because we detect that is a new form
        st.session_state.clicked = False
        return

    # If the form is finish, we ask the user a name for the form, we calculate the N best AIs and we save it all
    form_name = st.text_input("Give a name to your form here")
    if form_name == "":  # If the name is empty, we don't go further, we wait the user to fill it
        return
    txt_ok = form.no_dash_in_my_text(form_name)
    if not txt_ok:  # No - in the text
        st.warning("Please don't use dash in your form name")
        return

    # We check if the form name already exist in the database
    if (
        form.run_gremlin_query("g.V('" + username + "-answer1-" + form_name + "')")
        and st.session_state.last_form_name != form_name
    ):
        st.warning(
            "You already have a form with this name, please pick an other name or change your previous form in the historic page."
        )
        return None

    list_bests_ais = form.calcul_best_ais(N_BEST_AI, answers)
    # First time passing here, we show the "submit" button to save answers
    if not st.session_state.clicked:
        st.session_state.last_form_name = form_name
        st.button("Submit", on_click=form.save_answers, args=(answers, username, list_bests_ais, form_name))
    # Second time passing here, we show the result
    else:
        st.write("Answers saved")
        form.show_best_ai(list_bests_ais)  # We show de N best AI (5 by default)
        st.write(answers)
        st.session_state.last_form_name = None
        st.session_state.clicked = False


if __name__ == "__main__":
    main()
