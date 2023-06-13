"""
This file contains the class DbConnection, used to connect to the database and to run the queries
"""
import sqlite3
from typing import Optional

from regex import D

from ai_quality_check.models import Check

TABLE_LIST = ["Dataset"]


class DbAccess:
    """
    Class to manage the database Gremlin CosmosDB
    """

    def __init__(self) -> None:
        self.connector = sqlite3.connect("ai_quality_check/package_data_access/database_check_list")
        self.cursor = self.connector.cursor()

    def get_data(self, table_name: Optional[str] = None) -> dict[str, dict[str, list]]:
        """
        Method used to retreive all the data from the database
        Return dict[table: dict[cluster: list_of_elmt]]
        """
        dico: dict[str, dict[str, list]] = {}
        table_list = [table_name] if table_name is not None else TABLE_LIST
        for table in table_list:
            dico[table] = {}
            list_data = self.connector.execute(f"SELECT * FROM {table}").fetchall()
            for data in list_data:
                check_elmt = Check(number=data[0], text=data[1], help_text=data[2], cluster=data[3])
                if data[3] in dico[table]:
                    dico[table][data[3]].append(check_elmt)
                else:
                    dico[table][data[3]] = [check_elmt]

        return dico
