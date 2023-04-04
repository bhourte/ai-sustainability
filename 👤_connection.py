"""
This file is the main file
launch it with: streamlit run 👤_connection.py
"""
import streamlit as st

def main():
    """
        This is the code used to show the "Connection" page
        The user will connect here and be able to acces to the rest of the application after that
    """

    st.set_page_config(page_title="Connection Page", page_icon="👤")
    st.title("👤Connection")
    if 'username' not in st.session_state:  # User not already connected
        username = st.text_input("Put your username here to connect :")
    else: # User already connected, but can switch
        username = st.text_input("Put your username here to connect :", st.session_state.username)

    if username == "":  # User not connected
        st.caption("❌Not connected")
        return None
    
    if '-' in username:
        st.warning("You can't use '-' in your username")
        return None
    
    if username == 'Admin':
        st.caption("🔑Connected as an " + str(username))
    else :
        st.caption("✅Connected as " + str(username))
    st.session_state.username = username
    st.session_state.last_form_name = None  # To detect if the user create a form with the same name as the previous one
    st.session_state.clicked = False

    
if __name__ == "__main__":
    main()