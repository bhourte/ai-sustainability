import streamlit as st

def main():
    st.title("Connection")
    
    if 'username' not in st.session_state:
        st.session_state.username = st.text_input("Put your username here to connect :")
    else:
         st.session_state.username = st.text_input("Put your username here to connect :", st.session_state.username)

if __name__ == "__main__":
      main()