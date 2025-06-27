from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from io import BytesIO
from datasets import load_dataset
from pydantic import BaseModel
from typing import List, Dict

from .models import Task
from .database import Base, engine, get_db

import uuid
import random
import base64
import os

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
        "image_base64": img_base64
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
        user_answer=request.user_answer,
        passed=False
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return JSONResponse(content={"message": "Answer submitted and task stored", "task_id": task.task_id})
