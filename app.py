from flask import Flask, request, jsonify
import requests
from tinytag import TinyTag
from io import BytesIO
import logging

app = Flask(__name__)

# Basit log ayarı
logging.basicConfig(level=logging.INFO)

@app.route('/get-duration')
def get_duration():
    urls_param = request.args.get('urls')
    if not urls_param:
        return jsonify({"error": "No URLs provided"}), 400

    urls = urls_param.split(',')
    durations = []

    for url in urls:
        url = url.strip()
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code != 200:
                logging.warning(f"Failed to fetch: {url} - Status: {r.status_code}")
                durations.append(None)
                continue

            # TinyTag MP3 duration
            tag = TinyTag.get(BytesIO(r.content), filetype='mp3')
            duration = round(tag.duration, 2) if tag.duration else None

            if duration is None:
                logging.warning(f"Could not read duration: {url}")

            durations.append(duration)

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
            durations.append(None)

    return jsonify({"durations": durations})
