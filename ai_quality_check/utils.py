"""File with all utils functions"""

import streamlit as st

from ai_quality_check.application import Application


# Put the cache in comment during development phase (to not have to restart streamlit each time a modification is made)
# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


@st.cache_resource
def get_data(application: Application) -> dict:
    return application.get_data()
