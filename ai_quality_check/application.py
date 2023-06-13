"""File used for all application layer of the result part of the application"""

from ai_quality_check.business import Business
from ai_quality_check.package_data_access.db_access import DbAccess


class Application:
    """Application layer"""

    def __init__(self) -> None:
        self.database = DbAccess()
        self.business = Business()

    def get_data(self) -> dict:
        """Method used to retreive all the data from the database"""
        return self.database.get_data()
