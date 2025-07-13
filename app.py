from flask import Flask, request, jsonify
import subprocess
import tempfile
import requests
import os

app = Flask(__name__)

def get_mp3_duration_ffprobe(mp3_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
        temp.write(mp3_bytes)
        temp.flush()
        temp_path = temp.name

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", temp_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return round(float(result.stdout.strip()), 2)
        else:
            return None
    finally:
        os.remove(temp_path)

@app.route('/get-duration')
def get_duration():
    urls = request.args.get('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    durations = []
    for url in urls.split(','):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url.strip(), headers=headers)
            if r.status_code == 200:
                duration = get_mp3_duration_ffprobe(r.content)
                durations.append(duration)
            else:
                durations.append(None)
        except Exception:
            durations.append(None)

    return jsonify({"durations": durations})
