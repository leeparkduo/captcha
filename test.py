from datasets import load_dataset
from PIL import Image

import matplotlib.pyplot as plt
import sys

train_ds = load_dataset("parquet", data_files = {"train": "./dataset/data/train-*.parquet"})
identification_ds = load_dataset("parquet", data_files = {"identification": "./dataset/data/identification-*.parquet"})
notitle_ds = load_dataset("parquet", data_files = {"notitle": "./dataset/data/notitle-*.parquet",})
main_ds = load_dataset("parquet", data_files = {"main": "./dataset/data/main-*.parquet"})
withtitle_ds = load_dataset("parquet", data_files = {"withtitle": "./dataset/data/withtitle-*.parquet"})
yes_no_ds = load_dataset("parquet", data_files = {"yes_no": "./dataset/data/yes_no-*.parquet"})

"""
현재 데이터에서 공통된 컬럼은 다음과 같다.
- image
- ID
- image_path
- topic
- prompt
- ground_truth
- expected_bias
- with_title
- pixel
- metadata
"""
print(train_ds)
print(identification_ds)
print(notitle_ds)
print(main_ds)
print(withtitle_ds)
print(yes_no_ds)

# sample = ds["train"][22]
# img = sample["image"]
# plt.imshow(img)
# plt.axis("off")
# plt.show()