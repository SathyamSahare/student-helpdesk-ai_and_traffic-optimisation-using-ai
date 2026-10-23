import argparse
from pathlib import Path
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8 on a labeled vehicle dataset.")
    parser.add_argument("--data", required=True, help="Path to YOLO dataset YAML, e.g. dataset/data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Starting pretrained weights")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset YAML not found: {data_path}\n"
            "Copy dataset/data.yaml.example to dataset/data.yaml and edit its paths."
        )

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project="runs/detect",
        name="vehicle_custom",
        exist_ok=True,
    )
    print("Training finished. Check runs/detect/vehicle_custom/weights/best.pt")

if __name__ == "__main__":
    main()
