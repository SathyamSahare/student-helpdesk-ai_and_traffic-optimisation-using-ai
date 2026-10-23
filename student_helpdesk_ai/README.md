# Student Helpdesk AI — Keyword Matching Edition

A beginner-friendly Streamlit FAQ chatbot covering admissions, courses, fees, scholarships, internships, placements, and college contact information.

## Matching method

This project uses **keyword matching**, not TF-IDF or cosine similarity:
1. Normalize text to lowercase, remove punctuation, and standardize whitespace.
2. Detect a likely intent using manually defined keyword groups.
3. Compare the question's words with each FAQ's question, keywords, and intent.
4. Return the answer from the FAQ with the greatest keyword overlap.
5. If nothing matches, show a topic-specific fallback answer.

This is a rule-based retrieval chatbot, **not a trained machine-learning model**. The overlap score shown in the interface is only a rough indicator, not a calibrated probability.

## Files

```text
student_helpdesk_ai_keyword_matching/
├── app.py
├── chatbot.py
├── evaluate.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
└── data/
    ├── college_faq.csv
    └── test_questions.csv
```

## Windows setup (PowerShell)

1. Install Python 3.10+ from https://www.python.org/downloads/ and select **Add Python to PATH**.
2. Extract the ZIP.
3. Open the extracted project folder in File Explorer. Click its address bar, type `powershell`, and press Enter.
4. Confirm files exist:

   ```powershell
   Get-ChildItem
   Get-ChildItem .\data
   ```

5. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

6. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If activation says the file is missing, run `python -m venv .venv` from the project root again and check `Test-Path ".venv\Scripts\Activate.ps1"`.
   If PowerShell blocks scripts, for this window only run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

   You can also skip activation and use `.\.venv\Scripts\python.exe` in the commands below.

7. Install requirements:

   ```powershell
   python -m pip install --upgrade pip --timeout 120 --retries 5
   python -m pip install -r requirements.txt --timeout 120 --retries 5
   ```

8. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

   If you skipped activation:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

9. Open the local URL shown in PowerShell, usually `http://localhost:8501`. Stop the app with `Ctrl+C`.

## Evaluate the chatbot

Activate the virtual environment and run:

```powershell
python evaluate.py
```

This prints intent accuracy and FAQ match rate for the included labeled test questions. Review failed cases, add alternate words to the `keywords` column in `data/college_faq.csv`, and add representative student questions to `data/test_questions.csv`.

## Dataset notes

`data/college_faq.csv` columns: `intent`, `question`, `keywords`, `answer`, `source_url`.

Included answers are cautious sample guidance. The college website URL is provided as a starting reference, not a claim that every answer has been verified against a specific current page. **Before submitting or publishing, verify programs, admissions requirements, fees, contacts, scholarships, internships, and placement information using current official college sources.** Replace the source URLs with the exact pages you checked.

## Deploy with Streamlit Community Cloud

1. Upload the project files to a GitHub repository; do not upload `.venv`.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create an app, select your repository and branch, and set the main file to `app.py`.
4. Deploy. Streamlit installs the dependency in `requirements.txt`.
5. Test the deployed app with the questions in `data/test_questions.csv`.

This version needs no API key or separate backend API. Keep your repository public only if you are comfortable publishing the code and FAQ dataset.

## Troubleshooting

- **`Activate.ps1` missing:** Run `python -m venv .venv` from the project root and verify the file path.
- **`ConnectionResetError(10054)` during pip:** retry with `--timeout 120 --retries 5`; check network/proxy/VPN or try again later.
- **CSV not found:** ensure `data\college_faq.csv` exists beside the project files.
- **Weak answer matches:** add synonyms in the CSV `keywords` column and update `INTENT_KEYWORDS` in `chatbot.py`.
- **No trained model:** intentional for this version; intent detection is manually defined keyword logic.
