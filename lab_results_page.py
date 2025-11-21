import streamlit as st
from typing import List, Dict
import IA_interactions as ia

# =====================================================================
# MAIN PAGE FUNCTION
# =====================================================================
def lab_results_page():

    st.subheader("Laboratory Exam Upload")

    # inicializa armazenamento de exames
    if "lab_results" not in st.session_state:
        st.session_state.lab_results = []   # lista de jsons

    # ==============================================================
    # 1) Upload múltiplo de PDFs
    # ==============================================================
    uploaded_files = st.file_uploader(
        "Upload laboratory exam PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info("Processing uploaded exams… (AI placeholder)")

        for file in uploaded_files:
            pdf_bytes = file.read()

            # Chamar IA (placeholder)
            exam_json = ia.process_pdf_with_ai(pdf_bytes, file.name)

            # adicionar na memória
            st.session_state.lab_results.append(exam_json)

        st.success("✔ Exams processed successfully!")

    st.markdown("---")

    # ==============================================================
    # 2) Navegação pelos exames já processados
    # ==============================================================
    if len(st.session_state.lab_results) == 0:
        st.warning("No processed lab exams yet.")
        return

    st.write("### Processed Exams")

    # lista dos nomes
    exam_names = [
        exam.get("exam_name", f"Exam {i}") 
        for i, exam in enumerate(st.session_state.lab_results)
    ]

    selected_exam = st.selectbox("Select an exam to view:", exam_names)

    # encontra o json correspondente
    for exam in st.session_state.lab_results:
        if exam.get("exam_name") == selected_exam:
            st.json(exam)
            break

