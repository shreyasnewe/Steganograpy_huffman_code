from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from huffman_stego import HuffmanCPP  # your existing Huffman wrapper
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os
import uuid
import json
import struct

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Helper: bit/byte utilities and image embed/extract ----------
def _bytes_to_bitstring(b: bytes) -> str:
    return ''.join(f'{byte:08b}' for byte in b)

def _bitstring_to_bytes(s: str) -> bytes:
    # pad if needed
    if len(s) % 8 != 0:
        s = s + ('0' * (8 - (len(s) % 8)))
    return bytes(int(s[i:i+8], 2) for i in range(0, len(s), 8))

def embed_bytes_in_image(input_path: str, payload: bytes, output_path: str):
    """
    Embeds payload bytes into image LSBs.
    Payload format expected to be: 4-byte length (big-endian) + payload bytes
    """
    img = Image.open(input_path).convert('RGB')
    arr = np.array(img)
    flat = arr.flatten()  # dtype=uint8

    payload_bits = _bytes_to_bitstring(payload)
    needed_bits = len(payload_bits)
    capacity = flat.size  # one LSB per channel byte

    if needed_bits > capacity:
        raise ValueError(f"Payload too large for image capacity ({needed_bits} bits needed, {capacity} bits available)")

    # modify LSBs
    for i, bit in enumerate(payload_bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)

    # write back and save
    new_arr = flat.reshape(arr.shape)
    out_img = Image.fromarray(new_arr.astype('uint8'), 'RGB')
    out_img.save(output_path, format='PNG')

def extract_bytes_from_image(input_path: str) -> bytes:
    """
    Extracts payload bytes from image LSBs.
    Expects first 32 bits to be a big-endian uint32 payload length in bytes,
    followed by payload_length * 8 bits of payload data.
    Returns payload bytes (without the 4-byte length header).
    """
    img = Image.open(input_path).convert('RGB')
    arr = np.array(img)
    flat = arr.flatten()

    # Read first 32 bits — payload length in bytes
    if flat.size < 32:
        raise ValueError("Image too small or corrupt")

    len_bits = ''.join(str(int(flat[i] & 1)) for i in range(32))
    payload_len = int(len_bits, 2)  # number of bytes

    total_bits_needed = 32 + payload_len * 8
    if total_bits_needed > flat.size:
        raise ValueError("Declared payload length exceeds image capacity / corrupt data")

    payload_bitstr = ''.join(str(int(flat[i] & 1)) for i in range(32, 32 + payload_len * 8))
    payload_bytes = _bitstring_to_bytes(payload_bitstr)
    return payload_bytes

# ---------- End helpers ----------

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
        # Save uploaded image
        filename = secure_filename(file.filename)
        session_id = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(input_path)

        # ---- Huffman encoding: returns encoded_bits (string of '0'/'1') and codes (mapping) ----
        encoded_bits, codes = huffman.encode(text)  # adapt to your API if names differ
        # encoded_bits is a string of '0'/'1' (assumed). codes is serializable (dict-like).

        # Build payload: JSON with codes and bits
        payload_obj = {
            "codes": codes,
            "bits": encoded_bits
        }
        payload_json = json.dumps(payload_obj, separators=(',', ':')).encode('utf-8')  # bytes

        # Prefix with 4-byte big-endian length (number of payload bytes)
        payload_len = len(payload_json)
        if payload_len > (2**32 - 1):
            raise ValueError("Payload too large to encode length header")

        header = struct.pack('>I', payload_len)  # 4 bytes
        full_payload = header + payload_json

        # embed into image
        output_filename = f"{session_id}_encoded.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        embed_bytes_in_image(input_path, full_payload, output_path)

        # Calculate compression (same metric as you used previously)
        compression = (1 - len(encoded_bits) / (len(text) * 8)) * 100 if len(text) > 0 else 0.0

        # Clean up input file
        os.remove(input_path)

        return jsonify({
            "session_id": session_id,
            "encoded_image_url": f"/outputs/{output_filename}",
            "compression": round(compression, 2),
            "bits": len(encoded_bits)
        })

    except Exception as e:
        # attempt cleanup if input exists
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except:
            pass
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
        # Save uploaded image temporarily
        filename = secure_filename(file.filename)
        temp_id = str(uuid.uuid4())
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}_{filename}")
        file.save(image_path)

        # Extract payload bytes
        payload_bytes = extract_bytes_from_image(image_path)

        # payload_bytes is JSON (the format we saved)
        payload_obj = json.loads(payload_bytes.decode('utf-8'))
        codes = payload_obj.get('codes')
        encoded_bits = payload_obj.get('bits')

        if codes is None or encoded_bits is None:
            raise ValueError("Payload missing required fields")

        # Use Huffman decode with found codes
        decoded_text = huffman.decode(encoded_bits, codes)

        # Clean up
        os.remove(image_path)

        return jsonify({"decoded_text": decoded_text.strip()})

    except Exception as e:
        # cleanup
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass
        return jsonify({"error": str(e)}), 500

@app.route("/outputs/<filename>")
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
