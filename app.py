import streamlit as st
import utils as f

st.title("Isso é uma página de streamlit")
if st.button("Botão"):
    print("--")
    f.func()