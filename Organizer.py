import os
import json
import shutil
import sys
import io

# Ensure UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load config from config.json
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load config file: {e}")
        return {}

# Read the JSON file
def read_json_file(json_file_path):
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return []

# Generate a unique filename if file already exists
def get_unique_filename(folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base} ({counter}){ext}"
        counter += 1

    return new_filename

# Organize files into folders by category
def organize_files_by_category():
    config = load_config()
    json_file_path = config.get("json_path")
    source_folder = config.get("path")

    if not json_file_path or not source_folder:
        print("Config file must include 'json_path' and 'path'.")
        return

    file_list = read_json_file(json_file_path)
    if not file_list:
        print("No data found in the JSON file.")
        return

    for item in file_list:
        file_name = item.get("file_name")
        category = item.get("category", "unknown").lower().strip()

        old_path = os.path.join(source_folder, file_name)
        category_folder = os.path.join(source_folder, category)

        if not os.path.exists(old_path):
            print(f"File not found: {old_path}")
            continue

        if not os.path.exists(category_folder):
            try:
                os.makedirs(category_folder)
                print(f"Created category folder: {category_folder}")
            except Exception as e:
                print(f"Failed to create category folder: {e}")
                continue

        # Ensure unique filename
        new_filename = get_unique_filename(category_folder, file_name)
        new_path = os.path.join(category_folder, new_filename)

        try:
            shutil.move(old_path, new_path)
            print(f"{file_name} -> moved to '{category}' folder as '{new_filename}'.")
        except Exception as e:
            print(f"Failed to move {file_name}: {e}")

# Main runner
if __name__ == "__main__":
    organize_files_by_category()
