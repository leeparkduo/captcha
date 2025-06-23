from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from io import BytesIO
from PIL import Image
from datasets import load_dataset

from .database import Base, engine

import matplotlib.pyplot as plt
import sys
import random
import base64

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

# Index page
@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")

# 문세 생성
@app.get("/problem")
def problem():
    topic = random.choice(TOPICS)
    dataset = problem_set[topic][topic]
    total = len(dataset)
    idx = random.randint(0, total - 1)
    item = dataset[idx]
    img = item["image"]
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    problem = {
        "topic": topic,
        "id": item['ID'],
        "prompt": item['prompt'],
        "with_title": item.get('with_title'),
        "pixel": item.get('pixel'),
        "metadata": item.get('metadata'),
        "image_base64": img_base64
    }

    return JSONResponse(content=problem)
