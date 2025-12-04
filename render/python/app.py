from flask import Flask, request, jsonify, render_template
import os
import asyncio
from horde_sdk.ai_horde_api.ai_horde_clients import AIHordeAPISimpleClient
from horde_sdk.ai_horde_api.apimodels.generate import ImageGenerateAsyncRequest, GenerationInputStable
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow cross-origin requests

API_KEY = os.environ.get("AI_HORDE_KEY", "0000000000")  # Use environment variable on Render

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Use asyncio to run async Horde client in Flask
    async def run_horde(prompt):
        client = AIHordeAPISimpleClient(api_key=API_KEY)
        gen_request = ImageGenerateAsyncRequest(
            prompt=prompt,
            params=GenerationInputStable(),
            nsfw=False,
            censor_nsfw=False
        )
        # Submit job
        try:
            status_response, job_id = await client.image_generate_request(gen_request, timeout=300)
        except Exception as e:
            return {"error": f"Failed to submit generation: {e}"}

        # Poll until generation is ready
        while True:
            check = await client.get_generate_status(job_id)
            if check.generations:
                break
            await asyncio.sleep(1)

        gen = check.generations[0]
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
