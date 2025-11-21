import streamlit as st
import json
import patient_form_page as form
import lab_results_page as labs
import dashboard_page as dash
st.title("Smart Clinic")


# --- Credenciais hardcoded ---
correct_username = "admin"
correct_password = "1234"

# Estado de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")

    username = st.text_input("User")
    password = st.text_input("Password", type="password")
    isDoctor = st.checkbox("Usuário é medico.")
    if st.button("Entrar"):
        if not username or not password:
            st.error("Preencha usuário e senha.")
        else:
            st.session_state.logged_in = True
            st.rerun()
        
# --- Conteúdo após login ---
if st.session_state.logged_in:
    option = st.sidebar.radio("",
        ["Pre consultation form", "Lab result uploads", "Dashboard information"]
    )

    if option == "Pre consultation form":
        form.generate_patient_intake_form(None)
    if option == "Lab result uploads":
        labs.lab_results_page()
    if option == "Dashboard information":
        dash.lab_dashboard_page()