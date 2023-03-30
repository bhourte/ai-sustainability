import streamlit as st

def main():
    if 'username' in st.session_state:
        st.caption("Connected as " + str(st.session_state.username))
    else:
        st.caption("You are not connected, please connect with your username in the Connection page")
    st.title("Historic")

if __name__ == "__main__":
      main()