import cv2
import json
import easyocr
import pandas as pd
from PIL import Image
import numpy as np
import os

# Initialize reader once globally for better performance
reader = None

def get_reader():
    """Lazy load the EasyOCR reader"""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

# -------------------------------
# Helper: Run EasyOCR on an image
# -------------------------------
def run_easyocr(image_path):
    """
    Run EasyOCR on an image file path.
    Can accept either a file path string or a numpy array (cv2 image).
    Returns: list of (bbox, text, probability) tuples
    """
    # Handle both file path and image array
    if isinstance(image_path, str):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
    else:
        image = image_path
    
    # Preprocess image for better OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Get reader and process
    ocr_reader = get_reader()
    results = ocr_reader.readtext(thresh)
    
    return results

# -------------------------------
# Mode 1: Free OCR
# -------------------------------
def free_ocr(img_path, output_path="ocr_free.xlsx"):
    """
    Extract all text from image without structure.
    Saves to Excel and returns data.
    """
    image = cv2.imread(img_path)
    results = run_easyocr(image)

    data = []
    for (bbox, text, prob) in results:
        data.append([text.strip(), round(prob, 3)])

    df = pd.DataFrame(data, columns=["Text", "Confidence"])
    df.to_excel(output_path, index=False)
    print(f" Free OCR saved to {output_path}")
    
    return data

# -------------------------------
# Mode 2: Create Template (manual fields)
# -------------------------------
def create_template(img_path, template_path="template.json"):
    """
    Interactive tool to create a template by clicking on image.
    Click top-left and bottom-right corners for each field.
    Press 's' to save, 'q' to quit.
    """
    fields = []
    current_points = []
    field_name = None
    img_display = None

    def draw_box(event, x, y, flags, param):
        nonlocal current_points, field_name, img_display
        if event == cv2.EVENT_LBUTTONDOWN:
            current_points.append((x, y))
            
            # Draw point on image
            img_display = img.copy()
            for pt in current_points:
                cv2.circle(img_display, pt, 5, (0, 255, 0), -1)
            
            if len(current_points) == 2:
                # Draw rectangle
                cv2.rectangle(img_display, current_points[0], current_points[1], (0, 255, 0), 2)
                cv2.imshow("Template Creator", img_display)
                
                # Ask for field name in terminal
                field_name = input("Enter field name for this box: ")
                x1, y1 = current_points[0]
                x2, y2 = current_points[1]
                fields.append({
                    "name": field_name,
                    "coords": [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                })
                print(f" Added field: {field_name} at {fields[-1]['coords']}")
                
                # Draw all boxes so far
                img_display = img.copy()
                for field in fields:
                    x1, y1, x2, y2 = field["coords"]
                    cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img_display, field["name"], (x1, y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                current_points = []

    img = cv2.imread(img_path)
    img_display = img.copy()
    cv2.namedWindow("Template Creator")
    cv2.setMouseCallback("Template Creator", draw_box)

    print("\n  Click top-left and bottom-right corners for each field.")
    print("Press 's' to save and exit, 'q' to quit without saving\n")

    while True:
        cv2.imshow("Template Creator", img_display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("s"):  # Save template
            with open(template_path, "w") as f:
                json.dump(fields, f, indent=2)
            print(f" Template saved to {template_path}")
            break
        elif key == ord("q"):
            print("❌ Quit without saving")
            break

    cv2.destroyAllWindows()
    return fields

# -------------------------------
# Mode 3: Template OCR (use saved template)
# -------------------------------
def template_ocr(img_path, template_path="template.json", output_path="ocr_template.xlsx"):
    """
    Extract structured data using a predefined template.
    """
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return None

    with open(template_path, "r") as f:
        template = json.load(f)

    image = cv2.imread(img_path)
    ocr_reader = get_reader()

    results = {}
    
    # Handle both old and new template formats
    if isinstance(template, list):
        # New format: list of field objects
        for field_data in template:
            field = field_data["name"]
            box = field_data["coords"]
            x1, y1, x2, y2 = box
            cropped = image[y1:y2, x1:x2]
            ocr_result = ocr_reader.readtext(cropped, detail=0)
            results[field] = " ".join(ocr_result) if ocr_result else ""
    else:
        # Old format: dict with "fields" key
        for field, box in template.get("fields", template).items():
            x1, y1, x2, y2 = box
            cropped = image[y1:y2, x1:x2]
            ocr_result = ocr_reader.readtext(cropped, detail=0)
            results[field] = " ".join(ocr_result) if ocr_result else ""

    df = pd.DataFrame([results])
    df.to_excel(output_path, index=False)
    print(f" Structured OCR saved to {output_path}")
    
    return results

# -------------------------------
# Mode 4: Auto-Column OCR (detects columns automatically)
# -------------------------------
def auto_column_ocr(img_path, output_path="ocr_auto.xlsx"):
    """
    Automatically detect columns in the image and extract data.
    Best for tabular data without a template.
    """
    image = cv2.imread(img_path)
    results = run_easyocr(image)

    # Collect text with their coordinates
    texts = []
    for (bbox, text, prob) in results:
        # Calculate center x-coordinate and y-coordinate
        x_center = (bbox[0][0] + bbox[2][0]) / 2
        y_center = (bbox[0][1] + bbox[2][1]) / 2
        texts.append((x_center, y_center, text.strip()))

    if not texts:
        print("  No text detected in image")
        return None

    # Sort by y-position first (rows), then x-position (columns)
    texts.sort(key=lambda x: (x[1], x[0]))

    # Cluster x-positions into columns
    columns = {}
    col_threshold = 100  # Distance in pixels between columns
    
    # Group texts by similar x-coordinates (columns)
    for x, y, text in texts:
        # Find which column this belongs to
        found_col = False
        for col_name, col_data in columns.items():
            avg_x = sum(item[0] for item in col_data) / len(col_data)
            if abs(x - avg_x) < col_threshold:
                col_data.append((x, y, text))
                found_col = True
                break
        
        if not found_col:
            col_name = f"Col{len(columns) + 1}"
            columns[col_name] = [(x, y, text)]
    
    # Sort each column by y-position and extract text
    column_data = {}
    for col_name, col_items in columns.items():
        col_items.sort(key=lambda x: x[1])  # Sort by y-position
        column_data[col_name] = [item[2] for item in col_items]
    
    # Normalize row lengths
    max_len = max(len(v) for v in column_data.values()) if column_data else 0
    for col_name in column_data:
        while len(column_data[col_name]) < max_len:
            column_data[col_name].append("")

    df = pd.DataFrame(column_data)
    df.to_excel(output_path, index=False)
    print(f" Auto-Column OCR saved to {output_path}")
    
    return column_data

# -------------------------------
# Main Menu (for standalone testing)
# -------------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  HANDWRITTEN DATA OCR SYSTEM")
    print("="*50)
    print("\n Select OCR Mode:")
    print("  1 - Free OCR (extract all text)")
    print("  2 - Create Template (define fields manually)")
    print("  3 - Template OCR (use existing template)")
    print("  4 - Auto-Column OCR (automatic table detection)")
    print("="*50)

    choice = input("\n Enter choice (1/2/3/4): ").strip()
    img_path = input(" Enter path to image file: ").strip()
    template_path = "template.json"

    print("\n⏳ Processing...\n")

    if choice == "1":
        free_ocr(img_path)
    elif choice == "2":
        create_template(img_path, template_path)
    elif choice == "3":
        template_ocr(img_path, template_path)
    elif choice == "4":
        auto_column_ocr(img_path)
    else:
        print(" Invalid choice. Exiting.")
    
    print("\n Done!\n")
