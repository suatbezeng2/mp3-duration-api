from flask import Flask, request, jsonify
import subprocess
import requests
from io import BytesIO
import tempfile
import os

app = Flask(__name__)

def get_duration_ffprobe(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio.flush()
        temp_path = temp_audio.name

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())
    except Exception:
        duration = None
    finally:
        os.remove(temp_path)

    return round(duration, 2) if duration else None

@app.route('/get-duration')
def get_duration():
    urls = request.args.get('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    durations = []
    for url in urls.split(','):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url.strip(), headers=headers, timeout=10)
            if r.status_code == 200:
                duration = get_duration_ffprobe(r.content)
                durations.append(duration)
            else:
                durations.append(None)
        except Exception:
            durations.append(None)

    return jsonify({"durations": durations})
