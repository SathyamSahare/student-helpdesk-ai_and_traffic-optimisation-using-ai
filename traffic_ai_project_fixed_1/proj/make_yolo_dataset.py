import argparse
import os
import random

import cv2
from ultralytics import YOLO

# COCO class id -> our dataset class id
COCO_TO_OURS = {2: 0, 3: 1, 5: 2, 7: 3}
NAMES = ["car", "motorcycle", "bus", "truck"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="traffic.mp4")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--every", type=int, default=15, help="use 1 frame every N frames")
    ap.add_argument("--max-images", type=int, default=400)
    ap.add_argument("--conf", type=float, default=0.4)
    ap.add_argument("--out", default="dataset")
    a = ap.parse_args()

    random.seed(0)
    model = YOLO(a.model)
    video = cv2.VideoCapture(a.source)
    if not video.isOpened():
        raise SystemExit(f"Cannot open video: {a.source}")
    for sub in ("images/train", "images/val", "labels/train", "labels/val"):
        os.makedirs(os.path.join(a.out, sub), exist_ok=True)

    i = n = 0
    while n < a.max_images:
        ok, frame = video.read()
        if not ok:
            break
        if i % a.every == 0:
            split = "val" if random.random() < 0.2 else "train"
            res = model(frame, conf=a.conf, classes=list(COCO_TO_OURS), verbose=False)[0]
            h, w = frame.shape[:2]
            lines = []
            for box in res.boxes:
                cls = COCO_TO_OURS[int(box.cls[0])]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                lines.append(f"{cls} {(x1+x2)/2/w:.6f} {(y1+y2)/2/h:.6f} {(x2-x1)/w:.6f} {(y2-y1)/h:.6f}")
            if lines:
                name = f"frame_{n:05d}"
                cv2.imwrite(os.path.join(a.out, "images", split, name + ".jpg"), frame)
                with open(os.path.join(a.out, "labels", split, name + ".txt"), "w") as f:
                    f.write("\n".join(lines))
                n += 1
        i += 1
    video.release()

    yaml_path = os.path.join(a.out, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(f"path: {os.path.abspath(a.out)}\ntrain: images/train\nval: images/val\nnames:\n")
        for k, nme in enumerate(NAMES):
            f.write(f"  {k}: {nme}\n")
    print(f"Saved {n} labeled frames and {yaml_path}")
    print("Next: python train_custom_yolo.py --data dataset/data.yaml")


if __name__ == "__main__":
    main()
