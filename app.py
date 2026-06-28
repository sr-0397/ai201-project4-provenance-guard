import uuid
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from audit_log import write_log, get_recent, now_iso
from signals.llm_signal import groq_score
from signals.stylometric_signal import stylometric_score
from signals.confidence import combine_scores

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json(silent=True)

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({"error": "Request must include 'text' and 'creator_id' fields."}), 400

    text = data["text"].strip()
    creator_id = data["creator_id"].strip()

    if not text:
        return jsonify({"error": "'text' field cannot be empty."}), 400

    content_id = str(uuid.uuid4())

    # Signal 1: LLM
    llm_result = groq_score(text)
    llm = llm_result["score"]

    # Signal 2: Stylometrics
    stylo_result = stylometric_score(text)
    stylo = stylo_result["score"]

    # Combined confidence score
    scored = combine_scores(llm, stylo)
    confidence = scored["confidence"]
    attribution = scored["attribution"]

    # Placeholder label until Milestone 5
    label = "Placeholder label — full label generation coming in Milestone 5."

    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": now_iso(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm,
        "llm_reasoning": llm_result["reasoning"],
        "stylometric_score": stylo,
        "stylometric_metrics": stylo_result["metrics"],
        "status": "classified",
    }
    write_log(log_entry)

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "llm_score": llm,
        "stylometric_score": stylo,
    }), 200


@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({"entries": get_recent(20)}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True)