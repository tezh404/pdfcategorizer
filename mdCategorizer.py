import json
import os
import re
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
        print(f"Could not read config file: {e}")
        sys.exit(1)

config = load_config()
MD_FOLDER_PATH = config.get("path")  # Path to Markdown files
NUM_PAGES_TO_READ = config.get("pages", 5)  # Number of lines to read (not pages in Markdown context)
MODEL_NAME = config.get("model_name")
LMSTUDIO_URL = config.get("api_url")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.get('api_key')}"
}
PROMPT_TEMPLATE = config.get("prompt", "\"{file_name, title, text}\" Based on this information, determine the category for this document. It should be a single word in English. Example: Engineering, Computer etc.")
TEMPERATURE = config.get("temperature", 0.5)

# Markdown text cleaning function
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = text.strip()  # Remove leading/trailing whitespace
    return text

# Extract text from the first few lines of a Markdown file
def extract_first_x_lines(file_path, line_count):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            text = ''.join(lines[:min(line_count, len(lines))])
            return clean_text(text)
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

# Get the title from the Markdown file (typically the first line with a heading)
def get_md_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#'):
                title = first_line[1:].strip()
            else:
                title = "No Title Found"
            return title
    except Exception as e:
        print(f"Error reading Markdown file: {e}")
        return "No Title Found"

# Generate document category using LLM
def generate_category(file_name, title, text):
    prompt = PROMPT_TEMPLATE.format(file_name=file_name, title=title, text=text)
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE
    }

    try:
        print(f"📄 {file_name}\n📤 Sending to LLM... ", flush=True)
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
        raw_answer = response.json()['choices'][0]['message']['content'].strip()

        # Remove <think>...</think> block if it exists
        content = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()

        print(f"✅ Response received: {raw_answer}", flush=True)
        return content
    except Exception as e:
        print(f"[ERROR] {file_name} -> {str(e)}", flush=True)
        return "unknown"

# Process all Markdown files and save results to JSON
def process_files_and_save_json():
    md_files = [f for f in os.listdir(MD_FOLDER_PATH) if f.endswith(".md")]
    
    file_info = []
    successful_files = []
    failed_files = []

    for file in md_files:
        file_path = os.path.join(MD_FOLDER_PATH, file)
        title = get_md_title(file_path)
        text = extract_first_x_lines(file_path, NUM_PAGES_TO_READ)
        if not text:
            print(f"⚠️ Empty content, skipped: {file}", flush=True)
            failed_files.append(file)
            continue
        category = generate_category(file, title, text)
        file_info.append({
            "file_name": file,
            "title": title,
            "first_x_lines_text": text,
            "category": category
        })
        print(f"💾 Added to JSON: {file}\n", flush=True)
        successful_files.append(file)

    # Save to JSON file
    file_info_json = json.dumps(file_info, indent=4, ensure_ascii=False)
    with open("md_file_info.json", "w", encoding="utf-8") as json_file:
        json_file.write(file_info_json)

    # Print summary
    print("\n✅ Process Completed! Successfully Processed Files:")
    print("\n".join(["📄 " + file for file in successful_files]))

    if failed_files:
        print("\n⚠️ Failed Files:")
        print("\n".join(failed_files))

# Main
if __name__ == "__main__":
    process_files_and_save_json()
