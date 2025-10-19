
Here’s a complete and well-structured README.md for your Huffman Steganography project:

---

# 🔐 Huffman Steganography Tool (Python + C++)

A command-line tool that compresses text using Huffman encoding (via C++ backend) and hides it inside an image using LSB steganography. You can also extract and decode the hidden message from the image.

---

## 📦 Features

- ✅ Huffman encoding/decoding powered by a C++ executable
- 🖼️ LSB-based steganography for embedding binary data into RGB images
- 📊 Compression stats and bit-level control
- 🧠 Session-based Huffman code caching for decoding

---

## 🛠 Requirements

- Python 3.7+
- C++ compiler (e.g., `g++`)
- Python packages:
  ```bash
  pip install pillow
  ```

---

## ⚙️ Setup

### 1. Compile the C++ Huffman executable

Make sure you have `huffman.cpp` in the same directory. Then run:

```bash
g++ -O2 -o huffman huffman.cpp
```

On Windows, this will produce `huffman.exe`. On Unix-based systems, it will be `./huffman`.

### 2. Run the Python script

```bash
python stego_huffman.py
```

---

## 🚀 Usage

### Option 1️⃣: Encode text → compress → hide in image

- Input your secret text
- Provide a cover image path (e.g., `cover.png`)
- The tool will:
  - Compress the text using Huffman encoding
  - Embed the encoded bits into the image using LSB
  - Save the output as `encoded_image.png`

### Option 2️⃣: Extract & decode from image

- Provide the encoded image path
- The tool will:
  - Extract the embedded bits
  - Decode them using cached Huffman codes
  - Display the original hidden message

> ⚠️ Huffman codes are cached only during the current session. You must encode before decoding.

---

## 🧠 How It Works

### Huffman Encoding (C++)

- Compresses input text into binary using frequency-based codes
- Outputs:
  - Encoded bit string
  - Character-to-code mapping

### Steganography (Python)

- Embeds bits into the least significant bits of RGB pixels
- Prepends a 24-bit header indicating bit length
- Extracts and reconstructs the bit stream for decoding

---

## 🧹 Limitations

- Only supports RGB images (PNG recommended)
- Huffman codes are not embedded in the image — decoding requires session cache
- No encryption — this is compression + hiding, not secure messaging

---

## 📬 Contributions

Feel free to fork, improve, or extend:
- Embed Huffman codes into image metadata
- Add GUI or web frontend
- Support batch encoding/decoding
---

## 🖼️ Steganography Web App (React + Flask)

A modern, minimalist web interface to hide and reveal secret messages inside images using Huffman compression and LSB steganography. Built with React and Lucide icons, powered by a Flask backend.

### 🚀 Features

- 🔐 Encode text into images using Huffman compression  
- 🧠 Decode hidden messages from encoded images  
- 📉 Displays compression stats and bit usage  
- 🖼️ Drag-and-drop or click-to-upload image support  
- ⚡ Responsive UI with loading animation and error handling  

### 🛠 Tech Stack

| Frontend | Backend |
|----------|---------|
| React (Vite) | Flask (Python) |
| Lucide React Icons | Pillow (Image processing) |
| Tailwind CSS (optional) | Huffman encoder (C++) |

### 📦 Installation

#### 1. Clone the repo

```bash
git clone https://github.com/your-username/steganography-app.git
cd steganography-app
```

#### 2. Install frontend dependencies

```bash
npm install
```

#### 3. Start the frontend

```bash
npm run dev
```

#### 4. Start the Flask backend

Make sure your Flask server is running on `http://localhost:5000` and supports:

- `POST /encode` → accepts image + text, returns encoded image URL + stats  
- `POST /decode` → accepts image, returns decoded text  

### 🌐 Usage

#### Encode Mode

1. Select or drag an image (PNG/JPG/BMP)  
2. Enter your secret message  
3. Click **Encode & Hide**  
4. Download the encoded image  

#### Decode Mode

1. Select an encoded image  
2. Click **Extract & Decode**  
3. View the hidden message  

### 📬 API Contract

#### POST /encode

- FormData:
  - `image`: image file
  - `text`: string
- Response:
```json
{
  "encoded_image_url": "/static/encoded_image.png",
  "bits": 120,
  "compression": 45.8
}
```

#### POST /decode

- FormData:
  - `image`: encoded image file
- Response:
```json
{
  "decoded_text": "Your secret message"
}
```

### 📄 License

MIT License — free to use, modify, and share.

---