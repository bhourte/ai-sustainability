""" File used to manage the online database """
import json
import os

import pandas as pd
from decouple import config
from gremlin_python import statics
from gremlin_python.driver import client, serializer

statics.load_statics(globals())


class DbGestion:
    """
    Class to manage the database Gremlin CosmosDB

    Parameters :
        - endpoint : the endpoint of the database (string)
        - database_name : the name of the database (string)
        - container_name : the name of the container (string)
        - primary_key : the primary key of the database (string)

    Methods :
        - __init__
        - run_gremlin_query : run a gremlin query
        - close : close the connection to the database
        - save_graph : save the graph in a json file
        - create_script : create a script to create the graph from the json file created by save_graph
        - create_script_with_weight : create a script to create the graph from the json file created by save_graph and
                the weight matrix.xlsx file (used to update the coefficient of the AIs for each edges)
        - import_graph : import a graph from a script created by create_script
    """

    def __init__(self, endpoint: str, database_name: str, container_name: str, primary_key: str) -> None:
        self.endpoint = endpoint
        self.database_name = database_name
        self.container_name = container_name
        self.primary_key = primary_key
        self.gremlin_client = client.Client(
            "wss://" + endpoint + ":443/",
            "g",
            username="/dbs/" + database_name + "/colls/" + container_name,
            password=primary_key,
            message_serializer=serializer.GraphSONSerializersV2d0(),
        )

    def run_gremlin_query(self, query: str) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")
        """
        run = self.gremlin_client.submit(query).all()
        return run.result()

    def close(self) -> None:
        """
        Close the connection to the database, must be called at the end of the program
        """
        self.gremlin_client.close()

    def save_graph(self, path: str) -> None:
        """
        Save the graph in a json file

        Parameters :
            - path : the path of the json file (string) (Exemple : "data/graph.json")
        """
        all_vertices = self.run_gremlin_query("g.V()")
        all_edges = self.run_gremlin_query("g.E()")
        if os.path.exists(path):
            os.remove(path)
        all_graph = [all_vertices, all_edges]
        with open(path, "w", encoding="utf-8") as file:
            json.dump(all_graph, file, ensure_ascii=False, indent=4)
            file.close()
        print(f"File {path} created")

    def create_script(self, data_path: str, script_path: str) -> None:
        """
        Create a script to create the graph from a json file

        Parameters :
            - data_path : the path of the json file (string) (Exemple : "data/graph.json")
            - script_path : the path of the script file (string) (Exemple : "data/script.json")
        """
        with open(data_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            file.close()
        print(f"File {data_path} loaded")

        querys = []
        for vertex in json_data[0]:
            query = "g.addV('" + vertex["label"] + "').property('id', '" + vertex["id"] + "')"
            if "properties" in vertex:
                for prop in vertex["properties"]:
                    query += f".property('{prop}', '{vertex['properties'][prop][0]['value']}')"
            querys.append(query)
        for edge in json_data[1]:
            query = (
                f"g.V('{edge['outV']}').addE('{edge['label']}').to(g.V('{edge['inV']}')).property('id', '{edge['id']}')"
            )
            if "properties" in edge:
                for prop in edge["properties"]:
                    query += f".property('{prop}', '{edge['properties'][prop]}')"
            querys.append(query)
        with open(script_path, "w", encoding="utf-8") as file:
            json.dump(querys, file, ensure_ascii=False, indent=4)
            file.close()
        print(f"Script {script_path} created")

    def create_script_with_weight(self, data_path: str, script_path: str, matrix_path: str) -> None:
        """
        Create a script to create the graph from a json file and update all weight from a local weight_matrix excel file
        and put the list of all AI's name in the node with id=1

        Parameters :
            - data_path : the path of the json file (string) (Exemple : "data/graph.json")
            - script_path : the path of the script file (string) (Exemple : "data/script.json")
            - matrix_path : the path of the excel file where the weight matrix is stored (Exemple : Weight_matrix.xlsx)
        """
        with open(data_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            file.close()
        print(f"File {data_path} loaded")

        data = pd.read_excel(matrix_path)
        ids = list(data["id_edges"])
        list_ai = list(data.drop(["id_edges", "text"], axis=1).keys())
        ais = str(list_ai[0])
        i = 1
        while i < len(list_ai):
            ais += ", " + str(list_ai[i])
            i += 1
        data = data.drop(["id_edges", "text"], axis=1)
        matrix = data.to_numpy()
        dico_matrix = {}

        i = 0
        while i < 40:
            dico_matrix[ids[i]] = list(matrix[i])
            i += 1

        querys = []
        for vertex in json_data[0]:
            query = f"g.addV('{vertex['label']}').property('id', '{vertex['id']}')"
            if "properties" in vertex:
                for prop in vertex["properties"]:
                    if prop != "list_AI":
                        query += f".property('{prop}', '{vertex['properties'][prop][0]['value']}')"
            if vertex["id"] == "1":
                query += f".property('list_AI', '{ais}')"
            querys.append(query)
        for edge in json_data[1]:
            query = (
                f"g.V('{edge['outV']}').addE('{edge['label']}').to(g.V('{edge['inV']}')).property('id', '{edge['id']}')"
            )
            if "properties" in edge:
                for prop in edge["properties"]:
                    if prop != "list_coef":
                        query += f".property('{prop}', '{edge['properties'][prop]}')"
            query += f".property('list_coef', '{str(dico_matrix[edge['id']])[1:-1]}')"
            querys.append(query)
        with open(script_path, "w", encoding="utf-8") as file:
            json.dump(querys, file, ensure_ascii=False, indent=4)
            file.close()
        print(f"Script {script_path} created")

    def import_graph(self, script_path: str) -> None:
        """
        Import a graph from a script

        Parameters :
            - script_path : the path of the script file (string) (Exemple : "data/script.json")
        """
        with open(script_path, "r", encoding="utf-8") as file:
            querys = json.load(file)
            file.close()
        print(f"Script {script_path} loaded")

        for query in querys:
            self.run_gremlin_query(query)
        print("Graph imported")


if __name__ == "__main__":
    # Exemple of use:
    #   - create a test_node, save the graph in data.json,
    #       delete the graph, create a script from data.json,
    #       import the graph from the script, close the connection.
    #   - You will have a new node saved in the database and in the script (test_node)

    ENDPOINT = "questions-db.gremlin.cosmos.azure.com"
    DATABASE = "graphdb"
    COLLECTION = config("DATABASENAME")
    PRIMARYKEY = config("PRIMARYKEY")

    db_gestion = DbGestion(ENDPOINT, DATABASE, COLLECTION, PRIMARYKEY)
    # # db_gestion.save_graph("../data.json")
    # # db_gestion.save_graph("../data_weight.json")
    # db_gestion.run_gremlin_query("g.V().drop()")
    # db_gestion.run_gremlin_query("g.E().drop()")
    # db_gestion.create_script("../data.json", "../script.json")
    # # db_gestion.create_script_with_weight("../data_weight.json", "../script_weight.json", "../Weight_matrix.xlsx")
    db_gestion.import_graph("ai_sustainability/datas/script.json")
    db_gestion.close()
