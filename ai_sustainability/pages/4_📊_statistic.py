"""
This file is used to show the Statistic page
"""
from ai_sustainability.classes.class_statistic import StatisticStreamlit
from ai_sustainability.classes.db_connection import DbConnection


def main() -> None:
    """
    This is the code used by the admin to see statistics from the answers of the users
    """

    # Connection to the online gremlin database via db_connection.py
    database = DbConnection()
    st_statistic = StatisticStreamlit(database)
    database.make_connection()
    username = st_statistic.username
    if not username:
        return

    if not st_statistic.check_if_admin(username):
        return
    selected_edges = database.get_nb_selected_edge()
    st_statistic.display_statistic_edges(selected_edges)


if __name__ == "__main__":
    main()
