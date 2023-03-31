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
                container_name = config('DATABASENAME'),
                primary_key= config('PRIMARYKEY'),
           )
    
    next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED)
    answers = [answer]
    while next_node_id != 'end' and next_node_id is not None:
        next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted)
        if answer is not None:
            answers.append(answer)

    if next_node_id == 'end':

        form_name = st.text_input("Give a name to your form here")
        print('form_name = ' + str(form_name))
        if form_name != "":
            if st.button('Submit', on_click=form.save_answers, args=(answers,username,form_name)) and form_name != "":
                print(form.calcul_best_AIs(5, answers))
                st.write('Answers saved')
                st.write(answers)

if __name__ == "__main__":
    main()  
