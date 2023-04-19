"""
This file is used to show the From page
"""
import streamlit as st

from ai_sustainability.package_user_interface.pages_elements.page_form import (
    FormStreamlit,
)


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    st.set_page_config(page_title="Form Page", page_icon="📝")
    st.title("📝Form")

    st_form = FormStreamlit()
    username = st_form.username
    if not username:
        return
    st_form.render()


if __name__ == "__main__":
    main()
