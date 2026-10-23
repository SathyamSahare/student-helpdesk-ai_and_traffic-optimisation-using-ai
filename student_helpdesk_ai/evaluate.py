"""Evaluate intent detection and FAQ retrieval on the supplied labeled test set."""
import csv
from pathlib import Path
from chatbot import get_answer, load_knowledge_base

ROOT = Path(__file__).resolve().parent
TEST_FILE = ROOT / "data" / "test_questions.csv"

def main():
    faq_rows = load_knowledge_base()
    with TEST_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        tests = list(csv.DictReader(f))
    if not tests:
        print("No test questions found.")
        return
    intent_correct = 0
    faq_matched = 0
    for row in tests:
        result = get_answer(row["question"], faq_rows)
        intent_ok = result["intent"] == row["expected_intent"]
        intent_correct += int(intent_ok)
        faq_matched += int(bool(result["matched_question"]))
        print(f"[{'PASS' if intent_ok and result['matched_question'] else 'CHECK'}] {row['question']}")
        print(f"  expected={row['expected_intent']} | detected={result['intent']} | FAQ={result['matched_question'] or 'none'}")
    n = len(tests)
    print("\n" + "=" * 56)
    print(f"Intent accuracy on supplied test set: {intent_correct}/{n} ({intent_correct/n:.1%})")
    print(f"FAQ match rate: {faq_matched}/{n} ({faq_matched/n:.1%})")
    print("This small demonstration set is not a guarantee of real-world accuracy.")

if __name__ == "__main__":
    main()
