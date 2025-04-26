### 📂 Categorizer & Organizer PDF file by AI

This project contains **two separate Python modules**:

1. **Categorizer** – Reads the pages of a PDF file up to the desired number of pages., extracts text and metadata, and uses an LLM API to generate a category (e.g., "Engineering", "Computer"). You can improve the model's categorization by tweaking the prompt.
2. **Organizer** – Organizes your PDF files into folders based on the predicted category from a generated JSON file.

---

### 🧠 Powered by LM Studio (Local AI)

This tool uses **LM Studio** as a local LLM backend.

> ⚠️ **Important:** Make sure LM Studio is running and a model is actively served through the **OpenAI-compatible API server**.

#### To enable the API in LM Studio:
1. Launch LM Studio.
2. Load your model (e.g., `gemma-3`, `mistral`, etc.)
3. Go to **Server** tab.
4. Copy the **Model name** and place it in your `config.json`.
5. Copy the **API URL** (e.g., `http://localhost:1234/v1/chat/completions`) and place it in your `config.json`.

---

### 🔧 Requirements

Install required libraries:

```bash
pip install -r requirements.txt
```

---

### ⚙️ Configuration File

You need a `config.json` file like this:

```json
{
    "path": "path-pdf-files",
    "json_path": "Path/pdf_file_info.json",
    "pages": 3,
    "model_name": "your-model-name",
    "api_url": "http://localhost:1234/v1/chat/completions",
    "api_key": "<API_KEY>",
    "prompt": "\"{file_name}\" , \"{title}\" , \"{text}\" Based on this information, determine the category for this document. It should be a single word in English. Example: Engineering, Computer etc."
}
```

---

### 📁 Module 1: PDF Categorizer

**Location:** `Categorizer.py`  
**Function:**  
- Reads all PDFs in the given folder.
- Extracts title and first N pages.
- Sends a prompt to LM Studio's API.
- Saves results in `pdf_file_info.json`.

---

### 📁 Module 2: File Organizer

**Location:** `Organizer.py`  
**Function:**  
- Reads `pdf_file_info.json`.
- Moves each file into its respective category folder.

---

### ▶️ How to Use

1. **Start LM Studio and enable the API server.**
2. **Adjust the configuration file**
3. **Run the categorizer:**

```bash
python Categorizer.py
```

This will create `pdf_file_info.json`.

3. **Run the organizer:**

```bash
python Organizer.py
```
