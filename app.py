from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image
import torch
from realesrgan import RealESRGAN
import os
import io
import requests
import base64

app = Flask(__name__)

SCALE = 4
WEIGHTS_PATH = f"RealESRGAN_x{SCALE}.pth"
WEIGHTS_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5/RealESRGAN_x4.pth"

def download_weights(url, save_path):
    if os.path.isfile(save_path):
        return
    print(f"Downloading model weights from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded weights to {save_path}")

def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RealESRGAN(device, scale=SCALE)
    download_weights(WEIGHTS_URL, WEIGHTS_PATH)
    model.load_weights(WEIGHTS_PATH)
    return model

model = load_model()

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Image Depixelator</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 2em auto; padding: 1em; }
  input[type="file"] { margin-bottom: 1em; }
  button { padding: 0.5em 1em; font-size: 1em; }
  #result img { max-width: 100%; margin-top: 1em; border: 1px solid #ccc; }
  #loading { display: none; color: #555; }
</style>
</head>
<body>
  <h1>Image Depixelator</h1>
  <p>Upload a pixelated image and get a depixelated version.</p>
  <input type="file" id="imageInput" accept="image/*" />
  <br />
  <button onclick="uploadImage()">Depixelate</button>
  <p id="loading">Processing, please wait...</p>
  <div id="result"></div>

<script>
async function uploadImage() {
  const input = document.getElementById('imageInput');
  const resultDiv = document.getElementById('result');
  const loading = document.getElementById('loading');
  resultDiv.innerHTML = '';
  if (!input.files.length) {
    alert('Please select an image file.');
    return;
  }

  const formData = new FormData();
  formData.append('image', input.files[0]);

  loading.style.display = 'block';

  try {
    const response = await fetch('/depixelate', {
      method: 'POST',
      body: formData
    });

    loading.style.display = 'none';

    if (!response.ok) {
      const err = await response.json();
      alert('Error: ' + (err.error || 'Unknown error'));
      return;
    }

    const data = await response.json();
    const imgBase64 = data.image_base64;
    const imgElem = document.createElement('img');
    imgElem.src = 'data:image/jpeg;base64,' + imgBase64;
    resultDiv.appendChild(imgElem);
  } catch (err) {
    loading.style.display = 'none';
    alert('Error: ' + err.message);
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/depixelate", methods=["POST"])
def depixelate_endpoint():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files["image"]
    try:
        image = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400

    try:
        out = model.predict(image)
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

    img_byte_arr = io.BytesIO()
    out.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    # encode image as base64 for JSON transport
    img_base64 = base64.b64encode(img_byte_arr.read()).decode("utf-8")

    return jsonify({"image_base64": img_base64})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
