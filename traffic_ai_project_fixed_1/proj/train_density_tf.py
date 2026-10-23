
import argparse

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

from train_density_classifier import FEATURES, weak_label

CLASSES = ["LOW", "MEDIUM", "HIGH"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="density_samples.csv")
    ap.add_argument("--out", default="density_tf_model.keras")
    ap.add_argument("--epochs", type=int, default=60)
    a = ap.parse_args()

    df = pd.read_csv(a.data)
    if "label" not in df.columns or df["label"].isna().all():
        print("WARNING: no hand labels found; using weak rule-based labels.")
        df["label"] = df.apply(weak_label, axis=1)
    else:
        df = df.dropna(subset=["label"])
    if len(df) < 20:
        raise SystemExit("Need at least 20 labeled rows.")

    X = df[FEATURES].to_numpy("float32")
    y = df["label"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    norm = tf.keras.layers.Normalization()
    norm.adapt(X_train)
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(len(FEATURES),)),
        norm,
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(3, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.fit(X_train, y_train, epochs=a.epochs, batch_size=16, verbose=0,
              validation_data=(X_test, y_test))
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test accuracy: {acc:.2f}")
    model.save(a.out)
    print(f"Saved {a.out}")


if __name__ == "__main__":
    main()
