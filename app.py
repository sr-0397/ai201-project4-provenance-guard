import uuid
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from audit_log import write_log, read_log, get_recent, now_iso
from signals.llm_signal import groq_score
from signals.stylometric_signal import stylometric_score
from signals.confidence import combine_scores
from signals.labels import get_label


load_dotenv()

app = Flask(__name__)

# Replace your existing limiter setup with this:
def get_ip():
    return request.remote_addr or "127.0.0.1"

limiter = Limiter(
    key_func=get_ip,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

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

    # Combined confidence + attribution
    scored = combine_scores(llm, stylo)
    confidence = scored["confidence"]
    attribution = scored["attribution"]

    # Real transparency label
    label = get_label(confidence)

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
        "appeal_reasoning": None,
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


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json(silent=True)

    if not data or "content_id" not in data or "creator_reasoning" not in data:
        return jsonify({"error": "Request must include 'content_id' and 'creator_reasoning' fields."}), 400

    content_id = data["content_id"].strip()
    reasoning = data["creator_reasoning"].strip()

    if not content_id or not reasoning:
        return jsonify({"error": "'content_id' and 'creator_reasoning' cannot be empty."}), 400

    # Find and update the matching log entry
    entries = read_log()
    matched = False

    for entry in entries:
        if entry.get("content_id") == content_id:
            if entry.get("status") == "under_review":
                return jsonify({
                    "message": "An appeal for this content is already under review.",
                    "content_id": content_id,
                }), 200
            entry["status"] = "under_review"
            entry["appeal_reasoning"] = reasoning
            entry["appeal_timestamp"] = now_iso()
            matched = True
            break

    if not matched:
        return jsonify({"error": f"No submission found with content_id '{content_id}'."}), 404

    # Write updated entries back to log
    import json
    with open("audit_log.json", "w") as f:
        json.dump(entries, f, indent=2)

    return jsonify({
        "message": "Your appeal has been received and is under review.",
        "content_id": content_id,
        "status": "under_review",
    }), 200


@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({"entries": get_recent(20)}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True)


# Add this error handler anywhere in app.py
@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

