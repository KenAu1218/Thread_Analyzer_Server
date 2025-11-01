import os
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BlipProcessor,
    BlipForConditionalGeneration
)

#  Sentiment Model ---
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

