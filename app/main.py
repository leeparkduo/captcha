from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from io import BytesIO
from PIL import Image
from datasets import load_dataset

from .database import Base, engine

import matplotlib.pyplot as plt
import sys

# Dataset loading
data_files = {
    "train": "./dataset/data/train-*.parquet",
}
ds = load_dataset("parquet", data_files=data_files)

# Construct FastAPI app and database
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def index():
    return "Hello, World"

@app.get("/hello", include_in_schema=False)
def root():
    return FileResponse("static/index.html")

@app.get("/image/{idx}", response_class=StreamingResponse)
def get_image(idx: int):
    example = ds["train"][idx]
    img: Image.Image = example["image"]

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")