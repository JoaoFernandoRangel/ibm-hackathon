import json, os
from src.Diary import DiaryAnalyzer
from segredos.watson_api import project_id

#API mudar para st.secrets
# load apikey
with open('segredos/apikey.json','r',encoding='utf-8') as f:
    apikey = json.load(f).get('apikey')

an = DiaryAnalyzer(backend='watsonx', watsonx_api_key=apikey, watsonx_project_id=project_id)

form_data = {
    'name': 'João Silva',
    'age': 45,
    'gender': 'Male',
    'height_cm': 175,
    'weight_kg': 85,
    'allergies': 'Nenhuma',
    'current_medications': 'Losartana 50mg',
    'past_illnesses': 'Hipertensão',
    'family_medical_history': 'Pai com diabetes',
    'chief_complaint': 'Dor torácica intermitente',
    'pain_scale_0_to_10': 4,
    'symptoms_description': 'Dor desconfortável no lado esquerdo do peito há 2 dias, piora aos esforços.',
    'chronic_conditions': 'Hipertensão',
}

print('\n[TEST] Chamando generate_pre_prontuario via watsonx...')
result = an.generate_pre_prontuario(form_data)

os.makedirs('results', exist_ok=True)
out_path = os.path.join('results','pre_prontuario_watsonx.json')
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2)

print('\nResultado salvo em:', out_path)
print(json.dumps(result, ensure_ascii=False, indent=2))
