import heapq
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from gremlin_python import statics
from gremlin_python.driver import client, serializer

_range = range

statics.load_statics(globals())

@st.cache_resource
def connect(endpoint:str, database_name:str, container_name:str, primary_key:str) -> client.Client:
    """
    Connect to the database and return the client (made only once thanks to the cache)

    Parameters :
        - endpoint : the endpoint of the database (string)
        - database_name : the name of the database (string)
        - container_name : the name of the container (string)
        - primary_key : the primary key of the database (string)
    
    Return :
        - client : the client to connect to the database
    """
    return client.Client(
        'wss://' + endpoint + ':443/', 'g',
        username="/dbs/" + database_name + "/colls/" + container_name,
        password=primary_key,
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

# only string on
def validate_answer(text:str)->str:
    """
    Validate the answer to avoid errors in the gremlin query

    Parameters :
        - text : the answer to validate (string)
    
    Return :
        - text : the validated answer (string)
    """
    return text.replace("'", "\\'")

class Form:
    """
    Class to manage the form

    Parameters :
        - endpoint : the endpoint of the database (string)
        - database_name : the name of the database (string)
        - container_name : the name of the container (string)
        - primary_key : the primary key of the database (string)

    Methods :
        - run_gremlin_query : run a gremlin query
        - close : close the connection to the database
        - add_question : add question from db to form
        - build_help_text : build the help text for a question
        - add_open_question : add open question from db to form
        - add_qcm_question : add qcm question from db to form
        - add_qrm_question : add qrm question from db to form
        - add_qcm_bool_question : add qcm bool question from db to form
        - get_text_question : get the text of a question
        - get_propositions_of_question : get the propositions of a question
        - get_weight : get the weights of a question (for IA )
        - calcul_best_IAs : calcul the 5 best IAs following the answers
        - show_best_IA: show the best IAs following the answers
        - add_qcm_select_form : display a qcm question with all the previous answered form
        - save_answers : save the answers in the database
        - change_answers : change the answers in the database
        - save_feedback : save the feedback in the database
        - get_all_feedbacks : get all the feedbacks in the database
        - get_nb_selected_edges : get the number of selected edges in the database
        - display_bar_graph : display a bar graph with the number of selected edges 
    """
    def __init__(self, endpoint:str, database_name:str, container_name:str, primary_key:str):
        """
        Initialize the class with the connection to the database
        """
        self.gremlin_client = connect(endpoint, database_name, container_name, primary_key)

    def run_gremlin_query(self, query:str)->list:
        """
        Run a gremlin query
        
        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")
        
        Return :
            - result : the result of the query (list)
        """
        run = self.gremlin_client.submit(query).all()
        result = run.result()
        return result

    def close(self):
        """
        Close the connection to the database, must be called at the end of the program
        """
        self.gremlin_client.close()
    
    def add_question(self, node_id:str, modif_crypted:str, previous_answer:str=None)->tuple:
        """
        Add question from db to form

        Parameters :
            - node_id : the id of the node to add (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
            - previous_answer : the previous answer to the question (string)

        
        Return :
            - next_node_id : the id of the next node (string)
            - answer : the answer to the question (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
        """
        q_type = self.run_gremlin_query("g.V('"+node_id+"').label()")
        if q_type[0] == "Q_Open":
            next_node_id, answer, modif_crypted = self.add_open_question(node_id, modif_crypted, previous_answer)
        elif q_type[0] == "Q_QCM":
            next_node_id, answer, modif_crypted = self.add_qcm_question(node_id, modif_crypted, previous_answer)
        elif q_type[0] == "Q_QRM":
            next_node_id, answer, modif_crypted = self.add_qrm_question(node_id, modif_crypted, previous_answer)
        elif q_type[0] == "Q_QCM_Bool":
            next_node_id, answer, modif_crypted = self.add_qcm_bool_question(node_id, modif_crypted, previous_answer)
        elif q_type[0] == "end":
            next_node_id = "end"
            answer = None
        else:
            print("Error: unknown question type")
        return next_node_id, answer, modif_crypted
    
    def build_question_help_text(self, node_id:str, props_ids:list = None)->str:
        """
        Build the help text of a question

        Parameters :
            - node_id : the id of the node to add (string)
            - props_ids : the ids of the propositions of the question (list of string)

        Return :
            - help_text : the help text of the question (string)
        """
        help_text = self.run_gremlin_query("g.V('"+node_id+"').properties('help text').value()")[0] + "\n"
        if props_ids is not None:
            for prop_id in props_ids:
                if self.run_gremlin_query("g.E('"+prop_id+"').properties('help text')"):
                    help_text += self.run_gremlin_query("g.E('"+prop_id+"').properties('text').value()")[0] + ": "+self.run_gremlin_query("g.E('"+prop_id+"').properties('help text').value()")[0] + "\n"
        return help_text

    def add_open_question(self, node_id:str, modif_crypted:str, previous_answer:str=None)->tuple:
        """
        Add open question from db to form

        Parameters :
            - node_id : the id of the node to add (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
            - previous_answer : the previous answer to the question (string)
        
        Return :
            - next_node_id : the id of the next node (string)
            - answer : the answer to the question (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
        """
        question = self.get_text_question(node_id)
        next_node_id = self.run_gremlin_query("g.V('"+node_id+"').outE().inV().id()")[0]
        if previous_answer is not None:  # If it has to be auto-completed before
            answer = st.text_area(label=question, height=100,label_visibility="visible", value=previous_answer[0], help=self.build_question_help_text(node_id))
        else:
            answer = st.text_area(label=question, height=100,label_visibility="visible", help=self.build_question_help_text(node_id))
        # If no answer given, we return None
        if not answer:
            return None, None, modif_crypted
        
        validated_answer = validate_answer(answer)
        dict_answer = [{
            "text": validated_answer,
            "id": self.run_gremlin_query("g.V('"+node_id+"').outE().id()")[0],
        }]
        return next_node_id, dict_answer, modif_crypted
    
    def add_qcm_question(self, node_id:str, modif_crypted:str, previous_answer:str=None)->tuple:
        """
        Add qcm question from db to form

        Parameters :
            - node_id : the id of the node to add (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
            - previous_answer : the previous answer to the question (string)
        
        Return :
            - next_node_id : the id of the next node (string)
            - answer : the answer to the question (string)
            - modif_crypted : the argument if the user will work with crypted data or not (string)
        """
        question = self.get_text_question(node_id)
        options = ['<Select an option>']
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        if previous_answer is not None:  # If it has to be auto-completed before
            previous_index = options.index(previous_answer[0])
            answer = st.selectbox(label=question, options=options, index=previous_index, help=self.build_question_help_text(node_id, props_ids))
        else:
            answer = st.selectbox(label=question, options=options, index=0, help=self.build_question_help_text(node_id, props_ids))
        # If no answer given, we return None
        if answer == '<Select an option>':
            return None, None, modif_crypted
        
        index = propositions.index(answer)
        next_node_id = self.run_gremlin_query("g.E('"+props_ids[index]+"').inV().id()")[0]
        text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
        dict_answer = [{"id": props_ids[index], 'text': text['value']}]
        return next_node_id, dict_answer, modif_crypted

    def add_qrm_question(self, node_id:str, modif_crypted:str, previous_answer:str=None)->tuple:
        """
        Add qrm question from db to form

        Parameters:
            - node_id (str): id of the node in the db
            - modif_crypted (str): argument if the user will work with crypted data or not
            - previous_answer (str): previous answer to the question
        
        Return:
            - next_node_id (str): id of the next node
            - answer (str): answer to the question
            - modif_crypted (str): argument if the user will work with crypted data or not
        """
        question = self.get_text_question(node_id)
        options = []
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        if previous_answer is not None:  # If it has to be auto-completed before
            answers = st.multiselect(label=question, options=options, default=previous_answer, help=self.build_question_help_text(node_id, props_ids))
        else:
            answers = st.multiselect(label=question, options=options, default=None, help=self.build_question_help_text(node_id, props_ids))
        # If no answer given, we return None
        if answers == []:
            return None, None, modif_crypted
        
        next_node_id = self.run_gremlin_query("g.V('"+node_id+"').outE().inV().id()")[0]
        answers_returned = []
        for answer in answers:
            index = propositions.index(answer)
            text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
            answers_returned.append({'id': props_ids[index], 'text': text['value']})
        return next_node_id, answers_returned, modif_crypted
    
    def add_qcm_bool_question(self, node_id:str, modif_crypted:str, previous_answer:str=None)->tuple:
        """
        Add qcm bool question from db to form

        Parameters:
            - node_id (str): id of the node in the db
            - modif_crypted (str): argument if the user will work with crypted data or not
            - previous_answer (str): previous answer to the question
        
        Return:
            - next_node_id (str): id of the next node
            - answer (str): answer to the question
            - modif_crypted (str): argument if the user will work with crypted data or not
        """
        question = self.get_text_question(node_id)
        options = ['<Select an option>']
        propositions, props_ids = self.get_propositions_of_question(node_id, modif_crypted)
        for option in propositions:
            options.append(option)
        if previous_answer is not None:  # If it has to be auto-completed before
            previous_index = options.index(previous_answer[0])
            answer = st.selectbox(label=question, options=options, index=previous_index, help=self.build_question_help_text(node_id, props_ids))
        else:
            answer = st.selectbox(label=question, options=options, index=0, help=self.build_question_help_text(node_id, props_ids))
        # If no answer given, we return None
        if answer == '<Select an option>':
            return None, None, modif_crypted

        index = propositions.index(answer)
        next_node_id = self.run_gremlin_query("g.E('"+props_ids[index]+"').inV().id()")[0]
        text = self.run_gremlin_query("g.E('"+props_ids[index]+"').properties('text')")[0]
        modif_crypted = (answer == 'Yes')
        dict_answer = [{"id": props_ids[index], 'text': text['value']}]
        return next_node_id, dict_answer, modif_crypted
    
    def get_text_question(self, node_id:str)->str:
        """
        Get text of a question

        Parameters:
            - node_id (str): id of the node in the db
        
        Return:
            - question (str): text of the question
        """
        question = self.run_gremlin_query("g.V('"+node_id+"').properties('text').value()")[0]
        return question

    def get_propositions_of_question(self, node_id:str, modif_crypted:str)->tuple:
        """
        Get propositions of a question

        Parameters:
            - node_id (str): id of the node in the db
            - modif_crypted (str): argument if the user will work with crypted data or not
        
        Return:
            - propositions (list(str)): list of text of propositions
            - props_ids (list(str)): list of ids of propositions
        """
        propositions = []
        props_ids = []
        if modif_crypted:  # If there is some proposition we can not show because it's impossible to implement the AI doing it (because data are crypted)
            for edges in self.run_gremlin_query("g.V('"+node_id+"').outE().id()"):
                if self.run_gremlin_query("g.E('"+edges+"').properties('modif_crypted').value()")[0] == 'false':
                    props_ids.append(edges)
                    propositions.append(self.run_gremlin_query("g.E('"+edges+"').properties('text').value()")[0])
        else:  # If not, we return all existing propositions
            propositions = self.run_gremlin_query("g.V('"+node_id+"').outE().properties('text').value()")
            props_ids = self.run_gremlin_query("g.V('"+node_id+"').outE().id()")
        
        return propositions, props_ids
    
    def get_weight(self, edge_id:str)->list:
        """
            Get the list_coef from the edge with edge_id id
        
        Parameters:
            - edge_id (str): id of the edge in the db
        
        Return:
            - list_weight (list(float)): list of the weights of the edge
        """
        list_weight = self.run_gremlin_query("g.E('"+edge_id+"').properties('list_coef').value()")[0].split(", ")
        i = 0
        while i < len(list_weight):
            list_weight[i] = float(list_weight[i])
            i += 1
        return list_weight
    
    def calcul_best_AIs(self, nbAI:int, answers:list)->list:
        """
            Return the nbAI best AIs from a list of answers, but show less if there is less than nbAI possible
        
        Parameters:
            - nbAI (int): number of AIs to return
            - answers (list): list of answers
        
        Return:
            - list_bests_AIs (list): list of the nbAI best AIs

            TODO: check if 2 AI have the same coef what append
        """
        list_AI = self.run_gremlin_query("g.V('1').properties('list_AI')")[0]['value'].split(", ")
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
        return list_bests_AIs
    
    def show_best_AI(self, list_bests_AIs:list)->None:
        """
            Method used to show the n best AI obtained after the user has completed the Form
            The number of AI choosen is based on the nbAI wanted by the user and the maximum of available AI for the use of the user
            (If there is only 3 AI possible, but the user asked for 5, only 3 will be shown)

        Parameters:
            - list_bests_AIs (list): list of the n best AI
        
        Return:
            - None
        """
        if len(list_bests_AIs) > 0:
            st.subheader("There is "+str(len(list_bests_AIs))+" IA corresponding to your specifications, here they are in order of the most efficient to the least:", anchor=None)
            i = 0
            while i < len(list_bests_AIs):
                st.caption(str(i+1)+") "+list_bests_AIs[i])
                i += 1
        # If no AI corresponding the the choices
        else:
            st.subheader("There is no AI corresponding to your request, please make other choices in the form", anchor=None)

    def add_qcm_select_form(self, username:str)->str:
        """
            Display a qcm question with all the previous answered form

        Parameters:
            - username (str): username of the user
        
        Return:
            - next_node_id (str): id of the next node to display
        """
        question = "Select the previous form you want to see again or edit"
        list_form_name = ['<Select a form>']
        edges_answers = self.run_gremlin_query("g.V('"+str(username)+"').outE('Answer')")
        props_ids = []
        for edge in edges_answers:
            text = edge['inV'].split("-")  # we split the name between the "-", and the last item is the form name
            list_form_name.append(text[-1])  # We get the form name and we append it to the list of all forms names
            props_ids.append(edge['inV'])
        answer = st.selectbox(label=question, options=list_form_name, index=0)
        if answer == '<Select a form>':
            next_node_id = None
        else:  # We get the index of the form
            index = list_form_name.index(answer)-1
            next_node_id = props_ids[index]
        return next_node_id

    def save_answers(self, answers:list, username:str, list_bests_AIs:list, form_name:str=None)->None:
        """
        Save answers in db
        
        Parameters:
            - answers (list): list of answers
            - username (str): username of the user
            - list_bests_AIs (list): list of the n best AI
            - form_name (str): name of the form

        Return:
            - None
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
        if form_name is not None:
            nb_form = "-"+str(form_name)
        # If a node with the same name already exist, this means that a form with the same name already exist, so we exit without saving it again
        if self.run_gremlin_query("g.V('"+username+'-answer1'+nb_form+"')"):
            st.warning("You already have a form with this name, please pick an other name or change your previous form in the historic page.")
            return None

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
                while (self.run_gremlin_query("g.V('"+new_node_id+"').outE().has('answer', '"+dict_answer['text']+"').id()") == []): 
                    self.run_gremlin_query("g.V('"+new_node_id+"').addE('Answer').to(g.V('"+next_new_node_id+"')).property('answer', '"+dict_answer['text']+"').property('proposition_id', '"+dict_answer['id']+"')")
        first_node_id = username+'-'+'answer1'+nb_form
        self.run_gremlin_query("g.V('"+username+"').addE('Answer').to(g.V('"+first_node_id+"')).property('partitionKey', 'Answer')")
        list_bests_AIs = str(list_bests_AIs)[1:-1]
        self.run_gremlin_query("g.V('"+first_node_id+"').property('list_bests_AIs', '"+list_bests_AIs+"')")
        st.session_state.clicked = True  # global variable used to tell the form page that the button ("submit") has been clicked

    def change_answers(self, answers:list, username:str, list_bests_AIs:list, form_name:str, new_form_name:str)->None:
        """
        Change the answer in db

        Parameters:
            - answers (list): list of answers
            - username (str): username of the user
            - list_bests_AIs (list): list of the n best AI
            - form_name (str): name of the form
            - new_form_name (str): new name of the form
        
        Return:
            - None
        """
        # We first delete the existing graph
        node_id = username+'-answer1-'+str(form_name)
        end = True
        while end:
            next_node_id = self.run_gremlin_query("g.V('"+node_id+"').out().properties('id')")
            # we delete the node
            self.run_gremlin_query("g.V('"+node_id+"').drop()")
            if not next_node_id:
                end = False
            else:
                node_id = next_node_id[0]['value']
        self.save_answers(answers, username, list_bests_AIs, new_form_name)

    def save_feedback(self, text_feedback:str, username:str)->None:
        """
        Save feedback in db

        Parameters:
            - text_feedback (str): text of the feedback
            - username (str): username of the user
        
        Return:
            - None
        """
        nb_feedback_by_user = len(self.run_gremlin_query("g.V('"+username+"').outE().hasLabel('Feedback')"))
        node_feedback_id = 'feedback'+username
        if nb_feedback_by_user == 0:
            self.run_gremlin_query("g.addV('Feedback').property('partitionKey', 'Feedback').property('id', '"+node_feedback_id+"')")
        edge_feedback_id = 'feedback'+username+str(nb_feedback_by_user+1)
        self.run_gremlin_query("g.V('"+username+"').addE('Feedback').to(g.V('"+node_feedback_id+"')).property('id', '"+edge_feedback_id+"').property('text', '"+text_feedback+"')")
    
    def get_all_feedbacks(self)->None:
        """
        Get all feedback in db and display it

        Return:
            - None
        """
        all_users_id = self.run_gremlin_query("g.V().hasLabel('user').id()")
        if not all_users_id:
            st.write("There is no user registered in the database.")
            return None
        is_no_feedback = True
        for user_id in all_users_id:
            all_feedback = self.run_gremlin_query("g.V('"+user_id+"').outE().hasLabel('Feedback').id()")
            with st.expander('Feedbacks from '+ user_id):
                for feedback_id in all_feedback:
                    is_no_feedback = False
                    feedback = self.run_gremlin_query("g.E('"+feedback_id+"').properties('text').value()")
                    st.write(feedback_id + ': '+ feedback[0])
        if is_no_feedback:
            st.write("There is no feedback in the database.")
            return None

    def get_nb_selected_edges(self)->dict:
        """
        Get all answers in db

        return:
            - edges_selected (dict): dictionnary with proposition_id as key and number of time it was selected as value
        """
        edges_selected = {}
        all_selected_edges = self.run_gremlin_query("g.E().hasLabel('Answer').valueMap('proposition_id')")
        for edge in all_selected_edges:
            if 'proposition_id' in edge.keys():
                if edge['proposition_id'] not in edges_selected.keys():
                    edges_selected[edge['proposition_id']] = 0
                edges_selected[edge['proposition_id']] += 1
        return edges_selected

    def display_bar_graph(self, edges_selected:dict)->None:
        """
        Display bar graph of edges selected

        Parameters:
            - edges_selected (dict): dictionnary with proposition_id as key and number of time it was selected as value

        Return:
            - None
        """
        # change the dictionnary in dict {proposition_id: {text: text, nb_selected: nb_selected}}
        edges_selected_with_text = {}
        for key, value in edges_selected.items():
            text = self.run_gremlin_query("g.E('"+key+"').properties('text').value()")
            if text:
                edges_selected_with_text[key] = {'text': text[0], 'nb_selected': value}
            else:
                edges_selected_with_text[key] = {'text': self.run_gremlin_query("g.E('"+key+"').label()")[0], 'nb_selected': value}
        
        # sort the dict on x_axis (keys), display on x_label only the id of the proposition, and on the hover text the label and the text of the proposition
        # add in hover text the id of the proposition
                
        with st.spinner('Loading...'):
            sorted_edges_selected_with_text = {k: edges_selected_with_text[k] for k in sorted(edges_selected_with_text)}
            x_axis = []
            x_label = []
            hover_text = []
            y_axis = []
            for key, value in sorted_edges_selected_with_text.items():
                x_axis.append(key)
                x_label.append(key.split('-')[0])
                hover_text.append(value['text'] +'<br> proposition_id: ' +key)
                y_axis.append(value['nb_selected'])
            fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis, text=hover_text, hovertext=hover_text, hoverinfo='text')])
            # hover text angle to -90
            fig.update_layout(
                title='Number of times each edge was selected', 
                xaxis_title='Question', 
                yaxis_title='Number of times selected', 
                xaxis = dict(tickangle = -45, ticktext=x_label, tickvals=x_axis), 
                yaxis = dict(dtick = 1),
                )
            # Rotate x-axis labels, and set y-axis tick interval to 1 and 
            st.plotly_chart(fig)

    def display_bar_graph_v2(self, edge_selected)->None:
        """
        Display bar graph of edges selected (v2)

        Parameters:
            - edge_selected (dict): dictionnary with proposition_id as key and number of time it was selected as value
        
        Return:
            - None
        """
        # sort the dict on keys
        edge_selected = {k: edge_selected[k] for k in sorted(edge_selected)}
        hover_text = []
        text = []
        for key in edge_selected.keys():
            hover_text.append("Q"+self.run_gremlin_query("g.E('"+key+"').outV().id()")[0]+" to Q"+self.run_gremlin_query("g.E('"+key+"').inV().id()")[0])
            if self.run_gremlin_query("g.E('"+key+"').properties('text').value()"):
                text.append(self.run_gremlin_query("g.E('"+key+"').properties('text').value()")[0])
            else:
                text.append(self.run_gremlin_query("g.E('"+key+"').label()")[0])
        fig = go.Figure(data=[go.Bar(x=list(edge_selected.keys()), y=list(edge_selected.values()), hovertext=text, text=hover_text)])
        fig.update_layout(
            title='Number of times each edge was selected',
            xaxis_title='Edges/Propositions id',
            yaxis_title='Number of times selected',
            yaxis = dict(dtick = 1),
            )
        st.plotly_chart(fig)

    def no_dash_in_my_text(self, text:str)->bool:
        """
        Check if there is a dash in the text
        
        Parameters:
            - text (str): text to check
        
        Return:
            - bool: True if there is no dash, False otherwise"""
        if '-' in text:
            return False
        else:
            return True
