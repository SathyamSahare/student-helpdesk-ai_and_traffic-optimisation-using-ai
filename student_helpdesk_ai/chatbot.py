"""Keyword-based FAQ matching. No TF-IDF, cosine similarity, or scikit-learn."""
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "college_faq.csv"

STOP_WORDS = set("""
a an and are as at be by can do does for from how i in is it me my of on or
please tell the there to what when where which who why with you your about much many
give show want know could would like
""".split())

INTENT_KEYWORDS = {
    "scholarships": {"scholarship", "scholarships", "financial", "aid", "concession", "reimbursement", "grant"},
    "contact": {"contact", "phone", "telephone", "email", "address", "location", "office", "reach", "visit", "map", "number"},
    "admissions": {"admission", "admissions", "apply", "application", "eligibility", "eligible", "document", "documents", "enroll", "enrollment", "join"},
    "courses": {"course", "courses", "program", "programs", "branch", "branches", "degree", "engineering", "undergraduate", "postgraduate", "mtech", "mba", "btech"},
    "fees": {"fee", "fees", "tuition", "payment", "pay", "installment", "installments", "cost", "amount"},
    "internships": {"internship", "internships", "intern", "training", "industry", "industrial"},
    "placements": {"placement", "placements", "placed", "job", "jobs", "career", "recruitment", "company", "companies", "salary", "package", "recruiters"},
    "college_info": {"college", "website", "official", "details", "information"},
}

def normalize_text(text):
    """Lowercase, remove punctuation, and normalize whitespace."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text):
    return [word for word in normalize_text(text).split() if word not in STOP_WORDS]

def load_knowledge_base(path=DATA_FILE):
    if not path.exists():
        raise FileNotFoundError(f"FAQ dataset not found: {path}. Check data/college_faq.csv.")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"intent", "question", "keywords", "answer", "source_url"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV columns required: intent, question, keywords, answer, source_url")
        return [dict(row) for row in reader]

def detect_intent(question):
    words = set(tokenize(question))
    best_intent, best_score = "unknown", 0
    for intent, keywords in INTENT_KEYWORDS.items():
        score = len(words.intersection(keywords))
        if score > best_score:
            best_intent, best_score = intent, score
    return best_intent

def get_answer(question, knowledge_base=None):
    cleaned = normalize_text(question)
    if not cleaned:
        return {"answer": "Please type a question about admissions, courses, fees, scholarships, internships, or placements.",
                "intent": "unknown", "matched_question": "", "confidence": 0.0, "source_url": ""}
    rows = knowledge_base if knowledge_base is not None else load_knowledge_base()
    intent = detect_intent(cleaned)
    words = set(tokenize(cleaned))
    candidates = [r for r in rows if r.get("intent") == intent] or rows
    best_row, best_score = None, 0
    for row in candidates:
        faq_text = " ".join([row.get("question", ""), row.get("keywords", ""), row.get("intent", "").replace("_", " ")])
        faq_words = set(tokenize(faq_text))
        score = len(words.intersection(faq_words))
        if score > best_score:
            best_row, best_score = row, score
    if best_row and best_score > 0:
        return {"answer": best_row.get("answer", ""), "intent": best_row.get("intent", intent),
                "matched_question": best_row.get("question", ""),
                "confidence": round(best_score / max(len(words), 1), 2),
                "source_url": best_row.get("source_url", "")}
    fallback = {
        "admissions": "I couldn't match that admissions question. Check the official admissions information or contact the admissions office.",
        "courses": "I couldn't match that course question. Check the official programs list for current offerings.",
        "fees": "I couldn't match that fee question. Please confirm current amounts with the college office.",
        "scholarships": "I couldn't match that scholarship question. Contact the college office for current eligibility and deadlines.",
        "internships": "I couldn't match that internship question. Contact the placement or training department.",
        "placements": "I couldn't match that placement question. Contact the placement department for current information.",
        "contact": "Please use the college's official website to confirm current contact details and address.",
        "college_info": "Please check the college's official website for current information.",
        "unknown": "Sorry, I couldn't find a suitable answer. Try keywords such as admission documents, course list, fees, scholarships, internships, or placements."
    }
    return {"answer": fallback.get(intent, fallback["unknown"]), "intent": intent,
            "matched_question": "", "confidence": 0.0, "source_url": ""}
