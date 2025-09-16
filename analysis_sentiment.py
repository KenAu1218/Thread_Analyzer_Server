from nltk.sentiment import sentiment_analyzer, SentimentIntensityAnalyzer

from typing import Dict, List

from transformers import pipeline

# Initialize the sentiment analyzer once
sentiment_analyzer = SentimentIntensityAnalyzer()


# Load the model once and reuse it
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def analyze_sentiment_advanced(text: str):
    """
    Analyzes sentiment using a state-of-the-art Transformer model.
    """
    if not text:
        return {}
    max_length = 512
    truncated_text = text[:max_length]
    results = sentiment_pipeline(truncated_text)
    return results[0]

def analyze_sentiment(text: str) -> Dict:
    """
    Analyzes the sentiment of a given text and returns the scores.
    """
    if not text:
        return {}
    scores = sentiment_analyzer.polarity_scores(text)
    return scores