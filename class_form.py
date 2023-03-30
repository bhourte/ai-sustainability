import math
import heapq
import numpy as np
import streamlit as st
from gremlin_python import statics
from gremlin_python.driver import client, serializer

statics.load_statics(globals())

@st.cache_resource
def connect(endpoint, database_name, container_name, primary_key):
        return client.Client(
            'wss://' + endpoint + ':443/', 'g',
            username="/dbs/" + database_name + "/colls/" + container_name,
            password=primary_key,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

class Form:
    
    def __init__(self, endpoint, database_name, container_name, primary_key):
        self.gremlin_client = connect(endpoint, database_name, container_name, primary_key)
    
    def run_gremlin_query(self, query):
        """
        Run a gremlin query
        
        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")
        """
        run = self.gremlin_client.submit(query).all()
        result = run.result()
        return result

    def close(self):
        """
        Close the connection to the database, must be called at the end of the program
        """
        self.gremlin_client.close()
    
    def add_question(self, node_id, modif_crypted):
        """
        Add question from db to form
        """
        q_type = self.run_gremlin_query("g.V('"+node_id+"').label()")
        if q_type[0] == "Q_Open":
            next_node_id, answer, modif_crypted = self.add_open_question(node_id, modif_crypted)
        elif q_type[0] == "Q_QCM":
            next_node_id, answer, modif_crypted = self.add_qcm_question(node_id, modif_crypted)
        elif q_type[0] == "Q_QRM":
            next_node_id, answer, modif_crypted = self.add_qrm_question(node_id, modif_crypted)
        elif q_type[0] == "Q_QCM_Bool":
            next_node_id, answer, modif_crypted = self.add_qcm_bool_question(node_id, modif_crypted)
        elif q_type[0] == "end":
            next_node_id = "end"
            answer = None
        else:
            print("Error: unknown question type")
        return next_node_id, answer, modif_crypted
    
    def add_open_question(self, node_id, modif_crypted):
        """
        Add open question from db to form
        """
        question = self.get_text_question(node_id)
        next_node_id = self.run_gremlin_query("g.V('"+node_id+"').outE().inV().id()")[0]
        answer = st.text_area(label=question, height=100,label_visibility="visible")
        if not answer:
            answer = None
            next_node_id = None
        answer = [{
            "text": answer,
            "id": self.run_gremlin_query("g.V('"+node_id+"').outE().id()")[0],
        }]
        return next_node_id, answer, modif_crypted
    
    def add_qcm_question(self, node_id, modif_crypted):
        """
        Add qcm question from db to form
        """
        question = self.get_text_question(node_id)
        options = ['<Select an option>']
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        answer = st.selectbox(label=question, options=options, index=0)
        if answer == '<Select an option>':
            answer = None
            next_node_id = None
        else:
            index = propositions.index(answer)
            next_node_id = self.run_gremlin_query("g.E('"+props_ids[index]+"').inV().id()")[0]
            text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
            answer = [{"id": props_ids[index], 'text': text['value']}]
        return next_node_id, answer, modif_crypted

    def add_qrm_question(self, node_id, modif_crypted):
        """
        Add qrm question from db to form
        """
        question = self.get_text_question(node_id)
        options = []
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        answers = st.multiselect(label=question, options=options, default=None)
        answers_returned = []
        if answers == []:
            answers = None
            next_node_id = None
            
        else:
            next_node_id = self.run_gremlin_query("g.V('"+node_id+"').outE().inV().id()")[0]
            for answer in answers:
                index = propositions.index(answer)
                text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
                answers_returned.append({'id': props_ids[index], 'text': text['value']})
        return next_node_id, answers_returned, modif_crypted
    
    def add_qcm_bool_question(self, node_id, modif_crypted):
        """
        Add qcm bool question from db to form
        """
        question = self.get_text_question(node_id)
        options = ['<Select an option>']
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        answer = st.selectbox(label=question, options=options, index=0)
        if answer == '<Select an option>':
            answer = None
            next_node_id = None
        else:
            index = propositions.index(answer)
            next_node_id = self.run_gremlin_query("g.E('"+props_ids[index]+"').inV().id()")[0]
            text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
            modif_crypted = answer == 'Yes'
            answer = [{"id": props_ids[index], 'text': text['value']}]
        return next_node_id, answer, modif_crypted
    
    def get_text_question(self, node_id):
        """
        Get text of a question
        """
        question = self.run_gremlin_query("g.V('"+node_id+"').properties('text').value()")[0]
        return question

    def get_propositions_of_question(self, node_id, modif_crypted):
        """
        Get propositions of a question
        """
        propositions = []
        props_ids = []
        if modif_crypted:
            for edges in self.run_gremlin_query("g.V('"+node_id+"').outE().id()"):
                if self.run_gremlin_query("g.E('"+edges+"').properties('modif_crypted').value()")[0] == 'false':
                    props_ids.append(edges)
                    propositions.append(self.run_gremlin_query("g.E('"+edges+"').properties('text').value()")[0])
        else:
            propositions = self.run_gremlin_query("g.V('"+node_id+"').outE().properties('text').value()")
            props_ids = self.run_gremlin_query("g.V('"+node_id+"').outE().id()")
        
        return propositions, props_ids
    
    def get_weight(self, edge_id):
        """
            Get the list_coef from the edge with edge_id id
        """
        list_weight = self.run_gremlin_query("g.E('"+edge_id+"').properties('list_coef').value()")[0].split(", ")
        i = 0
        while i < len(list_weight):
            list_weight[i] = float(list_weight[i])
            i += 1
        return list_weight
    
    def calcul_best_AIs(self, nbAI, answers):
        """
            Return the nbAI best AIs from a list of answers
        """
        list_AI = self.run_gremlin_query("g.V('1').properties('list_AI')")[0]['value'].split(",")
        coef_AI = [1] * len(list_AI)
        i = 0
        while i < len(answers):
            j = 0
            while j <len(answers[i]):
                list_coef = self.get_weight(answers[i][j]["id"])
                coef_AI = np.multiply(coef_AI, list_coef)
                j += 1
            i += 1
        # We put all NaN value to -1
        i = 0
        while i < len(coef_AI):
            if coef_AI[i] != coef_AI[i]:  # if a NaN value is encounter, we put it to -1
                coef_AI[i] = -1
            i += 1
        best = list(heapq.nlargest(nbAI, np.array(coef_AI)))
        # We put the nbAI best AI in list_bests_AIs
        list_bests_AIs = []
        i = 0
        while i < nbAI:
            if best[i] > 0:
                index = list(coef_AI).index(best[i])
                list_bests_AIs.append(list_AI[index])
            i += 1
        self.show_best_AI(list_bests_AIs)
        return list_bests_AIs
    
    def show_best_AI(self, list_bests_AIs):
        """
            Method used to show the n best AI obtained after the user has completed the Form
            The number of AI choosen is based on the nbAI wanted by the user and the maximum of available AI for the use of the user
            (If there is only 3 AI possible, but the user asked for 5, only 3 will be shown)
        """
        if len(list_bests_AIs) > 0:
            st.subheader("There is "+str(len(list_bests_AIs))+" IA corresponding to your specifications, here they are in order of the most efficient to the least:", anchor=None)
            i = 0
            while i < len(list_bests_AIs):
                st.caption(str(i+1)+") "+list_bests_AIs[i])
                i += 1
        else:
            st.subheader("There is no AI corresponding to your request, please make other choices in the form", anchor=None)
        return None

    def save_answers(self, answers, username):
        """
        Save answers in db
        Answers = list of list of dict {id: , text:}
        """
        username_exist = self.run_gremlin_query("g.V('"+username+"').id()")
        if not username_exist:
            self.run_gremlin_query("g.addV('user').property('partitionKey', 'Answer').property('id', '"+username+"')")
            nb_form = 1

        else : 
            # count number of edges from user
            nb_edges = len(self.run_gremlin_query("g.V('"+username+"').outE().hasLabel('Answer').id()"))
            nb_form = nb_edges+1
        nb_form = "-form"+str(nb_form)

        for list_answer in answers:
            for dict_answer in list_answer:
                actual_node = self.run_gremlin_query("g.E('"+str(dict_answer['id'])+"').outV()")[0]
                next_question_node = self.run_gremlin_query("g.E('"+dict_answer['id']+"').inV()")[0]

                new_node_id = username+'-'+'answer'+actual_node['id']+nb_form
                next_new_node_id = username+'-'+'answer'+next_question_node['id']+nb_form

                new_node_id_exist = self.run_gremlin_query("g.V('"+new_node_id+"').id()")
                next_new_node_id_exist = self.run_gremlin_query("g.V('"+next_new_node_id+"').id()")

                if not new_node_id_exist:
                    self.run_gremlin_query("g.addV('Answer').property('partitionKey', 'Answer').property('id', '"+new_node_id+"').property('question', '"+actual_node['properties']['text'][0]['value']+"').property('question_id', '"+actual_node['id']+"')")

                if not next_new_node_id_exist :
                    if next_question_node['label'] == 'end':
                        self.run_gremlin_query('g.addV("end").property("partitionKey", "Answer").property("id", "'+next_new_node_id+'")')
                    else:
                        self.run_gremlin_query("g.addV('Answer').property('partitionKey', 'Answer').property('id', '"+next_new_node_id+"').property('question', '"+next_question_node['properties']['text'][0]['value']+"').property('question_id', '"+next_question_node['id']+"')")


                self.run_gremlin_query("g.V('"+new_node_id+"').addE('Answer').to(g.V('"+next_new_node_id+"')).property('answer', '"+dict_answer['text']+"').property('proposition_id', '"+dict_answer['id']+"')")

        self.run_gremlin_query("g.V('"+username+"').addE('Answer').to(g.V('answer1"+nb_form+"')).property('partitionKey', 'Answer')")
            
    def save_feedback(self, text_feedback, username):
        """
        Save feedback in db
        """
        nb_feedback_by_user = len(self.run_gremlin_query("g.V('"+username+"').outE().hasLabel('Feedback')"))
        node_feedback_id = 'feedback'+username
        if nb_feedback_by_user == 0:
            self.run_gremlin_query("g.addV('Feedback').property('partitionKey', 'Feedback').property('id', '"+node_feedback_id+"')")
        edge_feedback_id = 'feedback'+username+str(nb_feedback_by_user+1)
        self.run_gremlin_query("g.V('"+username+"').addE('Feedback').to(g.V('"+node_feedback_id+"')).property('id', '"+edge_feedback_id+"').property('text', '"+text_feedback+"')")