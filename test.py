from datasets import load_dataset
from PIL import Image

import matplotlib.pyplot as plt
import sys

data_files = {
    "train": "./dataset/data/train-*.parquet",
    # "identification": "./dataset/data/identification-*.parquet",
    # "notitle": "./dataset/data/notitle-*.parquet",
    # "main": "./dataset/data/main-*.parquet",
    # "withtitle": "./dataset/data/withtitle-*.parquet",
    # "yes_no": "./dataset/yes_no-*.parquet",
}

ds = load_dataset("parquet", data_files=data_files)
print(ds["train"][0])
sample = ds["train"][22]
img = sample["image"]
plt.imshow(img)
plt.axis("off")
plt.show()