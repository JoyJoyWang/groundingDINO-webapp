
from groundingdino.util.inference import load_model, load_image, predict, annotate
import os
import numpy as np
import torch
import cv2
from PIL import Image

HOME = os.getcwd()
CONFIG_PATH = os.path.join(HOME, "GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py")
WEIGHTS_PATH = os.path.join(HOME, "weights", "groundingdino_swint_ogc.pth")

try:
    model = load_model(CONFIG_PATH, WEIGHTS_PATH)
except Exception as e:
    print("Model load error:", e)
    model = None



# def run_inference(img_path, prompt):
#     # 模拟一个白色图像（用来验证流程）
#     image = Image.open(img_path).convert("RGB")
#     image = image.resize((512, 512))
#     return np.array(image)


def run_inference(image_path, prompt, box_threshold=0.15, text_threshold=0.15, user_keywords=None):
    if user_keywords is None:
        user_keywords = []
    image_source, image = load_image(image_path)
    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=prompt,
        box_threshold=box_threshold,
        text_threshold=text_threshold
    )

    height, width = image_source.shape[:2]
    boxes_np = boxes.cpu().numpy()
    boxes_xyxy = np.zeros_like(boxes_np)
    boxes_xyxy[:, 0] = (boxes_np[:, 0] - boxes_np[:, 2] / 2) * width
    boxes_xyxy[:, 1] = (boxes_np[:, 1] - boxes_np[:, 3] / 2) * height
    boxes_xyxy[:, 2] = (boxes_np[:, 0] + boxes_np[:, 2] / 2) * width
    boxes_xyxy[:, 3] = (boxes_np[:, 1] + boxes_np[:, 3] / 2) * height

    unwanted_keywords = ["shadow", "wire", "tube", "pipe", "stain", "graffiti", "rail", "stone", "ballast"]
    def is_valid_phrase(phrase):
        pl = phrase.lower()
        if any(bad in pl for bad in unwanted_keywords):
            return False
        if "crack" in pl or "hairline" in pl:
            return True
        for kw in user_keywords:
            if kw and kw in pl:
                return True
        return False
    valid_indices = [
        i for i, phrase in enumerate(phrases)
        if is_valid_phrase(phrase)
    ]
    if len(valid_indices) == 0:
        print("No valid detections found.")
        return np.array(Image.open(image_path).convert("RGB"))  # 返回原图或空白图

    filtered_boxes = boxes_xyxy[valid_indices].astype(int)
    filtered_phrases = [phrases[i] for i in valid_indices]
    filtered_scores = [logits[i] for i in valid_indices]

    # Assign a unique color to each phrase type
    color_map = {}
    color_palette = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Yellow
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
        (0, 128, 255),  # Light Blue
        (128, 255, 0),  # Lime
    ]
    color_idx = 0
    for phrase in set(filtered_phrases):
        color_map[phrase.lower()] = color_palette[color_idx % len(color_palette)]
        color_idx += 1
    filtered_colors = [color_map[ph.lower()] for ph in filtered_phrases]

    annotated = draw_boxes_opencv(
        image=image_source,
        boxes=filtered_boxes,
        phrases=filtered_phrases,
        scores=filtered_scores,
        colors=filtered_colors
    )
    if annotated.dtype != np.uint8:
        annotated = np.clip(annotated, 0, 255).astype(np.uint8)
    return annotated

def draw_boxes_opencv(image, boxes, phrases, scores=None, colors=None, font_scale=2.0, thickness=4):
    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        label = phrases[i] if i < len(phrases) else ""
        if scores and i < len(scores):
            label += f" ({scores[i]:.2f})"
        if not label.strip(): continue
        color = (0, 0, 255)  # Default red
        if colors and i < len(colors):
            color = colors[i]
        cv2.rectangle(img, (x1, y1), (x2, y2), color=color, thickness=thickness)
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cv2.rectangle(img, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
