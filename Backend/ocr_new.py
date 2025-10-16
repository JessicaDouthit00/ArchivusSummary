import cv2
import json
import easyocr
import pandas as pd
from PIL import Image
import numpy as np
import os

# -------------------------------
# Helper: Run EasyOCR on an image
# -------------------------------
def run_easyocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    reader = easyocr.Reader(['en'], gpu=False)
    return reader.readtext(thresh)

# -------------------------------
# Mode 1: Free OCR
# -------------------------------
def free_ocr(img_path):
    image = cv2.imread(img_path)
    results = run_easyocr(image)

    data = []
    for (bbox, text, prob) in results:
        data.append([text.strip(), round(prob, 3)])

    df = pd.DataFrame(data, columns=["Text", "Confidence"])
    df.to_excel("ocr_free.xlsx", index=False)
    print(" Free OCR saved to ocr_free.xlsx")

# -------------------------------
# Mode 2: Create Template (manual fields)
# -------------------------------
def create_template(img_path, template_path):
    fields = []
    current_points = []
    field_name = None

    def draw_box(event, x, y, flags, param):
        nonlocal current_points, field_name
        if event == cv2.EVENT_LBUTTONDOWN:
            current_points.append((x, y))
            if len(current_points) == 2:
                field_name = input("Enter field name for this box: ")
                x1, y1 = current_points[0]
                x2, y2 = current_points[1]
                fields.append({
                    "name": field_name,
                    "coords": [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                })
                print(f"Added field: {field_name} at {fields[-1]['coords']}")
                current_points = []

    img = cv2.imread(img_path)
    cv2.namedWindow("Template Creator")
    cv2.setMouseCallback("Template Creator", draw_box)

    print("🖱️ Click top-left and bottom-right corners for each field.")
    print("Press 's' to save and exit, 'q' to quit without saving.")

    while True:
        cv2.imshow("Template Creator", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):  # Save template
            template = {"fields": {f["name"]: f["coords"] for f in fields}}
            with open(template_path, "w") as f:
                json.dump(template, f, indent=2)
            print(f" Template saved to {template_path}")
            break
        elif key == ord("q"):
            print("Quit without saving")
            break

    cv2.destroyAllWindows()

# -------------------------------
# Mode 3: Template OCR (use saved template)
# -------------------------------
def template_ocr(img_path, template_path):
    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return

    with open(template_path, "r") as f:
        template = json.load(f)

    image = cv2.imread(img_path)
    reader = easyocr.Reader(['en'], gpu=False)

    results = {}
    for field, box in template["fields"].items():
        x1, y1, x2, y2 = box
        cropped = image[y1:y2, x1:x2]
        ocr_result = reader.readtext(cropped, detail=0)
        results[field] = " ".join(ocr_result) if ocr_result else ""

    df = pd.DataFrame([results])
    df.to_excel("ocr_template.xlsx", index=False)
    print("Structured OCR saved to ocr_template.xlsx")

# -------------------------------
# Mode 4: Auto-Column OCR (detects columns automatically)
# -------------------------------
def auto_column_ocr(img_path):
    image = cv2.imread(img_path)
    results = run_easyocr(image)

    # Collect text with their x-coordinates
    texts = []
    for (bbox, text, prob) in results:
        x_center = (bbox[0][0] + bbox[2][0]) / 2
        texts.append((x_center, text.strip()))

    # Sort by x position
    texts.sort(key=lambda x: x[0])

    # Cluster x-positions into columns
    columns = {}
    col_threshold = 50  # distance in pixels between columns
    col_index = 1

    last_x = None
    for x, text in texts:
        if last_x is None or abs(x - last_x) > col_threshold:
            col_name = f"Col{col_index}"
            columns[col_name] = []
            col_index += 1
        columns[f"Col{col_index-1}"].append(text)
        last_x = x

    # Normalize row lengths
    max_len = max(len(v) for v in columns.values())
    for k in columns:
        while len(columns[k]) < max_len:
            columns[k].append("")

    df = pd.DataFrame(columns)
    df.to_excel("ocr_auto.xlsx", index=False)
    print("Auto-Column OCR saved to ocr_auto.xlsx")

# -------------------------------
# Main Menu
# -------------------------------
if __name__ == "__main__":
    print("\n=== OCR System ===")
    print("1 - Free OCR (dump text)")
    print("2 - Create Template (manual)")
    print("3 - Use Template OCR (structured)")
    print("4 - Auto-Column OCR (automatic)")

    choice = input("Enter choice (1/2/3/4): ").strip()
    img_path = input("Enter path to image file: ").strip()
    template_path = "template.json"

    if choice == "1":
        free_ocr(img_path)
    elif choice == "2":
        create_template(img_path, template_path)
    elif choice == "3":
        template_ocr(img_path, template_path)
    elif choice == "4":
        auto_column_ocr(img_path)
    else:
        print("Invalid choice. Exiting.")
