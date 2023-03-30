import streamlit as st

def main():
    st.title("Historic")
    if 'username' not in st.session_state or st.session_state.username == "":
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    st.caption("Connected as " + str(username))

if __name__ == "__main__":
      main()