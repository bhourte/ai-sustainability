"""File with all utils functions"""

import streamlit as st

from ai_quality_check.application import Application
from ai_quality_check.models import Check


# Put the cache in comment during development phase (to not have to restart streamlit each time a modification is made)
# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


def get_data(application: Application) -> dict:
    st.session_state.database = application.get_data()
    return st.session_state.database


def render_check_list(data: dict) -> None:
    for cluster in data:
        if len(data[cluster]) == 1:
            check_elmt: Check = data[cluster][0]
            if st.checkbox(check_elmt.text, help=check_elmt.help_text, value=check_elmt.checked):
                check_elmt.checked = True
            else:
                check_elmt.checked = False
        else:
            count = sum(i.checked for i in data[cluster])
            expender = st.expander(f"{'✅' if count == len(data[cluster]) else ''} {cluster}")
            for check_elmt in data[cluster]:
                if expender.checkbox(check_elmt.text, help=check_elmt.help_text, value=check_elmt.checked):
                    check_elmt.checked = True
                    new_count = sum(i.checked for i in data[cluster])
                    if count == new_count - 1 and new_count == len(data[cluster]):  # If all elmt are checked after
                        st.experimental_rerun()
                else:
                    check_elmt.checked = False
                    new_count = sum(i.checked for i in data[cluster])
                    if count == new_count + 1 and count == len(data[cluster]):  # If all was checked but one is not now
                        st.experimental_rerun()
