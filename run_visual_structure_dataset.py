import os
import json
from PIL import Image, ImageDraw
from tqdm import tqdm

# Set paths
data_dir = 'trainset/'
json_path = os.path.join(data_dir, 'dataset.json')

# Load dataset
with open(json_path, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

augmented_dataset = []

for item in tqdm(dataset):
    new_item = item.copy()
    new_item['prompt'] = item['prompt'] + "\nScan the image sequentially based on horizontal lines exist in the image.\n"

    # Load images
    sub_img = Image.open(data_dir + new_item['submitted_path'])

    # Get image size
    width, height = sub_img.size
    interval = height // 6

    # Draw 5 black horizontal lines
    draw_sub = ImageDraw.Draw(sub_img)
    for i in range(1, 6):
        y = i * interval
        draw_sub.line([(0, y), (width-1, y)], fill=(0, 0, 0), width=1)

    # Overwrite original images
    sub_img.save(data_dir + new_item['submitted_path'])

    augmented_dataset.append(new_item)

# Save updated dataset JSON (optional, if prompts are changed)
aug_json_path = os.path.join(data_dir, 'dataset.json')
with open(aug_json_path, 'w', encoding='utf-8') as f:
    json.dump(augmented_dataset, f, ensure_ascii=False, indent=2)
