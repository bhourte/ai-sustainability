from class_form import Form
import streamlit as st

FIRST_NODE_ID = '1'
BASE_MODIF_CRYPTED = False

def main():

    form = Form(
                endpoint = "questions-db.gremlin.cosmos.azure.com",
                database_name = "graphdb",
                container_name = "Persons",
                primary_key=PRIMARYKEY,
           )
    
    next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED)
    answers = [answer]
    while next_node_id != 'end' and next_node_id is not None:
        next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted)
        if answer is not None:
            answers.append(answer)

    if next_node_id == 'end':
        st.write(answers)
        if st.button('Submit', on_click=form.save_answers, args=(answers,'Arnauld')):
            st.write('Answers saved')


if __name__ == "__main__":
    main()  
