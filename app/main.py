from fastapi import FastAPI, Depends, HTTPException
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from io import BytesIO
from datasets import load_dataset
from pydantic import BaseModel
from typing import List, Dict

from .models import Task
from .database import Base, engine, get_db
from PIL import Image, ImageDraw, ImageFont

import uuid
import random
import base64
import json
import os
import shutil
import tempfile

DATASET_DIR = os.environ.get("DATASET_DIR", "./trainset/data")

# 문제 토픽들
TOPICS = ['train', 'identification', 'notitle', 'main', 'withtitle', 'yes_no']

# Dataset loading
problem_set = {'train': load_dataset("parquet", data_files={"train": "./dataset/data/train-*.parquet"}),
               'identification': load_dataset("parquet",data_files={"identification": "./dataset/data/identification-*.parquet"}),
               'notitle': load_dataset("parquet", data_files={"notitle": "./dataset/data/notitle-*.parquet", }),
               'main': load_dataset("parquet", data_files={"main": "./dataset/data/main-*.parquet"}),
               'withtitle': load_dataset("parquet", data_files={"withtitle": "./dataset/data/withtitle-*.parquet"}),
               'yes_no': load_dataset("parquet", data_files={"yes_no": "./dataset/data/yes_no-*.parquet"})}

def get_problem_item(topic, idx):
    dataset = load_dataset("parquet", data_files={topic: f"./dataset/data/{topic}-*.parquet"}, split=topic)
    return dataset[idx]

# Construct FastAPI app and database
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Answer Reuest
class AnswerRequest(BaseModel):
    topic: str
    index: int
    user_masks: List[Dict]
    user_answer: str

# Index page
@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")

# 문제 생성
@app.get("/problem")
def problem(db: Session = Depends(get_db)):
    existing = db.query(Task.topic, Task.topic_data_idx).all()
    existing_set = set(existing)

    candidates = []
    for topic in TOPICS:
        dataset = problem_set[topic][topic]
        total = len(dataset)
        for idx in range(total):
            if (topic, idx) not in existing_set:
                candidates.append((topic, idx))

    if not candidates:
        raise HTTPException(status_code=404, detail="문제가 없습니다.")

    topic, idx = random.choice(candidates)
    item = problem_set[topic][topic][idx]
    img = item["image"]
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    image_width, image_height = img.size

    total_count = sum(len(problem_set[t][t]) for t in TOPICS)
    solved_count = len(existing_set)

    problem = {
        "topic": topic,
        "index": idx,
        "id": item['ID'],
        "prompt": item['prompt'],
        "with_title": item.get('with_title'),
        "pixel": item.get('pixel'),
        "metadata": item.get('metadata'),
        "ground_truth": item.get("ground_truth", ''),
        "expected_bias": item.get("expected_bias", ''),
        "image_width": image_width,
        "image_height": image_height,
        "image_base64": img_base64,
        "total_count": total_count,
        "solved_count": solved_count,
    }
    return JSONResponse(content=problem)

@app.post("/answer")
def create_answer(
        request: AnswerRequest,
        db: Session = Depends(get_db)):

    # Task를 새로 생성하여 답변과 함께 저장
    dataset = problem_set[request.topic][request.topic]
    index = request.index
    if index < 0 or index >= len(dataset):
        raise HTTPException(status_code=404, detail="문제 인덱스 오류")
    item = dataset[index]
    image_width, image_height = item["image"].size

    task = Task(
        task_id=str(uuid.uuid4()),
        topic=request.topic,
        topic_data_idx=index,
        prompt=item['prompt'],
        image_width=image_width,
        image_height=image_height,
        ground_truth=str(item.get("ground_truth", '')),
        expected_bias=str(item.get("expected_bias", '')),
        user_masks=request.user_masks,
        user_answer=request.user_answer
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    gt_dir = os.path.join(DATASET_DIR, "data", "ground_truth")
    os.makedirs(gt_dir, exist_ok=True)
    gt_path = os.path.join(gt_dir, f"{task.task_id}.png")
    item["image"].save(gt_path, format="PNG")

    # Save submitted image (draw user masks on a copy)
    sub_dir = os.path.join(DATASET_DIR, "data", "submitted")
    os.makedirs(sub_dir, exist_ok=True)
    sub_path = os.path.join(sub_dir, f"{task.task_id}.png")
    submitted_img = item["image"].copy()
    draw = ImageDraw.Draw(submitted_img)

    for idx, mask in enumerate(request.user_masks):
        x = mask.get("x", 0)
        y = mask.get("y", 0)
        width = mask.get("width", 0)
        height = mask.get("height", 0)
        center_x = x + width / 2
        center_y = y + height / 2
        number = str(idx + 1)

        # --- 안티앨리어싱 원 그리기 ---
        scale = 4  # 4배 크기로 그렸다가 줄임
        large_overlay = Image.new("RGBA", (submitted_img.width * scale, submitted_img.height * scale), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_overlay)
        ellipse_color = (204, 0, 0, 178)
        large_draw.ellipse(
            [int(x*scale), int(y*scale), int((x+width)*scale), int((y+height)*scale)],
            fill=ellipse_color
        )
        # 원본 크기로 리사이즈 (LANCZOS)
        overlay = large_overlay.resize(submitted_img.size, Image.LANCZOS)
        submitted_img = Image.alpha_composite(submitted_img.convert("RGBA"), overlay)

        # --- 폰트 크기 동적 조정 ---
        try:
            font = ImageFont.truetype("NotoSansSunuwar-Regular.ttf", size=20)
        except:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(submitted_img)
        bbox = draw.textbbox((0, 0), number, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(
            (center_x - text_w / 2, center_y - text_h / 2 - 6),
            number,
            fill="white",
            font=font
        )

    submitted_img = submitted_img.convert("RGB")
    submitted_img.save(sub_path, format="PNG")

    return JSONResponse(content={"message": "Answer submitted and task stored", "task_id": task.task_id})

@app.get("/download")
def download_dataset_zip():
    """
    Packages the entire DATASET_DIR folder into a zip file and downloads it.
    """

    OUTPUT_JSON = os.path.join(DATASET_DIR, "dataset.json")

    db = next(get_db())
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
            "gt_path": gt_path,
            "submitted_path": submitted_path
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    zip_filename = "dataset.zip"
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, zip_filename)
    shutil.make_archive(
        base_name=zip_path[:-4], 
        format='zip', 
        root_dir = os.path.dirname(DATASET_DIR), 
        base_dir = os.path.basename(DATASET_DIR))
    return FileResponse(zip_path, filename=zip_filename, media_type="application/zip")