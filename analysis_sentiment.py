from nltk.sentiment import sentiment_analyzer, SentimentIntensityAnalyzer

from typing import Dict, List

from transformers import pipeline

import requests
from PIL import Image

# Initialize the sentiment analyzer once
sentiment_analyzer = SentimentIntensityAnalyzer()


# Load the model once and reuse it
sentiment_pipeline = pipeline("sentiment-analysis", model="./local-model")

def analyze_sentiment_advanced(text: str):
    """
    Analyzes sentiment using a state-of-the-art Transformer model.
    """
    if not text:
        return None
    results = sentiment_pipeline(text, truncation=True, max_length=512)
    return results[0]

def analyze_sentiment(text: str) -> Dict:
    """
scrape_thread    Analyzes the sentiment of a given text and returns the scores.
    """
    if not text:
        return {}
    scores = sentiment_analyzer.polarity_scores(text)
    return scores



# --- NEW: Image Captioning Model ---
# Load the image captioning model and its processor once
image_captioning_processor = None
image_captioning_model = None
try:
    # This downloads the model the first time it's run
    from transformers import BlipProcessor, BlipForConditionalGeneration
    image_captioning_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    image_captioning_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    print("Successfully loaded Image Captioning model.")
except ImportError:
    print("Could not import Blip model. Please ensure 'transformers', 'torch', and 'Pillow' are installed.")
except Exception as e:
    print(f"An error occurred while loading the image captioning model: {e}")


def analyze_image_content(image_url: str) -> str:
    """
    Downloads an image from a URL and generates a text description using a vision model.
    """
    if not image_url or not image_captioning_model:
        return "Could not analyze image."

    try:
        # 1. Download the image and open it
        response = requests.get(image_url, stream=True, timeout=15)
        response.raise_for_status()
        image = Image.open(response.raw).convert('RGB')

        # 2. Prepare the image for the model
        inputs = image_captioning_processor(images=image, return_tensors="pt")

        # 3. Generate a caption
        pixel_values = inputs.pixel_values
        out = image_captioning_model.generate(pixel_values=pixel_values, max_length=50)

        # 4. Decode the caption into readable text
        caption = image_captioning_processor.decode(out[0], skip_special_tokens=True)
        return caption.strip()

    except Exception as e:
        print(f"Failed to analyze image at {image_url}: {e}")
        return "Failed to analyze image."