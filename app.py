from flask import Flask, jsonify, render_template
import subprocess
import threading
import time
import json
import os

app = Flask(__name__)

DATA_FILENAME = "worldnews_data.json"

def run_reddit_scraper():
    """Runs the Reddit scraping script in a separate process."""
    while True:
        try:
            subprocess.run(["python", "reddit_scraper.py"])
        except Exception as e:
            print(f"Error running scraper: {e}")
        time.sleep(60)

@app.route("/data", methods=["GET"])
def get_data():
    """Returns the collected Reddit data as JSON."""
    try:
        with open(DATA_FILENAME, "r", encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data file not found."}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON data."}), 500

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    if not os.path.exists(DATA_FILENAME):
        with open(DATA_FILENAME, "w") as f:
            json.dump([], f)

    # Start the Reddit scraper in a background thread
    scraper_thread = threading.Thread(target=run_reddit_scraper)
    scraper_thread.daemon = True  # Allow the main thread to exit even if this is running
    scraper_thread.start()

    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
