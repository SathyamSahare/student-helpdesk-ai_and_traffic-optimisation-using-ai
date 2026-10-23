import argparse

import joblib
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

FEATURES = ["vehicles_in_roi", "occupancy"]


def weak_label(row):
    if row["vehicles_in_roi"] < 5 and row["occupancy"] < 0.10:
        return "LOW"
    if row["vehicles_in_roi"] >= 12 or row["occupancy"] >= 0.30:
        return "HIGH"
    return "MEDIUM"


def predict_density(count, occupancy, model_path="density_model.joblib"):
    model = joblib.load(model_path)
    X = pd.DataFrame([[count, occupancy]], columns=FEATURES)
    return model.predict(X)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="density_samples.csv")
    ap.add_argument("--out", default="density_model.joblib")
    a = ap.parse_args()

    df = pd.read_csv(a.data)
    if "label" not in df.columns or df["label"].isna().all():
        print("WARNING: no hand labels found; using weak rule-based labels.")
        df["label"] = df.apply(weak_label, axis=1)
    else:
        df = df.dropna(subset=["label"])   # use only the rows you labeled by hand
        print(f"Training on {len(df)} hand-labeled rows.")
    if df["label"].nunique() < 2 or len(df) < 20:
        raise SystemExit("Need at least 20 rows and 2 classes. Run the counter on a longer video.")

    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], df["label"], test_size=0.25, random_state=42,
        stratify=df["label"] if df["label"].value_counts().min() >= 2 else None)
    model = DecisionTreeClassifier(max_depth=4, random_state=42).fit(X_train, y_train)
    print(classification_report(y_test, model.predict(X_test), zero_division=0))
    joblib.dump(model, a.out)
    print(f"Saved {a.out}")


if __name__ == "__main__":
    main()
