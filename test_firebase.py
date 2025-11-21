# filepath: test_firebase.py

from src.Diary import DiaryAnalyzer

# 🔧 Configure aqui:
API_KEY = "SUA_API_KEY"
PROJECT_ID = "SEU_PROJECT_ID"

an = DiaryAnalyzer(
    backend="local",
    watsonx_api_key=API_KEY,
    watsonx_project_id=PROJECT_ID
)

# Texto de teste
texto = """
Hoje acordei muito triste. Falei com Ana.
Depois encontrei João e me senti menos triste.
"""

# Rodar teste
resultado = an.run_single_page(texto, page_name="pagina_teste")

print("\n===== RESULTADO PROCESSADO =====")
print(resultado)
print("\n✓ Verifique no Firestore -> diary_pages/pagina_teste\n")
