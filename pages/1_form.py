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
        if form_name != "":
            txt_ok = form.no_dash_in_my_text(form_name)
            if txt_ok:
                list_bests_AIs = form.calcul_best_AIs(5, answers)
                if st.button('Submit', on_click=form.save_answers, args=(answers,username,list_bests_AIs,form_name)):
                    print("best AIs : " + str(list_bests_AIs))
                    st.write('Answers saved')
                    form.show_best_AI(list_bests_AIs)
                    st.write(answers)
            else:
                st.warning("Please don't use dash in your form name")

if __name__ == "__main__":
    main()  
