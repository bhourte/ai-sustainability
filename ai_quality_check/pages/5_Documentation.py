"""
Main file for the quality check of an AI Solution
This file correspond to the general value of the AI Quality Check page
"""

import streamlit as st

from ai_quality_check.utils import (
    get_application,
    get_data,
    render_check_list,
    show_score,
)

CORESPONDING_TABLE = "Documentation"


class DocumentationPage:
    """Class used to show the general value of the AI Quality Check"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Documentation quality check page")
        st.title("Documentation quality check")
        self.app = get_application()

    def render(self) -> None:
        """Method used to render the page"""
        data = (
            st.session_state.database[CORESPONDING_TABLE]
            if "database" in st.session_state
            else get_data(self.app)[CORESPONDING_TABLE]
        )
        container = st.container()
        render_check_list(data)
        score, max_score = self.app.compute_score_one_page(data)
        show_score(score, max_score, container)


if __name__ == "__main__":
    ui = DocumentationPage()
    ui.render()
