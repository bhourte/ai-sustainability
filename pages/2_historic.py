import streamlit as st
from class_form import Form
from decouple import config


FIRST_NODE_ID = '1'
BASE_MODIF_CRYPTED = False

def get_list_result(form, node_answer, next_node_id):

    # We create a list with all previous answers
    previous_answers = []
    while next_node_id != 'end' and next_node_id is not None:
        node_answer_label = form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('label')")[0]['value']
        if node_answer_label == 'end':
            break
        next_node_id = form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('question_id')")[0]['value']
        panswer = form.run_gremlin_query("g.V('"+str(node_answer)+"').outE().properties('answer')")
        previous_answer = []
        for i in panswer:
            previous_answer.append(i['value'])
        previous_answers.append(previous_answer)
        node_answer = form.run_gremlin_query("g.V('"+str(node_answer)+"').out().properties('id')")[0]['value']  # We go to the next vertice
    return previous_answers

def show_form(form, node_answer):
    next_node_id = None
    list_bests_AIs = form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('list_bests_AIs')")[0]['value']
    while next_node_id != 'end':
        node_answer_label = form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('label')")[0]['value']
        if node_answer_label == 'end':
            break
        question = form.run_gremlin_query("g.V('"+str(node_answer)+"').properties('question')")[0]['value']
        panswer = form.run_gremlin_query("g.V('"+str(node_answer)+"').outE().properties('answer')")
        answers = ""
        for i in panswer:
            answers += i['value'] + "<br>"
        st.subheader(question + " :")
        st.caption(answers, unsafe_allow_html=True)
        node_answer = form.run_gremlin_query("g.V('"+str(node_answer)+"').out().properties('id')")[0]['value']  # We go to the next vertice
    form.show_best_AI(list_bests_AIs)
    return None

def main():
    st.title("Historic")
    if 'username' not in st.session_state or st.session_state.username == "":
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    form = Form(
                endpoint = "questions-db.gremlin.cosmos.azure.com",
                database_name = "graphdb",
                container_name = config('DATABASENAME'),
                primary_key= config('PRIMARYKEY'),
            )
    if username != 'Admin':  # Connected as an User
        st.caption("Connected as " + str(username))

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

            new_form_name = st.text_input("If you want to change the name of the form, change it here:", form_name)
            if new_form_name != "":
                list_bests_AIs = form.calcul_best_AIs(5, answers)
                form.show_best_AI(list_bests_AIs)
                if st.button('Save Change', on_click=form.change_answers, args=(answers,username,list_bests_AIs,form_name,new_form_name)):
                    print("best AIs : " + str(list_bests_AIs))
                    st.write('Change saved')
                    st.write(answers)


    else:  # Connected as an Admin
        st.caption("Connected as an Admin")
        all_user = ["<Select an User>"] + form.run_gremlin_query("g.V().haslabel('user')")
        i = 1
        while i < len(all_user):
            all_user[i] = all_user[i]['id']
            i += 1
        user = st.selectbox(label="Select an user", options=all_user)
        if user != "<Select an User>":
            all_form = ["<Select a Form>"] + form.run_gremlin_query("g.V('"+str(user)+"').out().haslabel('Answer')")
            i = 1
            while i < len(all_form):
                all_form[i] = all_form[i]['id'].split("-")[-1]
                i += 1
            form_name = st.selectbox(label="Select a Form", options=all_form)
            if form_name != "<Select a Form>":
                first_node = str(user) + "-answer1-" + str(form_name)
                show_form(form, first_node)


if __name__ == "__main__":
    main()
