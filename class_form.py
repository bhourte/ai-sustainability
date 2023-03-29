from gremlin_python import statics
from gremlin_python.driver import client, serializer
import streamlit as st
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
        answer = {
            "text": answer,
            "id": self.run_gremlin_query("g.V('"+node_id+"').outE().id()")[0],
        }
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
            answer = props_ids[index]
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
        if answers == []:
            answers = None
            next_node_id = None
        else:
            next_node_id = self.run_gremlin_query("g.V('"+node_id+"').outE().inV().id()")[0]
            for answer in answers:
                index = propositions.index(answer)
                answers[answers.index(answer)] = props_ids[index]
        return next_node_id, answers, modif_crypted
    
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
            modif_crypted = answer == 'Yes'
            answer = props_ids[index]
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
    
    def save_answers(self, answers, username):
        """
        Save answers in db
        """
        self.run_gremlin_query("g.addV('user').property('partitionKey', 'Answer').property('id', '"+username+"')")
        previous_node_id = username
        for answer in answers:
            if type(answer) == dict:
                vertex = self.run_gremlin_query("g.E('"+answer['id']+"').outV()")[0]
                next_node_id = 'answer'+vertex['id']
                self.run_gremlin_query("g.addV('Answer').property('partitionKey', 'Answer').property('id', '"+next_node_id+"').property('question', '"+vertex['properties']['text'][0]['value']+"').property('question_id', '"+vertex['id']+"')")
                self.run_gremlin_query("g.V('"+previous_node_id+"').addE('answer').to(g.V('"+next_node_id+"')).property('answer', '"+answer['text']+"')")
            elif type(answer) == list:
                i = 0
                for ans in answer:
                    vertex = self.run_gremlin_query("g.E('"+ans+"').outV()")[0]
                    next_node_id = 'answer'+vertex['id']+"-"+str(i)   
                    self.run_gremlin_query("g.addV('Answer').property('partitionKey', 'Answer').property('id', '"+next_node_id+"').property('question', '"+vertex['properties']['text'][0]['value']+"').property('question_id', '"+vertex['id']+"')")
                    self.run_gremlin_query("g.V('"+previous_node_id+"').addE('answer').to(g.V('"+next_node_id+"')).property('answer', '"+ans+"')")
                    i += 1
                    
            else:
                vertex = self.run_gremlin_query("g.E('"+answer+"').outV()")[0]
                next_node_id = 'answer'+vertex['id']
                self.run_gremlin_query("g.addV('Answer').property('partitionKey', 'Answer').property('id', '"+next_node_id+"').property('question', '"+vertex['properties']['text'][0]['value']+"').property('question_id', '"+vertex['id']+"')")
                self.run_gremlin_query("g.V('"+previous_node_id+"').addE('answer').to(g.V('"+next_node_id+"')).property('answer_id', '"+answer+"').property('text', '"+self.run_gremlin_query("g.E('"+answer+"').properties('text')")+"')")

            previous_node_id = next_node_id
                