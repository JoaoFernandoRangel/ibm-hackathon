import streamlit as st
import json
import os
import patient_form_page as form
import dashboard_page as dash
import lab_results_page as labs
from src.Diary import DiaryAnalyzer
from KeyChain import KeyChain
project_id = "cf0f0ec9-62ec-4191-92e0-0c07d15a5fb0"



# load apikey only if watsonx
kc = KeyChain()
apikey = kc.load_from_env().get("WATSONX_APIKEY")
an = DiaryAnalyzer(backend="watsonx", watsonx_api_key=apikey, watsonx_project_id=project_id)

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
        ["Pre consultation form", "Lab result uploads", "Dashboard information", "Smart Clinical Summary", "Patients"],
        label_visibility='visible'
    )

    if option == "Pre consultation form":
        form.generate_patient_intake_form(None)
    if option == "Lab result uploads":
        labs.lab_results_page()
    if option == "Dashboard information":
        dash.dashboard_page()
    if option == "Patients":
        form.tela_pacientes()

    if option == "Smart Clinical Summary":
        st.header("🧾 Smart Clinical Summary")
        st.write("Generate a structured summary and a narrative version of the clinical case using the patient's stored JSON records (NOT the free-text diaries).")

        c1, c2 = st.columns([2, 3])
        
        #TODO Vem aqui Paulino
        with c1:
            backend = "watsonx"
            model_tone = st.selectbox("Summary tone", ["Concise", "Detailed", "Clinical formal"], index=0, key="smart_tone")
            



            # list patients (source of truth)
            try:
                
                pacientes = an.list_patients() or {}
            except Exception as e:
                st.error(f"Failed to list patients: {e}")
                pacientes = {}

            if not pacientes:
                st.warning("No patients found. Fill patient forms first.")
                display_list = []
                patient_keys = []
            else:
                patient_keys = list(pacientes.keys())
                display_list = [f"{pacientes[k].get('name','(sem nome)')} <{k}>" for k in patient_keys]

            patient_choice = st.selectbox("Select a patient", options=display_list, key="smart_patient_choice")
            patient_email = None
            patient_data = None
            if patient_choice:
                idx = display_list.index(patient_choice)
                patient_email = patient_keys[idx]
                patient_data = pacientes.get(patient_email)

            custom_prompt = st.text_area("Custom prompt (optional)", value="", height=120, key="smart_custom_prompt")

        with c2:
            st.markdown("**Prompt preview**")
            smart_custom_prompt = st.session_state.get("smart_custom_prompt", "")
            if smart_custom_prompt.strip() == "":
                preview = (
                    "Summarize the clinical case below in the following format: 1) objective summary; 2) main problems;"
                    " 3) suggested management; 4) a narrative version for the medical record. Use tone: {}.".format(model_tone)
                )
            else:
                preview = smart_custom_prompt

            st.text_area("Prompt in use", value=preview, height=220, key="smart_prompt_preview")

        # Action
        left, center, right = st.columns([1, 2, 1])
        with center:
            if st.button("Generate clinical summary (from patient's JSON records)", key="smart_generate_button"):
                if not patient_email:
                    st.error("Select a patient first.")
                    st.stop()

                # fetch all JSON records belonging to the patient from DiaryAnalyzer / Firebase
                with st.spinner("Loading patient records from storage..."):
                    records = None
                    try:
                        # preferred helper if implemented
                        records = an.get_all_patient_records(patient_email)
                    except Exception:
                        try:
                            # fallback: query collection for records with patient email
                            records = an.query_collection("patient_records", "email", "==", patient_email) or []
                        except Exception:
                            records = []

                if not records:
                    st.error("No records found for this patient.")
                    st.stop()

                # merge records into a single text payload for model
                try:
                    if isinstance(records, dict):
                        # single document returned as dict
                        merged = json.dumps(records, ensure_ascii=False, indent=2)
                    elif isinstance(records, list):
                        parts = []
                        for i, r in enumerate(records):
                            if isinstance(r, (dict, list)):
                                parts.append(f"--- RECORD {i+1} ---\n" + json.dumps(r, ensure_ascii=False))
                            else:
                                parts.append(f"--- RECORD {i+1} ---\n" + str(r))
                        merged = "\n\n".join(parts)
                    else:
                        merged = str(records)
                except Exception:
                    merged = str(records)

                # generate summary using selected backend
                with st.spinner("Generating summary..."):
                    # prefer a dedicated method if available, else call generate_summary_from_text
                    if hasattr(an, "generate_summary_from_text"):
                        summary = an.generate_summary_from_text(merged, max_new_tokens=1024, tone=model_tone, custom_prompt=custom_prompt)
                    else:
                        summary = an.summarize_case(save_to_file=False, save_to_firebase=False, page_names=None, tone=model_tone, custom_prompt=custom_prompt, patient_data=None)


                if summary:
                    st.subheader("Clinical Summary")
                    st.text_area("Clinical Summary", summary, height=360, key="smart_clinical_summary")
                    


    if option == "Intelligent Clinical Summary":
        st.header("🧾 Intelligent Clinical Summary")
        st.write("Generate a structured clinical prontuário/summary using the patient's form data (NOT the free-text diaries).")

        # Layout em duas colunas para options and action
        c1, c2 = st.columns([2, 3])

        with c1:
            backend = st.selectbox("Backend", ["watsonx", "local"], index=0, key="intel_backend")
            model_tone = st.selectbox("Summary tone", ["Concise", "Detailed", "Clinical formal"], index=0, key="intel_tone")
            
            # tenta carregar apikey localmente (somente quando for watsonx)
           

            # Carrega pacientes do Firebase / armazenamento via DiaryAnalyzer
            try:
                patients = an.list_patients() or {}
            except Exception as e:
                st.error(f"Failed to list patients: {e}")
                patients = {}

            if not patients:
                st.warning("No patients found. Fill patient forms first.")
                patient_keys = []
            else:
                # build display list "Name <email>"
                patient_keys = list(patients.keys())
                display_list = [f"{patients[k].get('name','Sem nome')} <{k}>" for k in patient_keys]

            selected_patient_display = st.selectbox("Select patient to summarize", options=display_list if patients else [], index=0 if patients else None, key="intel_select_patient")

            # resolve selected patient_data
            patient_data = None
            if patients and selected_patient_display:
                sel_idx = display_list.index(selected_patient_display)
                patient_email = patient_keys[sel_idx]
                patient_data = patients.get(patient_email)

            custom_prompt = st.text_area("Custom prompt (optional)", value="", height=120, key="intel_custom_prompt")

        with c2:
            st.markdown("**Prompt preview**")
            intel_custom_prompt = st.session_state.get("intel_custom_prompt", "")
            if intel_custom_prompt.strip() == "":
                preview = (
                    "Generate a clinical prontuário/summary FROM THE PATIENT FORM DATA only. Include: identification, chief complaint, HPI, relevant findings, diagnostic impression and brief recommendations. Use tone: {}.".format(model_tone)
                )
            else:
                preview = intel_custom_prompt

            st.text_area("Prompt in use", value=preview, height=220, key="intel_prompt_preview")

        # Action button
        left, center, right = st.columns([1, 2, 1])
        with center:
            if st.button("Generate from selected patient", key="intel_generate"):
                if not patient_data:
                    st.error("No patient selected or patient data missing.")
                else:
                    with st.spinner("Generating summary from patient form data (may take a while)..."):
                        # Prioritize patient_data as source of truth
                        summary = an.summarize_case(save_to_file=True, save_to_firebase=False, page_names=None, tone=model_tone, custom_prompt=st.session_state.get("intel_custom_prompt",""), patient_data=patient_data)
                        st.success("Summary generated from patient form.")
                        st.markdown("**Clinical Prontuário (from form)**")
                        st.text_area("Clinical Summary", summary, height=360, key="intel_clinical_summary")

                        # download
                        try:
                            out_path = os.path.join("results", "resumo_clinico.txt")
                            if os.path.exists(out_path):
                                with open(out_path, "rb") as f:
                                    data = f.read()
                                st.download_button("Download clinical summary", data=data, file_name="resumo_clinico.txt", key="intel_download")
                        except Exception as e:
                            st.warning(f"Could not prepare download: {e}")