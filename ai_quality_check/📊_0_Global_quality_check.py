"""
Main file for the quality check of an AI Solution
This file correspond to the general value of the AI Quality Check page
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from ai_quality_check.utils import get_application


class GlobalQuality:
    """Class used to show the general value of the AI Quality Check"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Global quality check page", page_icon="📊")
        st.title("📊 Global quality check")
        self.app = get_application()
        self.app.get_data()

    def show_global_score(self) -> None:
        """Method used to show a Eye-Catching Radial Bar Charts with all score and the global score"""
        lith_dict = {
            "LITH": ["None", "Deployement", "Documentation", "Performance", "Model selection", "Pipeline", "Dataset"],
            "COUNT": [40, 65, 40, 35, 40, 70, 50],
        }

        df = pd.DataFrame.from_dict(lith_dict)
        max_value_full_ring = 100
        data_len = len(df)
        ring_colours = ["#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"]
        ring_labels = [f"   {x} ({v}) " for x, v in zip(list(df["LITH"]), list(df["COUNT"]))]
        fig = plt.figure(figsize=(10, 10), linewidth=10, edgecolor="#ffffff", facecolor="#ffffff")
        rect = [0.1, 0.1, 0.8, 0.8]
        # Add axis for radial backgrounds
        ax_polar_bg = fig.add_axes(rect, polar=True, frameon=False)
        # Start bars at top of plot
        ax_polar_bg.set_theta_zero_location("N")
        # Make bars go counter-clockwise.
        ax_polar_bg.set_theta_direction(1)
        # Loop through each entry in the dataframe and plot a grey
        # ring to create the background for each one
        for i in range(data_len):
            ax_polar_bg.barh(i, max_value_full_ring * 1.5 * np.pi / max_value_full_ring, color="grey", alpha=0.1)
        # Hide all axis items
        ax_polar_bg.axis("off")
        # Add axis for radial chart for each entry in the dataframe
        ax_polar = fig.add_axes(rect, polar=True, frameon=False)
        ax_polar.set_theta_zero_location("N")
        ax_polar.set_theta_direction(1)
        ax_polar.set_rgrids(
            [0, 1, 2, 3, 4, 5, 6],
            labels=ring_labels,
            angle=0,
            fontsize=14,
            fontweight="bold",
            color="black",
            verticalalignment="center",
        )

        # Loop through each entry in the dataframe and create a coloured
        # ring for each entry
        for i in range(data_len):
            ax_polar.barh(i, list(df["COUNT"])[i] * 1.5 * np.pi / max_value_full_ring, color=ring_colours[i])
        # Hide all grid elements
        ax_polar.grid(False)
        ax_polar.tick_params(axis="both", left=False, bottom=False, labelbottom=False, labelleft=True)
        st.pyplot(fig)

    def render(self) -> None:
        """Method used to render the page"""
        self.show_global_score()


if __name__ == "__main__":
    ui = GlobalQuality()
    ui.render()
