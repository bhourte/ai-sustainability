"""File with all utils functions"""

from typing import Optional

import streamlit as st

from ai_validation.application import Application
from ai_validation.models import Experiment


# Put the cache in comment during development phase (to not have to restart streamlit each time a modification is made)
# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


def get_actual_experiment() -> Optional[Experiment]:
    selected_experiment = st.session_state.selected_experiment if "selected_experiment" in st.session_state else None
    if selected_experiment is None:
        st.warning("No experiment selected, please select one")
        return None
    st.caption(
        f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
    )
    return selected_experiment
