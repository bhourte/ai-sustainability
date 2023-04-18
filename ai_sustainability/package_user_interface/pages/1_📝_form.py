"""
This file is used to show the From page
"""
import streamlit as st

from ai_sustainability.package_user_interface.classes.class_form import FormStreamlit
from ai_sustainability.package_user_interface.utils_streamlit import get_application


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    # Connection to the online gremlin database via db_connection.py
    st.set_page_config(page_title="Form Page", page_icon="📝")
    st.title("📝Form")

    app = get_application()
    st_form = FormStreamlit(app)
    username = st_form.username
    if not username:
        return
    st_form.render()


if __name__ == "__main__":
    main()
