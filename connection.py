import streamlit as st
from streamlit.source_util import get_pages
def main():
    st.title("Connection")
    if 'username' not in st.session_state:
        username = st.text_input("Put your username here to connect :")
        if '-' in username:
            st.warning("You can't use '-' in your username")
        else:
            st.session_state.username = username
    else:
        username = st.text_input("Put your username here to connect :", st.session_state.username)
        if '-' in username:
            st.warning("You can't use '-' in your username")
        else:
            st.session_state.username = username
    
if __name__ == "__main__":
    main()