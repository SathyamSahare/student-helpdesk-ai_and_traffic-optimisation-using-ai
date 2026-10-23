import argparse
import os

import cv2
import pandas as pd

KEYS = {ord("1"): "LOW", ord("2"): "MEDIUM", ord("3"): "HIGH"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="density_samples.csv")
    ap.add_argument("--frames", default="density_frames")
    a = ap.parse_args()

    df = pd.read_csv(a.data)
    df["label"] = df["label"].astype("object")
    i = 0
    while 0 <= i < len(df):
        row = df.iloc[i]
        img = cv2.imread(os.path.join(a.frames, row["frame"]))
        if img is None:
            i += 1
            continue
        cv2.rectangle(img, (int(row.x1), int(row.y1)), (int(row.x2), int(row.y2)), (0, 255, 255), 3)
        done = int(df["label"].notna().sum())
        txt = f"{row['lane']}  [{i+1}/{len(df)}]  labeled {done}  current: {row['label']}"
        cv2.putText(img, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(img, "1=LOW 2=MEDIUM 3=HIGH s=skip b=back q=quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Label density (yellow box = lane)", img)
        k = cv2.waitKey(0) & 0xFF
        if k in KEYS:
            df.at[df.index[i], "label"] = KEYS[k]
            i += 1
        elif k == ord("s"):
            i += 1
        elif k == ord("b"):
            i -= 1
        elif k == ord("q"):
            break
    cv2.destroyAllWindows()
    df.to_csv(a.data, index=False)
    print(f"Saved. Labeled rows: {int(df['label'].notna().sum())} of {len(df)}")


if __name__ == "__main__":
    main()
