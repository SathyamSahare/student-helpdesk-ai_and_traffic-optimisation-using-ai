
import argparse
import os

import cv2
import numpy as np


def preprocess(frame, size=(960, 540)):
    resized = cv2.resize(frame, size)                              # 1) resize
    clean = cv2.fastNlMeansDenoisingColored(resized, None, 5, 5, 7, 21)  # 2) noise reduction
    normalized = clean.astype(np.float32) / 255.0                  # 3) normalization to 0..1
    return resized, clean, normalized


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="traffic.mp4")
    ap.add_argument("--every", type=int, default=30, help="save 1 frame every N frames")
    ap.add_argument("--max-frames", type=int, default=200, help="stop after saving this many")
    ap.add_argument("--out", default="frames")
    a = ap.parse_args()

    video = cv2.VideoCapture(a.source)
    if not video.isOpened():
        raise SystemExit(f"Cannot open video: {a.source}")
    os.makedirs(os.path.join(a.out, "raw"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "clean"), exist_ok=True)

    i = saved = 0
    sample = []
    while saved < a.max_frames:
        ok, frame = video.read()
        if not ok:
            break
        if i % a.every == 0:
            raw, clean, norm = preprocess(frame)
            cv2.imwrite(os.path.join(a.out, "raw", f"frame_{saved:05d}.jpg"), raw)
            cv2.imwrite(os.path.join(a.out, "clean", f"frame_{saved:05d}.jpg"), clean)
            if len(sample) < 10:
                sample.append(norm)
            saved += 1
        i += 1
    video.release()
    if sample:
        np.save(os.path.join(a.out, "normalized.npy"), np.stack(sample))
    print(f"Saved {saved} frames to {a.out}/raw and {a.out}/clean")


if __name__ == "__main__":
    main()
