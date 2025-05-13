import os
import json
import base64
import requests
import sys
import io

# === Console Output UTF-8 ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# === LOAD CONFIGURATION ===
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CONFIG ERROR] Could not read config file: {e}")
        sys.exit(1)

config = load_config()
IMAGE_FOLDER_PATH = config.get("path")
MODEL_NAME = config.get("model_name")
LMSTUDIO_URL = config.get("api_url")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.get('api_key', '')}"  # may be empty
}
PROMPT_TEMPLATE = config.get("prompt", "What is the main topic of this document image? Respond with one English word.")
TEMPERATURE = config.get("temperature", 0.5)

# === SUPPORTED FORMATS ===
SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".jfif")

# === DETERMINE MIME TYPE ===
def get_mime_type(filename):
    ext = filename.lower().split(".")[-1]
    return {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "jfif": "image/jpeg"
    }.get(ext, "image/png")

# === CONVERT IMAGE TO BASE64 ===
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return encoded
    except Exception as e:
        print(f"[ERROR] Failed to read image: {image_path} -> {e}")
        return None

# === SEND REQUEST TO LLM ===
def ask_llm_with_image(b64_image, prompt, filename):
    mime = get_mime_type(filename)
    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_image}"}}
                ]
            }
        ],
        "temperature": TEMPERATURE
    }

    try:
        print(f"📤 Sending: {filename}...", flush=True)
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
        raw = response.json()['choices'][0]['message']['content'].strip()
        print(f"✅ Response received: {raw}", flush=True)
        return raw
    except Exception as e:
        print(f"[LLM ERROR] Error occurred for {filename} -> {e}", flush=True)
        return "unknown"

# === PROCESS ALL IMAGES ===
def process_images_and_save_json():
    print("📁 Scanning folder:", IMAGE_FOLDER_PATH)
    files = [f for f in os.listdir(IMAGE_FOLDER_PATH) if f.lower().endswith(SUPPORTED_EXTS)]

    results = []
    successful_files = []
    failed_files = []

    for file in files:
        print(f"{file}\n📷 Processing: ")
        file_path = os.path.join(IMAGE_FOLDER_PATH, file)

        # Convert image to base64
        b64_img = image_to_base64(file_path)
        if not b64_img:
            print(f"⚠️ Skipped (unreadable): {file}")
            failed_files.append(file)
            continue

        # Send to LLM and get category
        category = ask_llm_with_image(b64_img, PROMPT_TEMPLATE, file)

        results.append({
            "file_name": file,
            "category": category
        })
        successful_files.append(file)
        print(f"💾 Added to JSON: {file}\n")

    # Save as JSON
    with open("img_file_info.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    # Summary
    print("\n✅ Process completed!")
    print("📊 Successfully categorized files:")
    for f in successful_files:
        print("  ✅", f)

    if failed_files:
        print("\n⚠️ Failed files:")
        for f in failed_files:
            print("  ❌", f)

# === MAIN ===
if __name__ == "__main__":
    process_images_and_save_json()
