import os
import json
import numpy as np
import uuid
from PIL import Image
from tqdm import tqdm

# 경로 설정
data_dir = 'trainset/'
json_path = os.path.join(data_dir, 'dataset.json')
gt_dir = os.path.join(data_dir, 'data', 'ground_truth')
sub_dir = os.path.join(data_dir, 'data', 'submitted')
gt_aug_dir = os.path.join(data_dir, 'data', 'ground_truth_aug')
sub_aug_dir = os.path.join(data_dir, 'data', 'submitted_aug')

os.makedirs(gt_aug_dir, exist_ok=True)
os.makedirs(sub_aug_dir, exist_ok=True)

# 데이터셋 로드
with open(json_path, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

augmented_dataset = []
count = 0

def add_noise(img):
    arr = np.array(img).astype('float32')
    noise = np.random.normal(0, 10, arr.shape)
    arr = arr + noise
    arr = np.clip(arr, 0, 255).astype('uint8')
    return Image.fromarray(arr)

def scale_img(img, scale=1.5):
    w, h = img.size
    return img.resize((int(w*scale), int(h*scale)), Image.BICUBIC)

for item in tqdm(dataset):
    gt_path = os.path.join(gt_dir, os.path.basename(item['gt_path']))
    sub_path = os.path.join(sub_dir, os.path.basename(item['submitted_path']))
    if not os.path.exists(gt_path) or not os.path.exists(sub_path):
        continue
    gt_img = Image.open(gt_path)
    sub_img = Image.open(sub_path)
    gt_scaled = scale_img(gt_img, 1.5)
    sub_scaled = scale_img(sub_img, 1.5)
    new_id = str(uuid.uuid4())
    gt_aug_path = os.path.join(gt_aug_dir, f"{new_id}.png")
    sub_aug_path = os.path.join(sub_aug_dir, f"{new_id}.png")
    gt_scaled.save(gt_aug_path)
    sub_scaled.save(sub_aug_path)

    gt_aug_path = gt_aug_path.replace(data_dir, '')
    sub_aug_path = sub_aug_path.replace(data_dir, '')

    new_item = item.copy()
    new_item['task_id'] = new_id
    new_item['image_width'] = gt_scaled.width
    new_item['image_height'] = gt_scaled.height
    new_item['gt_path'] = gt_aug_path
    new_item['submitted_path'] = sub_aug_path

    new_masks = []
    for mask in new_item['user_masks']:
        new_mask = mask.copy()
        new_mask['x'] = int(mask['x'] * 1.5)
        new_mask['y'] = int(mask['y'] * 1.5)
        new_mask['width'] = int(mask['width'] * 1.5)
        new_mask['height'] = int(mask['height'] * 1.5)
        new_masks.append(new_mask)
    new_item['user_masks'] = new_masks
    augmented_dataset.append(new_item)

for item in tqdm(dataset):
    gt_path = os.path.join(gt_dir, os.path.basename(item['gt_path']))
    sub_path = os.path.join(sub_dir, os.path.basename(item['submitted_path']))
    if not os.path.exists(gt_path) or not os.path.exists(sub_path):
        continue
    gt_img = Image.open(gt_path)
    sub_img = Image.open(sub_path)
    gt_scaled = add_noise(gt_img)
    sub_scaled = add_noise(sub_img)
    new_id = str(uuid.uuid4())
    gt_aug_path = os.path.join(gt_aug_dir, f"{new_id}.png")
    sub_aug_path = os.path.join(sub_aug_dir, f"{new_id}.png")

    gt_scaled.save(gt_aug_path)
    sub_scaled.save(sub_aug_path)

    gt_aug_path = gt_aug_path.replace(data_dir, '')
    sub_aug_path = sub_aug_path.replace(data_dir, '')

    new_item = item.copy()
    new_item['task_id'] = new_id
    new_item['image_width'] = gt_scaled.width
    new_item['image_height'] = gt_scaled.height
    new_item['gt_path'] = gt_aug_path
    new_item['submitted_path'] = sub_aug_path
    augmented_dataset.append(new_item)

final_dataset = dataset + augmented_dataset
aug_json_path = os.path.join(data_dir, 'dataset.json')
with open(aug_json_path, 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)
