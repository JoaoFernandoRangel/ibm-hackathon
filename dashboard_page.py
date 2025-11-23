import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================================
# FAKE DATA – hardcoded apenas para exibição
# Estrutura simulada após processamento dos PDFs
# ============================================================
FAKE_LAB_DATA = {
    "Hemograma": [
        {"test": "Hemoglobina", "value": 14.1, "unit": "g/dL", "date": "2024-01-10"},
        {"test": "Hemoglobina", "value": 13.7, "unit": "g/dL", "date": "2024-03-21"},
        {"test": "Hemoglobina", "value": 14.4, "unit": "g/dL", "date": "2024-07-18"},

        {"test": "Plaquetas", "value": 220, "unit": "mil/mm³", "date": "2024-01-10"},
        {"test": "Plaquetas", "value": 205, "unit": "mil/mm³", "date": "2024-03-21"},
        {"test": "Plaquetas", "value": 230, "unit": "mil/mm³", "date": "2024-07-18"},
    ],
    "Bioquímica": [
        {"test": "Glicose", "value": 92, "unit": "mg/dL", "date": "2024-02-15"},
        {"test": "Glicose", "value": 105, "unit": "mg/dL", "date": "2024-04-12"},
        {"test": "Glicose", "value": 99, "unit": "mg/dL", "date": "2024-08-01"},

        {"test": "Creatinina", "value": 0.91, "unit": "mg/dL", "date": "2024-02-15"},
        {"test": "Creatinina", "value": 1.02, "unit": "mg/dL", "date": "2024-04-12"},
        {"test": "Creatinina", "value": 0.97, "unit": "mg/dL", "date": "2024-08-01"},
    ],
    "Lipidograma": [
        {"test": "LDL", "value": 132, "unit": "mg/dL", "date": "2024-01-09"},
        {"test": "LDL", "value": 145, "unit": "mg/dL", "date": "2024-04-03"},
        {"test": "LDL", "value": 138, "unit": "mg/dL", "date": "2024-09-20"},

        {"test": "HDL", "value": 48, "unit": "mg/dL", "date": "2024-01-09"},
        {"test": "HDL", "value": 52, "unit": "mg/dL", "date": "2024-04-03"},
        {"test": "HDL", "value": 50, "unit": "mg/dL", "date": "2024-09-20"},
    ],
}


# ============================================================
# Helper: Detecta a unidade de um exame
# ============================================================
def detect_unit(test_name: str, df: pd.DataFrame) -> str:
    units = df[df["test"] == test_name]["unit"].unique()
    return units[0] if len(units) > 0 else ""


# ============================================================
# Helper: Gera um gráfico matplotlib e retorna a figura
# ============================================================
def generate_line_plot(df: pd.DataFrame, test_name: str):
    df_test = df[df["test"] == test_name].copy()
    df_test["date"] = pd.to_datetime(df_test["date"])

    fig, ax = plt.subplots()
    ax.plot(df_test["date"], df_test["value"], marker="o")
    ax.set_title(f"{test_name} Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Value ({detect_unit(test_name, df)})")
    plt.xticks(rotation=45)

    return fig


# ============================================================
# MAIN DASHBOARD PAGE
# ============================================================
def dashboard_page():
    st.title("📊 Clinical Dashboard")
    st.write("Overview of processed lab results")

    # Converter FAKE_LAB_DATA em um único dataframe consolidado
    all_records = []
    for category, entries in FAKE_LAB_DATA.items():
        for entry in entries:
            entry["category"] = category
            all_records.append(entry)

    df = pd.DataFrame(all_records)

    st.subheader("📈 Lab Test Trend Charts")

    # =======================================================
    # GRÁFICOS LADO A LADO — 2 por linha
    # =======================================================
    unique_tests = df["test"].unique()

    for i in range(0, len(unique_tests), 2):
        cols = st.columns(2)

        # Primeiro gráfico da linha
        with cols[0]:
            fig = generate_line_plot(df, unique_tests[i])
            st.pyplot(fig)

        # Segundo gráfico, se existir
        if i + 1 < len(unique_tests):
            with cols[1]:
                fig = generate_line_plot(df, unique_tests[i + 1])
                st.pyplot(fig)

    # =======================================================
    # TABELAS — aparecem DEPOIS dos gráficos
    # =======================================================
    st.subheader("📄 Detailed Tables by Category")

    categories = df["category"].unique()

    # Translate some common Portuguese category names to English for display
    name_map = {
        "Hemograma": "Hematology",
        "Bioquímica": "Biochemistry",
        "Lipidograma": "Lipid Panel"
    }

    for cat in categories:
        display_cat = name_map.get(cat, cat)
        st.markdown(f"### 🧪 {display_cat}")
        cat_df = df[df["category"] == cat].copy()
        st.dataframe(cat_df, width='stretch')


def lab_dashboard_page():
    """Compat shim: manter nome antigo `lab_dashboard_page` usado em app.py.

    Apenas repassa a chamada para `dashboard_page()` para retrocompatibilidade.
    """
    return dashboard_page()
