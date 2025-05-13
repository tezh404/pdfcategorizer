import json
import os
import re
import fitz
import requests
import sys
import io

# Console output encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === LOAD CONFIGURATION ===
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Could not read config file: {e}", flush=True)
        sys.exit(1)

config = load_config()
PDF_FOLDER_PATH = config.get("path")
NUM_PAGES_TO_READ = config.get("pages", 5)
MODEL_NAME = config.get("model_name")
LMSTUDIO_URL = config.get("api_url")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.get('api_key')}"
}
PROMPT_TEMPLATE = config.get(
    "prompt",
    "\"{file_name, title, text}\" Based on this information, determine the category for this document. It should be a single word in English. Example: Engineering, Computer etc."
)
TEMPERATURE = config.get("temperature", 0.5)

# PDF cleaning function
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\n", " ").replace("\r", "")
    text = re.sub(r'[^\w\sçÇğĞıİöÖşŞüÜ]', '', text)
    text = text.strip()
    return text

# Extract first X pages
def extract_first_x_pages(file_path, page_count):
    try:
        doc = fitz.open(file_path)
        text = ""
        for i in range(min(page_count, doc.page_count)):
            page = doc.load_page(i)
            text += page.get_text()
        return clean_text(text)
    except Exception as e:
        print(f"❌ Error (reading pages): {file_path} -> {e}", flush=True)
        return ""

# Get PDF metadata (title)
def get_pdf_title(file_path):
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        title = metadata.get("title", "No Title Found")
        return title
    except Exception as e:
        print(f"❌ Error (reading title): {file_path} -> {e}", flush=True)
        return "No Title Found"

# Generate category
def generate_category(file_name, title, text):
    prompt = PROMPT_TEMPLATE.format(file_name=file_name, title=title, text=text)
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE
    }

    try:
        print(f"📤 Sending to LLM...", flush=True)
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
        raw_answer = response.json()['choices'][0]['message']['content'].strip()
        print(f"✅ Response received: {raw_answer}", flush=True)
        return raw_answer
    except Exception as e:
        print(f"❌ Error (LLM response): {file_name} -> {e}", flush=True)
        return "unknown"

# Process files and save to JSON
def process_files_and_save_json():
    pdf_files = [f for f in os.listdir(PDF_FOLDER_PATH) if f.endswith(".pdf")]
    
    file_info = []
    successful_files = []
    failed_files = []

    for file in pdf_files:
        print(f"\n📄 Processing: {file}", flush=True)
        file_path = os.path.join(PDF_FOLDER_PATH, file)
        title = get_pdf_title(file_path)
        text = extract_first_x_pages(file_path, NUM_PAGES_TO_READ)
        
        if not text:
            print(f"⚠️ Empty content, skipped: {file}", flush=True)
            failed_files.append(file)
            continue

        category = generate_category(file, title, text)
        file_info.append({
            "file_name": file,
            "title": title,
            "first_x_pages_text": text,
            "category": category
        })
        print(f"💾 Added to JSON: {file}", flush=True)
        successful_files.append(file)

    # Save to file
    with open("pdf_file_info.json", "w", encoding="utf-8") as json_file:
        json.dump(file_info, json_file, indent=4, ensure_ascii=False)

    # Summary
    print("\n✅ Process Completed! Successfully Processed Files:")
    print("\n".join(["📄 " + f for f in successful_files]))

    if failed_files:
        print("\n⚠️ Files Failed to Process:")
        print("\n".join(["❌ " + f for f in failed_files]))

# Main
if __name__ == "__main__":
    process_files_and_save_json()
