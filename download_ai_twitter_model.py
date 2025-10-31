from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SAVE_PATH = "./local-model"

print(f"Downloading model {MODEL_NAME} to {SAVE_PATH}...")

# Download and save both the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

tokenizer.save_pretrained(SAVE_PATH)
model.save_pretrained(SAVE_PATH)

print("Model download complete.")