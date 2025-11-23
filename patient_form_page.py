import streamlit as st
import json
import os
from datetime import datetime, time, timedelta
from src.triage import assess_risk
from src.Diary import DiaryAnalyzer
import streamlit as st
from src.orchestrate_tools import orchestrate_followup_workflow, OrchestrateFollowupInput
import KeyChain

project_id = "cf0f0ec9-62ec-4191-92e0-0c07d15a5fb0"
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

import streamlit as st
from src.Diary import DiaryAnalyzer

def tela_pacientes():
    import streamlit as st
    import json
    import base64
    from datetime import datetime, timedelta
    from src.read_replies_tool import GmailReadRepliesInput, read_replies

    #API verificar tokens
    from src.send_email_tool import (
    GmailSendInput,
    send_gmail_email,
    GmailSendWithAttachmentInput,
    send_gmail_email_with_ics,
    get_access_token
    )

    from src.Diary import DiaryAnalyzer

    st.title("Patients list")

    an = DiaryAnalyzer()
    pacientes = an.list_patients()

    if "pac_selected" not in st.session_state:
        st.session_state.pac_selected = None

    lista = [f"{data.get('name','Nameless')} <{email}>" for email, data in pacientes.items()]
    emails = list(pacientes.keys())

    escolhido = st.selectbox("Choose a patient:", lista)

    if escolhido:
        idx = lista.index(escolhido)
        email_sel = emails[idx]
        st.session_state.pac_selected = an.get_patient(email_sel)

    if st.session_state.pac_selected:
        st.subheader("Selected patient data:")
        st.json(st.session_state.pac_selected)

    # -----------------------------
    # Mostrar última resposta do paciente (se houver)
    # -----------------------------
    st.markdown("### 💬 Latest patient reply (via email)")
    try:
        # Carregar segredos

        kc = KeyChain()
        keys = kc.load_from_streamlit(st)

        refresh_token = keys["GMAIL_REFRESH_TOKEN"]
        client_id = keys["GMAIL_CLIENT_ID"]
        client_secret = keys["GMAIL_CLIENT_SECRET"]

        # Obter novo access token
        #API mudar para st.secrets
        access_token = get_access_token(refresh_token, client_id, client_secret)

        if not isinstance(access_token, str) or not access_token:
            st.warning("⚠️ Não foi possível obter o access token para buscar respostas.")
        else:
            # O assunto que você enviou no follow-up
            # -> Caso queira unificar, coloque o mesmo assunto sempre
            assunto_respostas = f"Olá {st.session_state.pac_selected.get('name','Paciente')}, teste de envio"

            # Preparar input para a ferramenta
            input_data = GmailReadRepliesInput(
                access_token=access_token,
                subject=assunto_respostas
            )

            # Ler respostas
            respostas = read_replies(input_data)

            if respostas:
                ultima = respostas[-1]  # pega a mais recente
                st.text_area(
                    "Resposta mais recente:",
                    ultima,
                    height=200
                )
            else:
                st.info("Nenhuma resposta encontrada para este paciente.")
    except Exception as e:
        st.error(f"Erro ao buscar respostas: {e}")


    # -----------------------------
    # Orchestration options
    # -----------------------------
    st.markdown("---")
    st.write("### Actions / Follow-up Automation")

    send_followup = st.checkbox("Send follow-up form link via email", value=False)
    schedule_followup = st.checkbox("Schedule appointment (send calendar invite)", value=False)

    followup_date = None
    followup_time = None
    if schedule_followup:
        followup_date = st.date_input("Preferred follow-up date")
        followup_time = st.time_input("Preferred time")

     

    # -----------------------------
    # Envio de email de teste / follow-up
    # -----------------------------
    if st.button("Send test email to selected patient"):

        if not st.session_state.pac_selected:
            st.warning("Please select a patient before sending the email.")
            return

        patient_data = st.session_state.pac_selected
        patient_name = patient_data.get("name", "Patient")
        email_dest = patient_data.get("email", email_sel)  # fallback to dict key
        # Gmail Access token         
        # API verificar tokens
        try:
            kc = KeyChain()
            keys = kc.load_from_streamlit(st)

            refresh_token = keys.get("GMAIL_REFRESH_TOKEN")
            client_id = keys.get("GMAIL_CLIENT_ID")
            client_secret = keys.get("GMAIL_CLIENT_SECRET")

            # validação mínima
            if not all([refresh_token, client_id, client_secret]):
                raise ValueError("Missing Gmail OAuth credentials in st.secrets.")

        except Exception as e:
            st.error(f"Could not load Gmail OAuth credentials from st.secrets: {e}")
            return

        # exchange refresh token for a fresh access token (string)
        try:
            gmail_access_token = get_access_token(refresh_token, client_id, client_secret)
        except Exception as e:
            st.error(f"Failed to obtain Gmail access token: {e}")
            return

        if not isinstance(gmail_access_token, str) or not gmail_access_token:
            st.error("Could not obtain a valid Gmail access token. Check secrets/client_secret.json and network.")
            return

        # Compose simple email
        subject = f"Hello {patient_name}, test email"
        body = f"""Hello, this is a periodic follow-up form to help monitor the patient’s health.

            Are you feeling any discomfort or unusual symptoms in the past few days?

            Has your blood pressure been high, low, or normal recently?

            Have you experienced headaches, dizziness, or fatigue in the past few weeks?

            Are you taking your medication correctly every day?

            Have you had shortness of breath, swelling, or chest pain?
            How has your sleep been? 

            Have you been sleeping well?

            Have you noticed any change in appetite or weight?

            How would you describe your level of stress or anxiety lately?

            Have you had any falls, loss of balance, or difficulty moving around?

            Sincerely,
            XteF Clinic"""

        input_data = GmailSendInput(
            to=email_dest,
            subject=subject,
            body=body,
            access_token=gmail_access_token
        )

        try:
            result = send_gmail_email(input_data)
            st.success(f"Email successfully sent to {email_dest}!")
            st.write("Subject:", result)
        except Exception as e:
            st.error(f"Failed to send email: {e}")

    # -----------------------------
    # ICS CALENDAR INVITE
    # -----------------------------
    if schedule_followup and st.button("Enviar convite de consulta"):
        if not (followup_date and followup_time):
            st.error("Selecione uma data e hora para a consulta.")
            return

        # Obtain fresh access token
        #API verificar tokens
        try:
 
            refresh_token = kc.load_from_streamlit(st).get("GMAIL_REFRESH_TOKEN")
            client_id = kc.load_from_streamlit(st).get("GMAIL_CLIENT_ID")
            client_secret = kc.load_from_streamlit(st).get("GMAIL_CLIENT_SECRET")
            gmail_access_token = get_access_token(refresh_token, client_id, client_secret)
        except Exception as e:
            st.error(f"Could not obtain Gmail access token: {e}")
            return

        if not isinstance(gmail_access_token, str) or not gmail_access_token:
            st.error("Could not obtain a valid Gmail access token for calendar invite.")
            return

        start_dt = datetime.combine(followup_date, followup_time)
        end_dt = start_dt + timedelta(minutes=30)

        start_iso = start_dt.strftime("%Y%m%dT%H%M%S")
        end_iso = end_dt.strftime("%Y%m%dT%H%M%S")

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start_iso}
DTEND:{end_iso}
SUMMARY:Follow-up Appointment
DESCRIPTION:Scheduled follow-up consultation.
END:VEVENT
END:VCALENDAR
"""
        ics_b64 = base64.b64encode(ics_content.encode("utf-8")).decode("utf-8")

        payload = GmailSendWithAttachmentInput(
            to=email_dest,
            subject="Your appointment",
            body="Please find your calendar invitation attached.",
            access_token=gmail_access_token,
            attachment_bytes_base64=ics_b64,
            attachment_filename="appointment.ics"
        )

        try:
            send_gmail_email_with_ics(payload)
            st.success("Appointment invite sent successfully!")
        except Exception as e:
            st.error(f"Failed to send calendar invite: {e}")

    

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
        #ai_suggestions = ia.process_text_with_ai(raw_text)

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

        # ============================
        # SALVAR PACIENTE NO FIREBASE
        # ============================
        try:
            an = DiaryAnalyzer()   # backend default não importa para salvar no firebase
            ok = an.save_patient(filled_data)

            if ok:
                st.success("✔ Patient information saved successfully to Firebase!")
            else:
                st.warning("⚠ Failed to save patient information to Firebase.")

        except Exception as e:
            st.error(f"Firebase error: {e}")

        # Mostrar JSON salvo
        st.write("### Saved JSON:")
        st.json(filled_data)


        st.session_state.patient_data = filled_data
        st.success("✔ Information saved successfully!")


