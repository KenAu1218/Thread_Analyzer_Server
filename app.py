import os

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from scrape_thread import scrape_thread

# Suppress Hugging Face tokenizer warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize the Flask app
app = Flask(__name__)
# Enable CORS to allow your front-end to make requests to this server
CORS(app)


# Define the API endpoint
@app.route('/analyze', methods=['POST'])
def analyze_thread_endpoint():
    """
    This function is triggered when the front-end sends a request to the /analyze URL.
    """
    # 1. Get the URL from the incoming request data
    data = request.get_json()
    url = data.get('url')

    if not url:
        # Return an error if the URL is missing
        return jsonify({"error": "URL is required"}), 400

    try:
        # 2. Run your existing scraping function
        print(f"Received request to analyze: {url}")
        scraped_data = scrape_thread(url)
        print("Scraping and analysis complete.")

        # 3. Return the results as a JSON response
        return jsonify(scraped_data)

    except Exception as e:
        # Handle any errors that occur during scraping
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


# --- NEW: Image Proxy Endpoint ---
# This new route is dedicated to fetching images.
@app.route('/image-proxy')
def image_proxy():
    """
    Fetches an image from a given URL and returns it to the client.
    This bypasses CORS issues for client-side image loading.
    """
    image_url = request.args.get('url')
    if not image_url:
        return "URL parameter is required", 400

    try:
        # Use a User-Agent to pretend we're a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use stream=True to efficiently handle the image data
        response = requests.get(image_url, stream=True, headers=headers, timeout=10)
        response.raise_for_status()

        # Send the raw image data back with the correct content type
        return Response(response.iter_content(chunk_size=1024), content_type=response.headers['Content-Type'])

    except requests.exceptions.RequestException as e:
        print(f"Error proxying image {image_url}: {e}")
        return "Could not fetch image", 500

# This allows you to run the app by executing "python app.py"
if __name__ == '__main__':
    app.run(debug=True)