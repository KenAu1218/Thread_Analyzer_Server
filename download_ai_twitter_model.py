import os
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BlipProcessor,
    BlipForConditionalGeneration
)

# --- 1. Sentiment Model ---
SENTIMENT_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SENTIMENT_SAVE_PATH = "./local-model" # Matches your scrape_thread.py

print(f"Downloading sentiment model: {SENTIMENT_MODEL_NAME}...")

# Create directory if it doesn't exist
os.makedirs(SENTIMENT_SAVE_PATH, exist_ok=True)

# Download and save both the tokenizer and the model
sentiment_tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL_NAME)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL_NAME)

sentiment_tokenizer.save_pretrained(SENTIMENT_SAVE_PATH)
sentiment_model.save_pretrained(SENTIMENT_SAVE_PATH)

print("Sentiment model download complete.")


# --- 2. Image Captioning Model ---
IMAGE_MODEL_NAME = "Salesforce/blip-image-captioning-large"
IMAGE_SAVE_PATH = "./local-image-model" # New path for the image model

print(f"Downloading image captioning model: {IMAGE_MODEL_NAME}...")
print("This may take several minutes and download a few gigabytes...")

# Create directory if it doesn't exist
os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)

# Download and save both the processor and the model
image_processor = BlipProcessor.from_pretrained(IMAGE_MODEL_NAME)
image_model = BlipForConditionalGeneration.from_pretrained(IMAGE_MODEL_NAME)

image_processor.save_pretrained(IMAGE_SAVE_PATH)
image_model.save_pretrained(IMAGE_SAVE_PATH)

print("Image captioning model download complete.")
print("All models have been downloaded successfully.")

