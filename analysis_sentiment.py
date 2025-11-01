import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, List
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import requests
from PIL import Image

# Initialize the NLTK sentiment analyzer once
# Ensure you have run `python download_nltk_data.py` in your Dockerfile
try:
    sentiment_analyzer = SentimentIntensityAnalyzer()
except LookupError:
    print("NLTK 'vader_lexicon' not found. Make sure it's downloaded.")
    nltk.download('vader_lexicon')
    sentiment_analyzer = SentimentIntensityAnalyzer()

# --- THIS PART IS CORRECT ---
# Load the sentiment model from the local directory
sentiment_pipeline = pipeline("sentiment-analysis", model="./local-model")
print("Successfully loaded LOCAL sentiment model.")


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
    Analyzes the sentiment of a given text and returns the scores.
    """
    if not text:
        return {}
    scores = sentiment_analyzer.polarity_scores(text)
    return scores


# --- THIS IS THE UPDATED PART ---
# Load the image captioning model and its processor from their LOCAL directory
image_captioning_processor = None
image_captioning_model = None
IMAGE_MODEL_PATH = "./local-image-model" # Path we will use in the download script

try:
    # This now loads from the local folder, not the internet
    image_captioning_processor = BlipProcessor.from_pretrained(IMAGE_MODEL_PATH)
    image_captioning_model = BlipForConditionalGeneration.from_pretrained(IMAGE_MODEL_PATH)
    print("Successfully loaded LOCAL Image Captioning model.")
except ImportError:
    print("Could not import Blip model. Please ensure 'transformers', 'torch', and 'Pillow' are installed.")
except Exception as e:
    print(f"An error occurred while loading the LOCAL image captioning model from {IMAGE_MODEL_PATH}: {e}")
    print("Make sure the model was downloaded correctly during the build.")


def analyze_image_content(image_url: str) -> str:
    """
    Downloads an image from a URL and generates a text description using a vision model.
    """
    if not image_url or not image_captioning_model or not image_captioning_processor:
        return "Could not analyze image (model not loaded)."

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

