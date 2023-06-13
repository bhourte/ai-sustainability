"""
Main file for the quality check of an AI Solution
This file correspond to the general value of the AI Quality Check page
"""

import streamlit as st

from ai_quality_check.utils import get_application


class DatasetPage:
    """Class used to show the general value of the AI Quality Check"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Dataset quality check page", page_icon="📊")
        st.title("📊 Dataset quality check")
        self.app = get_application()

    def render(self) -> None:
        """Method used to render the page"""
        data = self.app.get_data("Dataset")
        print(data)


if __name__ == "__main__":
    ui = DatasetPage()
    ui.render()
