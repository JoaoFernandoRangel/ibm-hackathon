import streamlit as st
import IA_interactions as ia
# Schema fixo do formulário
FORM_SCHEMA = {
    "name": "text",
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
