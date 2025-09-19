# https://docs.streamlit.io/library/api-reference/layout/st.columns

import streamlit as st

col1, col2, col3 = st.columns(3)

# col1.header("aaaaa")

with col1:
   st.header("A cat")
   st.image("https://static.streamlit.io/examples/cat.jpg")

with col2:
   st.header("A dog")
   st.image("https://static.streamlit.io/examples/dog.jpg")

with col3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg")