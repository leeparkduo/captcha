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

def draw_transparent_red_circles(submitted_img, user_masks):
    scale = 4  # 안티앨리어싱용 확대 비율
    for mask in user_masks:
        x = mask.get("x", 0)
        y = mask.get("y", 0)
        width = mask.get("width", 0)
        height = mask.get("height", 0)

        # 75% 크기로 축소
        new_w = width * 0.75
        new_h = height * 0.75
        center_x = x + width / 2
        center_y = y + height / 2
        new_x = center_x - new_w / 2
        new_y = center_y - new_h / 2

        # 4배 확대된 오버레이 생성
        large_overlay = Image.new("RGBA", (submitted_img.width * scale, submitted_img.height * scale), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_overlay)
        ellipse_color = (204, 0, 0, 128)  # 빨간색, 50% 투명도

        # 타원 좌표 계산 (확대 적용)
        ellipse_box = [
            int(new_x * scale),
            int(new_y * scale),
            int((new_x + new_w) * scale),
            int((new_y + new_h) * scale)
        ]
        large_draw.ellipse(ellipse_box, fill=ellipse_color)

        # 원본 크기로 리사이즈 (LANCZOS)
        overlay = large_overlay.resize(submitted_img.size, Image.LANCZOS)
        submitted_img = Image.alpha_composite(submitted_img.convert("RGBA"), overlay)

    return submitted_img.convert("RGB")


for item in tqdm(dataset):
    new_item = item.copy()
    new_item['prompt'] = item['prompt'] + "\nScan the image sequentially based on horizontal lines exist in the image.\n"

    gt_img = Image.open(data_dir + new_item['gt_path'])

    result_img = draw_transparent_red_circles(gt_img, new_item.get('user_masks', []))
    result_img.save(data_dir + new_item['submitted_path'], format="PNG")

    augmented_dataset.append(new_item)

# Save updated dataset JSON (optional, if prompts are changed)
aug_json_path = os.path.join(data_dir, 'dataset.json')
with open(aug_json_path, 'w', encoding='utf-8') as f:
    json.dump(augmented_dataset, f, ensure_ascii=False, indent=2)
