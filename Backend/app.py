from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

# Import updated modules
import ocr_new
import template_helpers_new

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/api/free-ocr", methods=["POST"])
def free_ocr_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Run free OCR
    results = ocr_new.run_easyocr(filepath)
    data = [{"text": text, "confidence": float(prob)} for (_, text, prob) in results]

    return jsonify({"results": data})


@app.route("/api/template-ocr", methods=["POST"])
def template_ocr_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    if not os.path.exists("Backend/template.json"):
        return jsonify({"error": "Template not found. Please create one first."}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Use template_helpers_new to extract fields
    results = template_helpers_new.extract_with_template(filepath, "Backend/template.json")

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)
