
import os
import json

from sqlalchemy.orm import Session

from .models import Task
from .database import Base, engine, get_db

DATASET_DIR = os.environ.get("DATASET_DIR", "./trainset/data")
OUTPUT_JSON = os.path.join(os.path.dirname(DATASET_DIR), "dataset.json")

def main():
    db: Session = next(get_db())
    tasks = db.query(Task).all()
    result = []
    for task in tasks:
        gt_path = os.path.join("data", "ground_truth", f"{task.task_id}.png")
        submitted_path = os.path.join("data", "submitted", f"{task.task_id}.png")
        result.append({
            "task_id": task.task_id,
            "topic": task.topic,
            "topic_data_idx": task.topic_data_idx,
            "prompt": task.prompt,
            "image_width": task.image_width,
            "image_height": task.image_height,
            "ground_truth": task.ground_truth,
            "expected_bias": task.expected_bias,
            "user_masks": task.user_masks,
            "user_answer": task.user_answer,
            "passed": task.passed,
            "gt_path": gt_path,
            "submitted_path": submitted_path
        })
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(result)} tasks to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()