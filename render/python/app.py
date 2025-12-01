import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_API_KEY = os.getenv("HF_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.json.get("prompt")
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {"inputs": prompt}

    response = requests.post(HF_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Generation failed", "details": response.text}), 500

    # HuggingFace returns the image bytes directly
    image_bytes = response.content
    image_base64 = image_bytes.encode("base64").decode()

    return jsonify({"image": image_base64})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
