from flask import Flask, request, jsonify
import requests
from mutagen.mp3 import MP3
from io import BytesIO

app = Flask(__name__)

@app.route('/get-duration')
def get_duration():
    urls = request.args.get('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    durations = []

    for url in urls.split(','):
        try:
            url = url.strip()
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*",
            }
            r = requests.get(url, headers=headers, timeout=10)

            # HTTP hatası mı? (örnek: 403, 404, 500)
            if r.status_code != 200:
                durations.append(None)
                continue

            # MP3 değilse atla
            content_type = r.headers.get("Content-Type", "")
            if "audio" not in content_type and "mpeg" not in content_type:
                durations.append(None)
                continue

            # MP3 uzunluğunu ölç
            audio = MP3(BytesIO(r.content))
            durations.append(round(audio.info.length, 2))

        except Exception as e:
            durations.append(None)

    return jsonify({"durations": durations})
