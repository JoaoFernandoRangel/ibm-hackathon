import json
import sys
from src.Diary import DiaryAnalyzer
from segredos.watson_api import project_id


def load_apikey():
    try:
        with open("segredos/apikey.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("apikey")
    except Exception as e:
        print(f"Error reading apikey: {e}")
        return None


def main():
    apikey = load_apikey()
    if not apikey:
        print("API key not found in segredos/apikey.json")
        sys.exit(1)

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
