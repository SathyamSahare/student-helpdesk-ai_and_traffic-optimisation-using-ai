"""Evaluation: (1) 5-fold cross-validation on training patterns, (2) hand-written held-out test set
incl. typos and out-of-scope questions. Writes test_results.csv."""
import csv
from collections import Counter
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report
from chatbot import HelpdeskBot, build_model, load_training_data, BASE

X, y = load_training_data()
cv = cross_val_score(build_model(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
print(f"5-fold CV accuracy on training patterns: {cv.mean()*100:.1f}% (+/- {cv.std()*100:.1f})\n")

bot = HelpdeskBot(model_path=BASE / "model.joblib")
tests = list(csv.DictReader(open(BASE / "data" / "test_questions.csv", encoding="utf-8-sig")))
rows, y_true, y_pred = [], [], []
for t in tests:
    pred, conf = bot.guess_topic(t["question"])
    pred = pred or "OUT_OF_SCOPE"
    exp = t["expected_intent"].strip()
    y_true.append(exp); y_pred.append(pred)
    rows.append({"question": t["question"], "expected": exp, "predicted": pred,
                 "confidence": round(conf, 3), "passed": pred == exp})
with open("test_results.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

ok = sum(r["passed"] for r in rows)
print(f"Held-out test set: {ok}/{len(rows)} correct = {ok/len(rows)*100:.1f}%")
oos = [r for r in rows if r["expected"] == "OUT_OF_SCOPE"]
print(f"  Out-of-scope rejected correctly: {sum(r['passed'] for r in oos)}/{len(oos)}")
print("\nPer-intent report:\n", classification_report(y_true, y_pred, zero_division=0))
print("Misclassified:")
for r in rows:
    if not r["passed"]:
        print(f"  '{r['question']}': expected {r['expected']}, got {r['predicted']} ({r['confidence']})")
