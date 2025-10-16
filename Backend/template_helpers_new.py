import json
import cv2
import easyocr
import pandas as pd

# Load OCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def extract_with_template(image_path, template_path="Backend/template.json", output_excel="output.xlsx"):
    """
    Extracts text from an image based on predefined template.json regions,
    saves results to Excel, and also returns the data as a dictionary.
    """

    # Load template
    with open(template_path, "r") as f:
        template = json.load(f)

    # Load filled form image
    image = cv2.imread(image_path)
    results = {}

    # Loop through template fields
    for field, box in template["fields"].items():
        x1, y1, x2, y2 = box
        cropped = image[y1:y2, x1:x2]  # crop region

        # OCR on cropped region
        ocr_result = reader.readtext(cropped, detail=0)

        results[field] = " ".join(ocr_result) if ocr_result else ""

    # Convert results to a DataFrame
    df = pd.DataFrame([results])

    # Save to Excel
    df.to_excel(output_excel, index=False)

    print(f" Extracted data saved to {output_excel}")
    return results
