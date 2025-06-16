import pandas as pd
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import config

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found in environment or .env file.")
    exit()
else:
    genai.configure(api_key=api_key)

def translate_nepali_to_english_batch(texts_to_translate):
    if not texts_to_translate:
        return []

    try:
        model = genai.GenerativeModel(config.MODEL)
        input_texts_formatted = "\n".join([f"Item {i+1}: {text}" for i, text in enumerate(texts_to_translate)])

        prompt = (
            "You are given a list of Nepali sentences. For each item, translate it to English.\n"
            "Detect and extract any named or location entities in both Nepali and English versions.\n"
            "Return the result as a JSON list, where each object contains the following keys:\n"
            "- sentence: the original Nepali sentence\n"
            "- matched_locations: a list of matched location/entity names in the Nepali sentence\n"
            "- translated_sentence_en: the English translation of the sentence\n"
            "- matched_locations_en: the corresponding location/entity names in English\n\n"
            f"Input:\n{input_texts_formatted}\n\n"
            "Output format:\n[\n"
            "  {\n"
            "    \"sentence\": \"...\",\n"
            "    \"matched_locations\": [\"...\", \"...\"],\n"
            "    \"translated_sentence_en\": \"...\",\n"
            "    \"matched_locations_en\": [\"...\", \"...\"]\n"
            "  },\n"
            "  ...\n"
            "]\n"
            "Be accurate, do not hallucinate locations or translations. Keep formatting strict JSON."
        )

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        print(f"Received response: {result_text[:1000]}...") 

        # Save raw Gemini response for inspection
        with open("debug_response.txt", "a", encoding="utf-8") as debug_file:
            debug_file.write(result_text + "\n\n")

        # Parse response
        parsed = json.loads(result_text)

        # Append to single file
        output_path = "/home/nabin/Desktop/Allprojects/POS-tagger/POS-Tagger/location_translator/final_output/translated.json"
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        existing.extend(parsed)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print(f"Appended {len(parsed)} records to '{output_path}'. Total items: {len(existing)}")

        return parsed

    except Exception as e:
        print(f"Error: {e}")
        return [{"sentence": s, "translated_sentence_en": f"API Error: {e}", "matched_locations": [], "matched_locations_en": []} for s in texts_to_translate]


if __name__ == "__main__":
    try:
        df = pd.read_csv(config.INPUT_CSV_PATH)
        if config.ROW_END is not None:
            df = df.iloc[config.ROW_START:config.ROW_END]
        else:
            df = df.iloc[config.ROW_START:]

        sentences = df['sentence'].astype(str).tolist()
        print(f"Loaded {len(sentences)} sentences for translation.")
        translate_nepali_to_english_batch(sentences)

    except FileNotFoundError:
        print(f"File not found: {config.INPUT_CSV_PATH}")
    except KeyError as ke:
        print(f"Missing column: {ke}")
    except Exception as e:
        print(f"Unexpected error: {e}")
