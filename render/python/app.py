# app.py
import os
import asyncio

from flask import Flask, request, jsonify
from flask_cors import CORS

from horde_sdk.ai_horde_api.ai_horde_clients import AIHordeAPISimpleClient
from horde_sdk.ai_horde_api.apimodels.generate._async import (
    ImageGenerateAsyncRequest,
    ImageGenerationInputPayload,
)

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("AI_HORDE_KEY", "0000000000")

@app.route("/")
def index():
    # Flask will look inside templates/ folder automatically
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    async def do_gen(prompt_text):
        client = AIHordeAPISimpleClient()
        # Build request
        req = ImageGenerateAsyncRequest(
            apikey=API_KEY,
            prompt=prompt_text,
            params=ImageGenerationInputPayload(width=512, height=512, steps=25, n=1),
            nsfw=False,
            censor_nsfw=False,
        )
        # Send request & wait
        status_resp, job_id = await client.image_generate_request(req, timeout=300)
        # status_resp.generations holds images once done
        generation = status_resp.generations[0]
        img_b64 = generation.img
        return img_b64

    try:
        img_b64 = asyncio.run(do_gen(prompt))
    except Exception as e:
        return jsonify({"error": "Generation failed", "details": str(e)}), 500

    data_uri = f"data:image/png;base64,{img_b64}"
    return jsonify({"image_base64": img_b64, "image_data_uri": data_uri})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
