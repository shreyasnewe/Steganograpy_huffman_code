from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from huffman_stego import HuffmanCPP, Steganography
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

huffman = HuffmanCPP()

# Session-based codes storage
codes_sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/encode", methods=["POST"])
def encode():
    # Check if image and text are present
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    if 'text' not in request.form:
        return jsonify({"error": "No text provided"}), 400

    file = request.files['image']
    text = request.form['text']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, or BMP"}), 400

    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded image
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(input_path)

        # Encode with Huffman
        encoded_bits, codes = huffman.encode(text)
        
        # Store codes for this session
        codes_sessions[session_id] = codes

        # Embed in image
        output_filename = f"{session_id}_encoded.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        Steganography.embed(input_path, encoded_bits, output_path)

        # Calculate compression
        compression = (1 - len(encoded_bits) / (len(text) * 8)) * 100

        # Clean up input file
        os.remove(input_path)

        return jsonify({
            "session_id": session_id,
            "encoded_image_url": f"/outputs/{output_filename}",
            "compression": round(compression, 2),
            "bits": len(encoded_bits)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/decode", methods=["POST"])
def decode():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, or BMP"}), 400

    try:
        # Save uploaded image
        filename = secure_filename(file.filename)
        temp_id = str(uuid.uuid4())
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}_{filename}")
        file.save(image_path)

        # Try to extract session_id from filename
        session_id = None
        if '_encoded.png' in filename:
            session_id = filename.split('_encoded.png')[0]

        # Get codes from session
        if not session_id or session_id not in codes_sessions:
            os.remove(image_path)
            return jsonify({
                "error": "No Huffman codes found for this image. Make sure you're decoding an image that was encoded in this session."
            }), 400

        codes = codes_sessions[session_id]

        # Extract and decode
        extracted_bits = Steganography.extract(image_path)
        decoded_text = huffman.decode(extracted_bits, codes)

        # Clean up
        os.remove(image_path)

        return jsonify({"decoded_text": decoded_text.strip()})

    except Exception as e:
        if os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({"error": str(e)}), 500

@app.route("/outputs/<filename>")
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)