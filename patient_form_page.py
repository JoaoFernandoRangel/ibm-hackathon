import streamlit as st
import IA_interactions as ia
import json
import os
from datetime import datetime, time, timedelta
from src.triage import assess_risk
from src.Diary import DiaryAnalyzer
from segredos.watson_api import project_id
from src.orchestrate_tools import orchestrate_followup_workflow, OrchestrateFollowupInput
# Schema fixo do formulário
FORM_SCHEMA = {
    "name": "text",
    "email": "text",
    "age": "number",
    "gender": "select:Male,Female,Other",
    "height_cm": "number",
    "weight_kg": "number",
    "allergies": "text",
    "current_medications": "text",
    "past_illnesses": "text",
    "family_medical_history": "text",
    "surgeries_or_hospitalizations": "text",
    "smoking_history": "select:Never,Former,Current",
    "alcohol_consumption": "select:Never,Occasionally,Regularly",
    "chief_complaint": "text",
    "pain_scale_0_to_10": "number",
    "symptoms_description": "text",
    "chronic_conditions": "text",
    "exercise_frequency": "select:None,1-2 times/week,3-5 times/week,Daily",
    "diet_description": "text"
}



# --------------------------------------------------------------
# MAIN PAGE FUNCTION
# --------------------------------------------------------------
def generate_patient_intake_form(_schema: dict):

    st.subheader("Patient Intake Form")

    # Armazena dados finais
    if "patient_data" not in st.session_state:
        st.session_state.patient_data = {}

    # ==========================================================
    # 1. Upload de arquivo
    # ==========================================================
    uploaded_file = st.file_uploader(
        "Upload a medical text file (optional) to auto-fill the form using AI",
        type=["txt"]
    )

    ai_suggestions = {}

    # Se o arquivo foi enviado
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8")

        st.info("Processing file with AI… (placeholder)")

        # FUTURE AUTOMATION: IA irá extrair dados
        ai_suggestions = ia.process_text_with_ai(raw_text)

    st.markdown("---")
    st.write("### Review and complete the form")

    # ==========================================================
    # 2. Formulário com valores da IA já preenchidos
    # ==========================================================
    form = st.form(key="patient_form_ui")

    filled_data = {}

    for field, field_type in FORM_SCHEMA.items():

        initial_value = ai_suggestions.get(field, "")

        # Select
        if field_type.startswith("select"):
            options = field_type.split(":")[1].split(",")
            default_index = options.index(initial_value) if initial_value in options else 0
            filled_data[field] = form.selectbox(
                field.replace("_", " ").title(),
                options,
                index=default_index
            )

        # Número
        elif field_type == "number":
            try:
                num_value = float(initial_value) if initial_value else 0
            except:
                num_value = 0
            filled_data[field] = form.number_input(
                field.replace("_", " ").title(),
                value=num_value,
                step=1
            )

        # Textarea normal
        else:
            filled_data[field] = form.text_area(
                field.replace("_", " ").title(),
                value=str(initial_value)
            )

    submitted = form.form_submit_button("Submit information")

    # ==========================================================
    # 3. Salvar resultado final
    # ==========================================================
    if submitted:
        st.session_state.patient_data = filled_data
        st.success("✔ Information saved successfully!")

        st.write("### Saved JSON:")
        st.json(filled_data)

        # Post-save action options
        st.markdown("---")
        st.write("### Actions")
        backend = st.selectbox("Backend for AI calls", ["watsonx", "local"], index=0)
        save_fb = st.checkbox("Save pre-prontuario to Firebase (if configured)", value=False)

        # Orchestration options
        st.write("### Follow-up Automation")
        patient_email_for_followup = st.text_input("Patient email for follow-up (used for sending invites)", value="")
        if not patient_email_for_followup:
            patient_email_for_followup = None
        send_followup = st.checkbox("Send follow-up form link via email", value=False)
        schedule_followup = st.checkbox("Schedule appointment (send calendar invite)", value=False)
        followup_date = None
        followup_time = None
        if schedule_followup:
            followup_date = st.date_input("Preferred follow-up date")
            followup_time = st.time_input("Preferred time")

        # Access token for Gmail API (OAuth access token) — can also be provided via segredos
        gmail_access_token = st.text_input("Gmail OAuth access token (for sending emails)", value="", type="password")

        # Ler apikey quando necessário
        apikey = None
        apikey_path = os.path.join("segredos", "apikey.json")
        if backend == "watsonx" and os.path.exists(apikey_path):
            try:
                with open(apikey_path, "r", encoding="utf-8") as f:
                    apikey = json.load(f).get("apikey")
            except Exception:
                apikey = None

        if st.button("Assess risk and generate pre-prontuario"):
            # Risk assessment
            with st.spinner("Assessing risk..."):
                triage_result = assess_risk(filled_data, backend=backend, watsonx_api_key=apikey, watsonx_project_id=project_id)

            st.subheader("Triage result")
            st.json(triage_result)

            # Generate pre-prontuario
            with st.spinner("Generating pre-prontuario with Granite..."):
                an = DiaryAnalyzer(backend=backend, watsonx_api_key=apikey, watsonx_project_id=project_id)
                pre = an.generate_pre_prontuario(filled_data)

            st.subheader("Pre-Prontuario (structured)")
            st.json(pre)

            # save to disk
            try:
                os.makedirs("results", exist_ok=True)
                out_path = os.path.join("results", "pre_prontuario.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(pre, f, ensure_ascii=False, indent=2)
                st.success(f"Pre-prontuario saved to: {out_path}")
                # download
                with open(out_path, "rb") as f:
                    data = f.read()
                st.download_button("Download pre_prontuario", data=data, file_name="pre_prontuario.json")
            except Exception as e:
                st.warning(f"Failed to save pre-prontuario: {e}")

            # save to Firebase (via Diary.save_week_summary or save_page_result) — DiaryAnalyzer uses save_page_result internally
            if save_fb:
                try:
                    an = DiaryAnalyzer(backend=backend, watsonx_api_key=apikey, watsonx_project_id=project_id)
                    # save the pre-prontuario as a document
                    an.save_json("pre_prontuario.json", json.dumps(pre, ensure_ascii=False, indent=2))
                    st.info("Attempted to save to Firebase (if configured).")
                except Exception as e:
                    st.warning(f"Failed to send to Firebase: {e}")

            # Orchestrate follow-up: send email and optionally schedule appointment
            if send_followup or schedule_followup:
                if not gmail_access_token:
                    st.warning("Gmail access token is required to send follow-up emails. Provide it in the field above.")
                else:
                    form_link = "https://example.com/followup-form"  # TODO: replace with real hosted form URL
                    followup_subject = "Please complete your follow-up form"
                    followup_body_template = "Hello, please complete the follow-up form here: {form_link}\n\nBest regards, Clinic"

                    start_iso = None
                    end_iso = None
                    if schedule_followup and followup_date and followup_time:
                        dt = datetime.combine(followup_date, followup_time)
                        start_iso = dt.replace(microsecond=0).isoformat() + 'Z'
                        # default duration 30 minutes
                        end_iso = (dt + timedelta(minutes=30)).replace(microsecond=0).isoformat() + 'Z'

                    orch_input = OrchestrateFollowupInput(
                        patient_email=patient_email_for_followup or filled_data.get('email') or filled_data.get('name') or 'patient@example.com',
                        form_link=form_link,
                        followup_subject=followup_subject,
                        followup_body_template=followup_body_template,
                        schedule=schedule_followup,
                        start_iso=start_iso,
                        end_iso=end_iso,
                        organizer_email='clinic@example.com',
                        access_token=gmail_access_token,
                    )

                    try:
                        with st.spinner('Triggering follow-up orchestration...'):
                            result = orchestrate_followup_workflow(orch_input)
                        st.success('Orchestration completed (check logs or email).')
                        st.json(result)
                    except Exception as e:
                        st.error(f'Failed to run orchestration: {e}')
