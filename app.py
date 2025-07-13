from flask import Flask, request, jsonify
import subprocess
import tempfile
import requests
import os

app = Flask(__name__)

def get_mp3_duration_ffprobe(mp3_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(mp3_bytes)
        tmp.flush()
        path = tmp.name

    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0 and result.stdout.strip():
            return round(float(result.stdout.strip()), 2)
        else:
            return None
    finally:
        os.remove(path)

@app.route('/get-duration')
def get_duration():
    urls = request.args.get('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    durations = []

    for url in urls.split(','):
        url = url.strip()
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"}, timeout=10)
            if r.status_code != 200:
                durations.append(None)
                continue
            ct = r.headers.get("Content-Type", "")
            if "audio" not in ct and "mpeg" not in ct:
                durations.append(None)
                continue

            duration = get_mp3_duration_ffprobe(r.content)
            durations.append(duration)

        except Exception:
            durations.append(None)

    return jsonify({"durations": durations})
