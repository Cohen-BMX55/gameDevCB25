from flask import Flask, request, jsonify, render_template
import os
import asyncio
from flask_cors import CORS

# Horde SDK v0.18.0 imports
from horde_sdk import AsyncStableHordeClient
from horde_sdk.models import StableHordeGenerationRequest

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("AI_HORDE_KEY", "0000000000")  # use env var on Render

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    async def run_horde(prompt):
        client = AsyncStableHordeClient(api_key=API_KEY)
        # Use StableHordeGenerationRequest instead of old ImageGenerateAsyncRequest
        gen_request = StableHordeGenerationRequest(
            prompt=prompt,
            # width, height, steps, sampler, etc. can be customized
            steps=25,
            width=512,
            height=512,
            nsfw=False
        )

        # Submit job
        job_response = await client.generate_async(gen_request)
        job_id = job_response.id

        # Poll for result
        while True:
            status = await client.get_status(job_id)
            if status.generations and len(status.generations) > 0:
                break
            await asyncio.sleep(1)

        gen = status.generations[0]
        img_b64 = gen.img
        data_uri = f"data:image/png;base64,{img_b64}"

        return {
            "prompt": prompt,
            "image_base64": img_b64,
            "image_data_uri": data_uri
        }

    result = asyncio.run(run_horde(prompt))
    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
