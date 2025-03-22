# https://docs.streamlit.io/library/api-reference/layout/st.container


import streamlit as st
import numpy as np

with st.container():
   st.write("This is inside the container")

   # You can call any Streamlit command, including custom components:
   st.bar_chart(np.random.randn(50, 3))

st.write("This is outside the container")