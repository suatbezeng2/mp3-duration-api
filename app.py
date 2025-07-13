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
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url.strip(), headers=headers)
            audio = MP3(BytesIO(r.content))
            durations.append(round(audio.info.length, 2))
        except Exception as e:
            durations.append(None)

    return jsonify({"durations": durations})
