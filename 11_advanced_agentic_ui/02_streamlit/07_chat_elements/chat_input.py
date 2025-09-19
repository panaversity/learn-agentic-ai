# https://docs.streamlit.io/library/api-reference/chat/st.chat_input

import streamlit as st

prompt = st.chat_input("Say something")

if 'data' not in st.session_state:
    st.session_state.data  = []

if prompt:
    st.session_state.data.append(prompt)
    for text in st.session_state.data:
        st.write(f"User has sent the following prompt: {text}")

st.write(st.session_state.data)