import os
import base64
from io import BytesIO
from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from PIL import Image

app = Flask(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    provider="auto",
    api_key=os.environ["HF_API_KEY"],
    )


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.json.get("prompt")

    image = client.text_to_image(
        prompt,
        model="ByteDance/SDXL-Lightning",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    image_b64 = base64.b64encode(png_bytes).decode("utf-8")
    
    return jsonify({"image": image_b64})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
