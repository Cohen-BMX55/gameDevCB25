# app.py
import os
import asyncio

from flask import Flask, request, jsonify, render_template
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

    client = AIHordeAPISimpleClient()

    req = ImageGenerateAsyncRequest(
        apikey=API_KEY,
        prompt=prompt,
        model="stable_diffusion",
        params=ImageGenerationInputPayload(
            width=512,
            height=512,
            steps=25,
            n=1
        ),
        nsfw=False,
        censor_nsfw=False,
    )

    # Submit job
    submit_resp = await client.image_generate_request(req)
    job_id = submit_resp.id

    # Poll for completion
    while True:
        status = await client.image_generate_status(job_id)
        if status.done:
            break
        await asyncio.sleep(1)

    img_b64 = status.generations[0].img
    data_uri = f"data:image/png;base64,{img_b64}"

    return jsonify({"image_base64": img_b64, "image_data_uri": data_uri})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
