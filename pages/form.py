from class_form import Form
import streamlit as st

from decouple import config

FIRST_NODE_ID = '1'
BASE_MODIF_CRYPTED = False

def main():
    st.title("Form")
    if 'username' not in st.session_state or st.session_state.username == "":
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    st.caption("Connected as " + str(username))
    form = Form(
                endpoint = "questions-db.gremlin.cosmos.azure.com",
                database_name = "graphdb",
                container_name = "Form",
                primary_key= config('PRIMARYKEY'),
           )
    
    next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED)
    answers = [answer]
    while next_node_id != 'end' and next_node_id is not None:
        next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted)
        if answer is not None:
            answers.append(answer)

    if next_node_id == 'end':

        print(form.calcul_best_AIs(5, answers))

        if st.button('Submit', on_click=form.save_answers, args=(answers,username)):
            st.write('Answers saved')
            st.write(answers)

if __name__ == "__main__":
    main()  
