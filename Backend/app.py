from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

# Import updated modules
import ocr_new
import template_helpers_new

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Handwritten Data OCR API",
        "endpoints": {
            "/api/free-ocr": "POST - Free-form OCR",
            "/api/template-ocr": "POST - Template-based OCR"
        }
    })

@app.route("/api/free-ocr", methods=["POST"])
def free_ocr_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    try:
        # Run free OCR
        results = ocr_new.run_easyocr(filepath)
        data = [{"text": text, "confidence": float(prob)} for (_, text, prob) in results]
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({"results": data})
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

@app.route("/api/template-ocr", methods=["POST"])
def template_ocr_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    if not os.path.exists("template.json"):
        return jsonify({"error": "Template not found. Please create one first."}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    try:
        # Use template_helpers_new to extract fields
        results = template_helpers_new.extract_with_template(filepath, "template.json")
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({"results": results})
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

@app.route("/api/auto-column-ocr", methods=["POST"])
def auto_column_ocr_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    try:
        # Run auto-column detection OCR
        results = ocr_new.auto_column_ocr(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({"results": results})
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
