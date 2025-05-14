### 📂 AI-Powered File Categorizer & Organizer

**Supports:** PDF, Markdown (.md), and Images 🧠

This project uses **local LLMs (via LM Studio)** to categorize files (PDFs, Markdown, and Images), then organizes them into folders based on their content.

---

### 🧠 Powered by LM Studio (Local AI)

Make sure **LM Studio** is running and a model is served using the **OpenAI-compatible API**.

#### To enable the API in LM Studio:

1. Launch LM Studio.
2. Load a model (e.g., `gemma-3`, `mistral`, etc.).
3. Go to the **Server** tab.
4. Copy the **model name** and **API URL**, and add them to your `config.json`.

---

### 🔧 Requirements

```bash
pip install -r requirements.txt
```

---

### ⚙️ Configuration (`config.json`)

```json
{
    "path": "path-to-your-files",
    "json_path": "Path/output_file_info.json",
    "pages": 3,
    "model_name": "your-model-name",
    "api_url": "http://localhost:1234/v1/chat/completions",
    "api_key": "<API_KEY>",
    "prompt": "\"{file_name}\" , \"{title}\" , \"{text}\" Based on this information, determine the category for this document. It should be a single word in English. Example: Engineering, Computer etc."
}
```

---

### 📁 Step 1: Categorize Files

Run one or more of the following categorizers depending on the file type:

#### 📄 PDF Files

```bash
python pdfCategorizer.py
```

→ Generates `pdf_file_info.json`

#### 📝 Markdown Files

```bash
python mdCategorizer.py
```

→ Generates `md_file_info.json`

#### 🖼️ Image Files

⚠️ Requires a model that supports image input (e.g., `gemma-3-12b-4b`)

```bash
python imgCategorizer.py
```

→ Generates `img_file_info.json`

---

### 📂 Step 2: Organize Files

After categorizing, set `"json_path"` in your `config.json` to the relevant `.json` file created, then run:

```bash
python Organizer.py
```

Files will be moved into folders based on their detected category.

---

### ✅ Example Workflow

1. Start LM Studio and load your model.
2. Categorize files:

   * `python pdfCategorizer.py`
   * `python mdCategorizer.py`
   * `python imgCategorizer.py`
3. Run the organizer for each JSON output:

   * Update `json_path` to match (`pdf_file_info.json`, etc.)
   * `python Organizer.py`

