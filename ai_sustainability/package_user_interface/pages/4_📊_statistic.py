"""
This file is used to show the Statistic page
"""
from ai_sustainability.package_data_access.db_connection_old import DbConnection
from ai_sustainability.package_user_interface.classes.class_statistic import (
    StatisticStreamlit,
)


def main() -> None:
    """
    This is the code used by the admin to see statistics from the answers of the users
    """

    # Connection to the online gremlin database via db_connection.py
    st_statistic = StatisticStreamlit()
    database = DbConnection()
    username = st_statistic.username
    if not username:
        return

    if not st_statistic.check_if_admin(username):
        return
    selected_edges = database.get_nb_selected_edge_stats()
    st_statistic.display_statistic_edges(selected_edges)
    st_statistic.display_statistic_ais()  # Don't do anything for now


if __name__ == "__main__":
    main()
