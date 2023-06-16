"""
Main file for the quality check of an AI Solution
This file correspond to the general value of the AI Quality Check page
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from ai_quality_check.utils import get_application, get_data

TABLE_LIST = ["Deployment", "Documentation", "Performance", "Model_Selection", "Pipeline", "Dataset"]


class GlobalQuality:
    """Class used to show the general value of the AI Quality Check"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Global quality check page", page_icon="📊")
        st.title("📊 Global quality check")
        self.app = get_application()
        self.app.get_data()

    def show_graph_score(self, score: dict) -> None:
        """Method used to show a Eye-Catching Radial Bar Charts with all scores"""
        ring_colours = ["#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"]
        ring_labels = [f"   {score_elmt} ({score[score_elmt][0]}/{score[score_elmt][1]}) " for score_elmt in score]
        fig = plt.figure(figsize=(10, 10), linewidth=10, edgecolor="#ffffff", facecolor="#ffffff")
        rect = [0.1, 0.1, 0.8, 0.8]
        # Add axis for radial backgrounds
        ax_polar_bg = fig.add_axes(rect, polar=True, frameon=False)
        # Start bars at top of plot
        ax_polar_bg.set_theta_zero_location("N")
        # Make bars go counter-clockwise.
        ax_polar_bg.set_theta_direction(1)
        # Loop through each entry in the dict and plot a grey
        # ring to create the background for each one
        for i in score:
            max_value = score[i][1]
            ax_polar_bg.barh(i, max_value * 1.5 * np.pi / max_value, color="grey", alpha=0.1)
        # Hide all axis items
        ax_polar_bg.axis("off")
        # Add axis for radial chart for each entry
        ax_polar = fig.add_axes(rect, polar=True, frameon=False)
        ax_polar.set_theta_zero_location("N")
        ax_polar.set_theta_direction(1)
        ax_polar.set_rgrids(
            list(range(len(score.keys()))),
            labels=ring_labels,
            angle=0,
            fontsize=14,
            fontweight="bold",
            color="black",
            verticalalignment="center",
        )

        # Loop through each entry and create a coloured ring for eachones
        index = 0
        for _, item in score.items():
            value = item[0]
            max_value = item[1]
            ax_polar.barh(index, value * 1.5 * np.pi / max_value, color=ring_colours[index])
            index += 1
        # Hide all grid elements
        ax_polar.grid(False)
        ax_polar.tick_params(axis="both", left=False, bottom=False, labelbottom=False, labelleft=True)
        st.pyplot(fig)

    def show_global_score(self, score: dict) -> None:
        global_score = 0.0
        for _, (value, max_value) in score.items():
            global_score += value / max_value
        global_score = global_score / len(score.keys())
        st.title(f"Global score = {round(global_score * 100, 2)}%")
        color = "green" if global_score > 0.75 else "orange" if global_score > 0.5 else "red"
        if global_score == 1:
            text = "Perfect!!!"
        elif global_score > 0.75:
            text = "Good!!"
        elif global_score > 0.5:
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
        st.progress(global_score, text)

    def render(self) -> None:
        """Method used to render the page"""
        data = st.session_state.database if "database" in st.session_state else get_data(self.app)
        score = self.app.compute_score(data)
        # score = {"Database": (20, 20), "Test1": (9, 14), "test3": (65, 140)}
        self.show_global_score(score)
        self.show_graph_score(score)


if __name__ == "__main__":
    ui = GlobalQuality()
    ui.render()
