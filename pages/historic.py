import streamlit as st

def main():
    st.title("Historic")
    if 'username' in st.session_state and st.session_state.username != "":
        st.caption("Connected as " + str(st.session_state.username))
    else:
        st.caption("You are not connected, please connect with your username in the Connection page.")

if __name__ == "__main__":
      main()