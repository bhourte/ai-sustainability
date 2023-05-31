import streamlit as st

from ai_validation.application import Application


# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app
