
import argparse
import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta

import cv2
from ultralytics import YOLO

from simulated_signal_controller import recommend_green


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VIDEO = os.path.join(BASE_DIR, "traffic.mp4")
DEFAULT_MODEL = os.path.join(BASE_DIR, "yolov8n.pt")


VEHICLES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


LANES = {
    "Left": {
        "line": (80, 400, 480, 400),
        "roi": (80, 200, 480, 460)
    },
    "Right": {
        "line": (480, 400, 880, 400),
        "roi": (480, 200, 880, 460)
    }
}

def get_density(count):
    if count < 5:
        return "LOW"
    elif count < 12:
        return "MEDIUM"
    return "HIGH"


def get_green_time(count, lane="lane"):
   
    return recommend_green(count, lane).green_seconds


def main():
    parser = argparse.ArgumentParser(
        description="AI Traffic Flow Optimization"
    )
    parser.add_argument(
        "--source", default=DEFAULT_VIDEO,
        help="Path to traffic video"
    )
    parser.add_argument(
        "--weights", default=DEFAULT_MODEL,
        help="YOLO model weights"
    )
    parser.add_argument(
        "--log", default="traffic_history.csv",
        help="CSV file for interval counts (timestamp,lane,vehicle_count)"
    )
    parser.add_argument(
        "--interval", type=int, default=900,
        help="Seconds of VIDEO time per logged interval (900 = 15 min)"
    )
    parser.add_argument(
        "--no-show", action="store_true",
        help="Run without a window (faster, works on servers)"
    )
    parser.add_argument(
        "--save", default="",
        help="Optional output video path, e.g. output.mp4"
    )
    args = parser.parse_args()

   
    if not os.path.isfile(args.source):
        print(f"ERROR: Video file not found:\n{args.source}")
        return

    # Load YOLO model
    print("Loading YOLO model...")
    model = YOLO(args.weights)

    # Open video
    video = cv2.VideoCapture(args.source)

    if not video.isOpened():
        print("ERROR: Cannot open video.")
        print("Try playing the video normally to check the file.")
        return

    print("Video opened successfully!")
    print("Starting vehicle detection. Press Q to quit.")

    fps = video.get(cv2.CAP_PROP_FPS) or 30.0
    writer = None
    if args.save:
        writer = cv2.VideoWriter(
            args.save, cv2.VideoWriter_fourcc(*"mp4v"), fps, (960, 540)
        )
    log_start = datetime.now().replace(microsecond=0)
    log_file = open(args.log, "w", newline="", encoding="utf-8")
    log = csv.writer(log_file)
    log.writerow(["timestamp", "lane", "vehicle_count"])
    interval_frames = max(1, int(args.interval * fps))
    last_logged = {lane: 0 for lane in LANES}
    frame_no = 0
    sample_file = open("density_samples.csv", "w", newline="", encoding="utf-8")
    samples = csv.writer(sample_file)
    samples.writerow(["lane", "vehicles_in_roi", "occupancy", "label", "frame", "x1", "y1", "x2", "y2"])
    os.makedirs("density_frames", exist_ok=True)
    sample_every = max(1, int(fps * 5))   # one sample every 5 s of video

    counted = defaultdict(set)
    totals = defaultdict(int)
    previous_side = {}

    while True:
        success, frame = video.read()

        if not success:
            print("Video ended or a frame could not be read.")
            break

        # Resize to match the lane coordinates
        frame_no += 1
        frame = cv2.resize(frame, (960, 540))
        raw_frame = frame.copy() if frame_no % sample_every == 0 else None

        # Track vehicles
        result = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=list(VEHICLES.keys()),
            conf=0.35,
            verbose=False
        )[0]

        queue = defaultdict(int)
        occupancy = defaultdict(float)

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            ids = result.boxes.id.int().cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()

            for box, vehicle_id, class_id in zip(boxes, ids, classes):
                x1, y1, x2, y2 = map(int, box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                name = VEHICLES.get(class_id, "Vehicle")

                # Draw bounding box and tracking ID
                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                cv2.putText(
                    frame, f"{name} ID:{vehicle_id}",
                    (x1, max(20, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2
                )

                for lane, data in LANES.items():
                    rx1, ry1, rx2, ry2 = data["roi"]
                    lx1, ly1, lx2, ly2 = data["line"]

                    # Count currently tracked vehicles in the ROI
                    if rx1 <= cx <= rx2 and ry1 <= cy <= ry2:
                        queue[lane] += 1
                        roi_area = max(1, (rx2 - rx1) * (ry2 - ry1))
                        occupancy[lane] += (x2 - x1) * (y2 - y1) / roi_area

                    # Count a tracked vehicle crossing the line
                    if lx1 <= cx <= lx2:
                        side = 1 if cy >= ly1 else -1
                        key = (lane, vehicle_id)

                        if key in previous_side:
                            old_side = previous_side[key]

                            if (
                                old_side != side
                                and vehicle_id not in counted[lane]
                            ):
                                counted[lane].add(vehicle_id)
                                totals[lane] += 1

                        previous_side[key] = side

        # Draw lanes and traffic information
        for lane, data in LANES.items():
            lx1, ly1, lx2, ly2 = data["line"]
            rx1, ry1, rx2, ry2 = data["roi"]

            cv2.rectangle(
                frame, (rx1, ry1), (rx2, ry2),
                (255, 200, 0), 2
            )
            cv2.line(
                frame, (lx1, ly1), (lx2, ly2),
                (0, 0, 255), 2
            )

            vehicles_now = queue[lane]
            density = get_density(vehicles_now)
            green_time = get_green_time(vehicles_now, lane)

            # Display separate lane information
            text = (
                f"{lane}: In ROI={vehicles_now} "
                f"Crossed={totals[lane]} "
                f"Traffic={density} Green={green_time}s"
            )

            y_text = 30 if lane == "North" else 65

            cv2.putText(
                frame, text, (10, y_text),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (255, 255, 255), 2
            )

        # Log vehicles that crossed each line during this interval
        if frame_no % interval_frames == 0:
            stamp = log_start + timedelta(seconds=frame_no / fps)
            for lane in LANES:
                log.writerow([
                    stamp.isoformat(timespec="minutes"), lane,
                    totals[lane] - last_logged[lane]
                ])
                last_logged[lane] = totals[lane]
            log_file.flush()

        # One feature sample per second of video, for train_density_classifier.py
        if raw_frame is not None:
            name = f"frame_{frame_no:06d}.jpg"
            cv2.imwrite(os.path.join("density_frames", name), raw_frame)
            for lane, data in LANES.items():
                samples.writerow([lane, queue[lane], round(occupancy[lane], 4), "",
                                  name, *data["roi"]])

        if writer is not None:
            writer.write(frame)

        if not args.no_show:
            cv2.imshow("AI Traffic Flow Optimization", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    video.release()
    if writer is not None:
        writer.release()
    log_file.close()
    sample_file.close()
    cv2.destroyAllWindows()

    print("\nFinal vehicle counts:")
    for lane in LANES:
        print(f"{lane}: {totals[lane]} vehicles crossed")
    print(f"Interval counts saved to {args.log}")



if __name__ == "__main__":
    main()
