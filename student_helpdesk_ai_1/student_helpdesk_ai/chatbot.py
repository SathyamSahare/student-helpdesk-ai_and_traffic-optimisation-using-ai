"""Student helpdesk chatbot, explained in plain words.

How it works:
  1. Clean the question          (lowercase, remove symbols and filler words)
  2. Turn the text into numbers  (give each word / letter piece an importance score)
  3. Guess the topic             (fees, admission, internships ... plus how sure we are)
  4. Reply with the saved answer for that topic, or say "Sorry, I'm not sure"
"""
import csv, json, re
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer   # "importance score" maker (TF-IDF)
from sklearn.linear_model import LogisticRegression            # the learner that decides the topic
from sklearn.pipeline import FeatureUnion, Pipeline

BASE = Path(__file__).parent

# Filler words that don't help us find the topic.
FILLER_WORDS = {"a","an","the","is","are","am","do","does","did","to","of","in","on","at","for","and","or","me","my","i","you","your","can","could","please","tell","about","there","it","this","that","be","how","what","which","where","when","who","whom","will","should","would","any","some","get","have","has","with","from","by","as"}
# Question words that DO matter, so we keep them even though they look like filler.
KEEP_WORDS = {"how","what","when","where","who","whom","which","last","pay"}

def clean_text(text: str) -> str:
    """Step 1: lowercase, remove symbols, remove extra spaces, remove filler words."""
    text = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()
    words = [w for w in text.split() if w not in FILLER_WORDS or w in KEEP_WORDS]
    return " ".join(words)

def build_model() -> Pipeline:
    """Step 2 + 3: the number-maker and the topic-guesser, joined together."""
    number_maker = FeatureUnion([
        # Scores single words and word pairs (e.g. "last date")
        ("words", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        # Scores small letter pieces inside words, so spelling mistakes like "admision" still work
        ("letter_pieces", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
    ])
    topic_guesser = LogisticRegression(C=20, max_iter=2000, class_weight="balanced")
    return Pipeline([("number_maker", number_maker), ("topic_guesser", topic_guesser)])

def load_training_data(path=BASE / "data" / "intents.csv"):
    """Read example questions (data/intents.csv) and the topic each one belongs to."""
    questions, topics = [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["text"].strip():
                questions.append(clean_text(row["text"]))
                topics.append(row["intent"].strip())
    return questions, topics

class HelpdeskBot:
    def __init__(self, min_sureness=0.30, model_path=BASE / "model.joblib"):
        self.min_sureness = min_sureness          # if the bot is less sure than this, it says "Sorry"
        config = json.loads((BASE / "data" / "responses.json").read_text(encoding="utf-8"))
        self.saved_answers = config["intents"]    # topic -> ready-made answer
        self.sorry_message = config["fallback"]
        model_path = Path(model_path)
        if model_path.exists():
            self.model = joblib.load(model_path)  # reuse the already-trained model
        else:
            questions, topics = load_training_data()
            self.model = build_model().fit(questions, topics)   # learn from the examples
            joblib.dump(self.model, model_path)
        self.topics = list(self.model.classes_)

    def guess_topic(self, text: str):
        """Return (topic, sureness). Topic is None if the question is off-topic or the bot is unsure."""
        cleaned = clean_text(text)
        if not cleaned:
            return None, 0.0
        sureness_per_topic = self.model.predict_proba([cleaned])[0]
        best = int(sureness_per_topic.argmax())
        topic, sureness = self.topics[best], float(sureness_per_topic[best])
        if topic == "out_of_scope" or sureness < self.min_sureness:
            return None, sureness
        return topic, sureness

    def answer(self, text: str) -> dict:
        """Step 4: find the topic, then reply with its saved answer (or the 'Sorry' message)."""
        if not text or not text.strip():
            return {"answer": "Please type a question so I can help.", "intent": None, "confidence": 0.0}
        topic, sureness = self.guess_topic(text)
        if topic is None:
            return {"answer": self.sorry_message, "intent": None, "confidence": round(sureness, 3)}
        saved = self.saved_answers[topic]
        reply = saved["answer"]
        if saved.get("source_url"):
            reply += f"\n\nOfficial source: {saved['source_url']}"
        return {"answer": reply, "intent": topic, "confidence": round(sureness, 3),
                "verified": saved.get("verified", False)}

def train(model_path=BASE / "model.joblib"):
    """Learn from data/intents.csv and save the result to model.joblib."""
    questions, topics = load_training_data()
    model = build_model().fit(questions, topics)
    joblib.dump(model, model_path)
    return model

if __name__ == "__main__":
    train()
    print("Model trained and saved to model.joblib")
