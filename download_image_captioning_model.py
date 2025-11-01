import os
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration
)

#  Image Captioning Model ---
IMAGE_MODEL_NAME = "Salesforce/blip-image-captioning-base"
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

