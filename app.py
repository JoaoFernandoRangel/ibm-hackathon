import streamlit as st
import json
import os
import patient_form_page as form
import lab_results_page as labs
import dashboard_page as dash
from src.Diary import DiaryAnalyzer
from segredos.watson_api import project_id

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
    isDoctor = st.checkbox("User is a doctor")
    if st.button("Sign in"):
        if not username or not password:
            st.error("Please enter username and password.")
        else:
            st.session_state.logged_in = True
            st.rerun()
        
# --- Conteúdo após login ---
if st.session_state.logged_in:
    option = st.sidebar.radio("Menu",
        ["Pre consultation form", "Lab result uploads", "Dashboard information", "Sumário Clínico Inteligente"],
        label_visibility='visible'
    )

    if option == "Pre consultation form":
        form.generate_patient_intake_form(None)
    if option == "Lab result uploads":
        labs.lab_results_page()
    if option == "Dashboard information":
        dash.dashboard_page()

    if option == "Smart Clinical Summary":
        st.header("🧾 Smart Clinical Summary")
        st.write("Generate a structured summary and a narrative version of the clinical case using Granite (watsonx) or a local model.")

        # Layout em duas colunas para opções e ação
        c1, c2 = st.columns([2, 3])

        with c1:
            backend = st.selectbox("Backend", ["watsonx", "local"], index=0)
            model_tone = st.selectbox("Summary tone", ["Concise", "Detailed", "Clinical formal"], index=0)
            save_fb = st.checkbox("Save to Firebase (if configured)", value=False)

            # tenta carregar apikey localmente (somente quando for watsonx)
            apikey = None
            apikey_path = os.path.join("segredos", "apikey.json")
            if backend == "watsonx":
                if os.path.exists(apikey_path):
                    try:
                        with open(apikey_path, "r", encoding="utf-8") as f:
                            apikey = json.load(f).get("apikey")
                    except Exception:
                        apikey = None

                if not apikey:
                    st.warning("File `segredos/apikey.json` not found or invalid. Watsonx requires this key.")

            # permitir seleção de páginas (se houver pasta `database` com arquivos txt)
            pages = []
            try:
                db_dir = os.path.join("database")
                if os.path.exists(db_dir):
                    pages = [p for p in os.listdir(db_dir) if p.endswith('.txt')]
            except Exception:
                pages = []

            selected_pages = st.multiselect("Include pages/diaries (optional)", options=pages, default=pages)

            custom_prompt = st.text_area("Custom prompt (optional)", value="", height=120)

        with c2:
            st.markdown("**Prompt preview**")
            if custom_prompt.strip() == "":
                preview = (
                    "Summarize the clinical case below in the following format: 1) objective summary; 2) main problems;"
                    " 3) suggested management; 4) a narrative version for the medical record. Use tone: {}.".format(model_tone)
                )
            else:
                preview = custom_prompt

            st.text_area("Prompt in use", value=preview, height=220)

        # Single action: centered button that respects the selected backend
        left, center, right = st.columns([1, 2, 1])
        with center:
            if st.button("Generate"):
                with st.spinner("Generating summary (may take a while)..."):
                    try:
                        if backend == "watsonx":
                            if not apikey:
                                st.error("Watsonx API key missing. Place it in `segredos/apikey.json`.")
                                raise RuntimeError("Watsonx API key missing")
                            an = DiaryAnalyzer(backend="watsonx", watsonx_api_key=apikey, watsonx_project_id=project_id)
                        else:
                            an = DiaryAnalyzer(backend="local")

                        summary = an.summarize_case(save_to_file=True, save_to_firebase=save_fb, page_names=selected_pages, tone=model_tone, custom_prompt=custom_prompt)
                        st.success("Summary generated.")
                        st.markdown("**Summary (ready for medical record)**")
                        st.text_area("Clinical Summary", summary, height=360)

                        # download
                        try:
                            out_path = os.path.join("results", "resumo_clinico.txt")
                            if os.path.exists(out_path):
                                with open(out_path, "rb") as f:
                                    data = f.read()
                                st.download_button("Download clinical summary", data=data, file_name="resumo_clinico.txt")
                        except Exception as e:
                            st.warning(f"Could not prepare download: {e}")

                    except Exception:
                        # erro já reportado ao usuário via st.error quando aplicável
                        pass