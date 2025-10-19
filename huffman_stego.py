import subprocess
import os
import sys
import platform
from PIL import Image

class HuffmanCPP:
    def __init__(self):
        # Auto-detect executable name based on OS
        if platform.system() == "Windows":
            self.exe = "huffman.exe"
        else:
            self.exe = "./huffman"
        
        if not os.path.exists(self.exe):
            raise FileNotFoundError(
                f"Huffman executable not found: {self.exe}\n"
                f"Compile with: g++ -O2 -o huffman huffman.cpp"
            )

    def encode(self, text):
        """Encode text using C++ Huffman encoder"""
        try:
            result = subprocess.run(
                [self.exe, "encode", text],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Encoding failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Huffman executable not found: {self.exe}\n"
                f"Make sure you compiled with: g++ -O2 -o huffman huffman.cpp"
            )

        lines = result.stdout.strip().split('\n')
        if len(lines) < 1:
            raise ValueError("Invalid encoder output")

        encoded_bits = lines[0]
        codes = {}

        for line in lines[1:]:
            parts = line.split()
            if len(parts) == 2:
                try:
                    char_code, code = int(parts[0]), parts[1]
                    codes[chr(char_code)] = code
                except (ValueError, IndexError):
                    continue

        return encoded_bits, codes

    def decode(self, encoded_bits, codes):
        """Decode using C++ Huffman decoder"""
        # Build code map input
        code_map = "\n".join(f"{ord(char)} {code}" for char, code in codes.items())

        try:
            result = subprocess.run(
                [self.exe, "decode", encoded_bits],
                input=code_map,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Decoding failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Huffman executable not found: {self.exe}\n"
                f"Make sure you compiled with: g++ -O2 -o huffman huffman.cpp"
            )

        return result.stdout


class Steganography:
    @staticmethod
    def embed(image_path, bits, output_path="encoded_image.png"):
        """Embed bits in image using LSB of RGB channels"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = Image.open(image_path).convert("RGB")
        pixels = list(img.getdata())

        bit_length = len(bits)
        required_pixels = (bit_length + 23) // 8
        if len(pixels) < required_pixels + 8:
            raise ValueError(
                f"Image too small. Need {required_pixels + 8} pixels, have {len(pixels)}"
            )

        # Header: 24-bit length
        header = format(bit_length, "024b")
        all_bits = header + bits

        new_pixels = []
        bit_index = 0

        for pixel in pixels:
            r, g, b = pixel
            if bit_index < len(all_bits):
                r = (r & ~1) | int(all_bits[bit_index])
                bit_index += 1
            if bit_index < len(all_bits):
                g = (g & ~1) | int(all_bits[bit_index])
                bit_index += 1
            if bit_index < len(all_bits):
                b = (b & ~1) | int(all_bits[bit_index])
                bit_index += 1
            new_pixels.append((r, g, b))

        img.putdata(new_pixels)
        img.save(output_path)
        return output_path

    @staticmethod
    def extract(image_path):
        """Extract bits from image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = Image.open(image_path).convert("RGB")
        pixels = list(img.getdata())

        if len(pixels) < 8:
            raise ValueError("Image too small to contain embedded data")

        # Extract header (24 bits)
        bits = ""
        for i in range(8):
            r, g, b = pixels[i]
            bits += str(r & 1)
            bits += str(g & 1)
            bits += str(b & 1)

        bit_count = int(bits, 2)

        # Extract data bits
        extracted_bits = ""
        for pixel in pixels:
            r, g, b = pixel
            extracted_bits += str(r & 1)
            extracted_bits += str(g & 1)
            extracted_bits += str(b & 1)
            if len(extracted_bits) >= 24 + bit_count:
                break

        return extracted_bits[24 : 24 + bit_count]


def main():
    print("\n" + "=" * 60)
    print("🔐 STEGANOGRAPHY WITH HUFFMAN ENCODING (C++ Backend)")
    print("=" * 60)

    try:
        huffman = HuffmanCPP()
        print(f"✅ Found huffman executable: {huffman.exe}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    codes_cache = {}

    while True:
        print("\n1️⃣  Encode text → compress → hide in image")
        print("2️⃣  Extract & decode from image")
        print("3️⃣  Exit")
        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            text = input("\nEnter text to hide: ").strip()
            if not text:
                print("❌ Empty text. Try again.")
                continue

            image_path = input("Enter image path: ").strip().strip('"').strip("'")

            try:
                # Encode with C++ Huffman
                encoded_bits, codes = huffman.encode(text)
                codes_cache = codes  # Cache for decoding

                print(f"\n📊 Original text length: {len(text)} characters ({len(text) * 8} bits)")
                print(f"📊 Encoded bits: {len(encoded_bits)} bits")
                compression = (1 - len(encoded_bits) / (len(text) * 8)) * 100
                print(f"📊 Compression: {compression:.1f}%")

                # Embed in image
                output_path = Steganography.embed(image_path, encoded_bits)
                print(f"\n✅ Encoded image saved: {output_path}")
                print(f"✅ Huffman codes cached for decoding")

            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            image_path = input("\nEnter encoded image path: ").strip().strip('"').strip("'")

            try:
                if not codes_cache:
                    print("❌ No codes cached. Encode text first in this session.")
                    continue

                # Extract bits
                extracted_bits = Steganography.extract(image_path)
                print(f"\n✅ Extracted {len(extracted_bits)} bits from image")

                # Decode with C++ Huffman
                decoded_text = huffman.decode(extracted_bits, codes_cache)
                print(f"✅ Decoded text:\n\n{decoded_text}\n")

            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()