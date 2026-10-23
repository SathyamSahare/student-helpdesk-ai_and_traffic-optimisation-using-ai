# CEC Student Helpdesk AI — Minor Project (City Engineering College, Bengaluru)

AI chatbot that answers student queries on admissions, courses, fees, scholarships, internships and placements.

## Pipeline (maps to the project steps)
| Step | Where |
|---|---|
| 1 Scope | 15 intents + greeting/goodbye/thanks/out_of_scope (`data/intents.csv`) |
| 2 Collect data | `data/intents.csv` (training phrasings) + `data/responses.json` (answers) |
| 3 Clean & normalize | `chatbot.clean()` — lowercase, punctuation removal, stopword removal |
| 4 Vectorize | TF-IDF word 1–2 grams + character 3–5 grams (typo tolerant) |
| 5 Approach | NLP-based (not rule-based) |
| 6 Train model | Logistic Regression intent classifier (`python chatbot.py`) |
| 7 Response mapping | intent → answer dictionary in `responses.json`, confidence threshold + fallback |
| 8 Interface | Streamlit web UI (`app.py`): topic cards, quick questions, chat, clear-chat button |
| 9 API integration | FastAPI backend (`api.py`, `POST /chat`); UI calls it via `API_URL` |
| 10 Test & deploy | `evaluate.py`, `test_api.py`, `render.yaml` |

## Plain-word glossary
| Technical term | Plain meaning |
|---|---|
| Vectorize | Turn words into numbers |
| TF-IDF | Give each word an importance score (a word seen in only a few question types scores high, a common word scores low) |
| Word n-grams | Look at single words and word pairs |
| Character n-grams | Look at small letter pieces inside words, so spelling mistakes still work |
| Intent | The topic of the question (fees, admission, ...) |
| Intent classification | Guess which topic a question belongs to |
| Logistic Regression | The learner that studies the examples and decides the topic |
| Confidence | How sure the bot is (0 to 1) |
| Threshold | Minimum sureness needed to answer (0.30) |
| Fallback | The "Sorry, I'm not sure" reply |
| Response mapping | A lookup table from topic to ready-made answer |
| Out-of-scope | A question that is not about college |
| Backend API | A separate program that receives a question and returns the answer |

**How it works in plain words:** the student types a question -> the bot cleans it -> turns it into numbers by scoring words and letter pieces -> guesses the topic and how sure it is -> if sure enough, returns the saved answer for that topic, otherwise says "Sorry, I'm not sure".

## Run locally
```
pip install -r requirements.txt
python chatbot.py                # train -> model.joblib
uvicorn api:app --reload         # backend on :8000  (docs at /docs)
# new terminal (Windows PowerShell: $env:API_URL="http://localhost:8000")
API_URL=http://localhost:8000 streamlit run app.py
```
Without `API_URL`, the UI runs the model in-process (single-service deployment).

## Evaluate / test
```
python evaluate.py     # CV accuracy + held-out test set + per-intent report
pytest -q              # API tests
```
Latest results: 66-question held-out set (typos + 8 off-topic) = **95.5% (63/66)**, all off-topic rejected.
Caveat: the test set was written by the same author as the training data, so real-world accuracy will be lower. Add real student questions to improve it.

## Deploy
- **Backend:** push to GitHub → Render → New Web Service (uses `render.yaml`). Note the URL.
- **Frontend:** Streamlit Community Cloud → main file `app.py` → Secrets/env: `API_URL = "https://<your-render-url>"`.
- Or deploy only the Streamlit app with no `API_URL` (local model).

## College data (source: cityengineeringcollege.ac.in, collected Oct 2026)
`data/responses.json` now holds real City Engineering College information: address, phone numbers, programmes,
2026-27 first-year B.E. fees (CET and CET-SNQ seats), placement statistics 2019-2023, and links to the official pages.
Every answer carries a `source_url`. Re-check before submission, because websites change:
- Management / COMEDK fees vary by branch: they are NOT in the bot, only a pointer to the fee PDF.
- Placement statistics page was last updated in 2024 (latest year shown: 2023).
- Admission dates, documents, eligibility and scholarships were not published on the pages checked. The bot says so and gives the helpline.
- Answers with `"verified": false` show a warning in the UI (currently: scholarships).
Add real student questions to `data/intents.csv` and re-run `python chatbot.py` to improve accuracy.

## Limitations
Retrieval-style intent classifier, not generative: it can misclassify unusual phrasings, and has no multi-turn memory.
