import json
import sys
from src.Diary import DiaryAnalyzer

project_id = "cf0f0ec9-62ec-4191-92e0-0c07d15a5fb0"


#API Mudar para st.secrets
def load_apikey():
    from KeyChain import KeyChain
    kc = KeyChain()
    keys = kc.load_from_env(st)
    return keys.get("WATSONX_APIKEY")


def main():
    apikey = load_apikey()


    an = DiaryAnalyzer(
        backend="watsonx",
        watsonx_api_key=apikey,
        watsonx_project_id=project_id
    )

    # Generate summary aggregating all pages in database/
    summary = an.summarize_case(save_to_file=True, save_to_firebase=False)

    print("\n--- SUMMARY GENERATED ---\n")
    print(summary)


if __name__ == '__main__':
    main()
