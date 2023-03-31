import streamlit as st
from class_form import Form
from decouple import config


FIRST_NODE_ID = '1'
BASE_MODIF_CRYPTED = False

def get_list_result(_form, node_answer, next_node_id):

    # We create a list with all previous answers
    previous_answers = []
    while next_node_id != 'end' and next_node_id is not None:
        node_answer_label = _form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('label')")[0]['value']
        if node_answer_label == 'end':
            break
        next_node_id = _form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('question_id')")[0]['value']
        panswer = _form.run_gremlin_query("g.V('"+str(node_answer)+"').outE().properties('answer')")
        previous_answer = []
        for i in panswer:
            previous_answer.append(i['value'])
        previous_answers.append(previous_answer)
        
        node_answer = _form.run_gremlin_query("g.V('"+str(node_answer)+"').out().properties('id')")[0]['value']  # We go to the next vertice
    return previous_answers

def main():
    st.title("Historic")
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

    node_answer = form.add_qcm_select_form(username)
    if node_answer == None:  # if none form selected, don't show the rest
        return None
    form_name = node_answer.split("-")[-1]
    next_node_id = node_answer

    previous_answers = get_list_result(form, node_answer, next_node_id)

    next_node_id, answer, modif_crypted = form.add_question(FIRST_NODE_ID, BASE_MODIF_CRYPTED, previous_answers[0])
    label_next_node = form.run_gremlin_query("g.V('"+str(next_node_id)+"').properties('label')")[0]['value']
    answers = [answer]
    i = 1
    while label_next_node != 'end' and next_node_id is not None:
        next_node_id, answer, modif_crypted = form.add_question(next_node_id, modif_crypted, previous_answers[i])
        if answer is not None and len(answer) != 0:
            label_next_node = form.run_gremlin_query("g.V('"+str(next_node_id)+"').properties('label')")[0]['value']
            answers.append(answer)
            if previous_answers[i] != None and answer[0]['text'] != previous_answers[i][0]:
                previous_answers = [None] * len(previous_answers)
        i += 1
        if i == len(previous_answers):
            previous_answers.append(None)

    if label_next_node == 'end':

        print("best AIs : " + str(form.calcul_best_AIs(5, answers)))

        if st.button('Save Change', on_click=form.change_answers, args=(answers,username, form_name)):
            st.write('Change saved')
            st.write(answers)


if __name__ == "__main__":
      main()