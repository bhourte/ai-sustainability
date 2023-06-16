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

CORESPONDING_TABLE = "Dataset"


class DatasetPage:
    """Class used to show the general value of the AI Quality Check"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Dataset quality check page")
        st.title("Dataset quality check")
        self.app = get_application()

    def show_page_score(self, score: dict) -> None:
        page_score = 0.0
        for _, (value, max_value) in score.items():
            page_score += value / max_value
        page_score = page_score / len(score.keys())
        st.title(f"Global score = {round(page_score * 100, 2)}%")
        color = "green" if page_score > 0.75 else "orange" if page_score > 0.5 else "red"
        if page_score == 1:
            text = "Perfect!!!"
        elif page_score > 0.75:
            text = "Good!!"
        elif page_score > 0.5:
            text = "Not that bad!"
        else:
            text = "Bad"
        st.markdown(
            """
            <style>
                .stProgress > div > div > div > div {
                    background-color: """
            + color
            + """;
                }
            </style>""",
            unsafe_allow_html=True,
        )
        st.progress(page_score, text)

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
    ui = DatasetPage()
    ui.render()
