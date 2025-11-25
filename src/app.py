"""
Flask application to expose the artist_pulse_job function as a web service.
"""

import os
from flask import Flask, request, jsonify
from main import artist_pulse_job  # assume sua função já existe em src/main.py

app = Flask(__name__)


@app.route("/run", methods=["GET", "POST"])
def run_job():
    """
    Endpoint to trigger the artist pulse job.
    """
    # passa o request do Flask para sua função (ou apenas None se preferir)
    resp, status = artist_pulse_job(request)
    return (resp, status)


@app.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"status": "ok", "message": "Service is running"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
