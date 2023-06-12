"""File used for all application layer of the result part of the application"""

from ai_quality_check.business import Business
from ai_quality_check.db_access import DbAccess


class Application:
    """Application layer"""

    def __init__(self) -> None:
        self.database = DbAccess()
        self.business = Business()
