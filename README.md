# Thread_Analyer_Server in debug mode

# 1. Install all the Python packages from requirements.txt
pip install -r requirements.txt

# 2. Download the NLTK 'vader_lexicon' data
python3 download_nltk_data.py

# 3. Download the two AI models 
python3 download_ai_twitter_model.py

#  Download the two AI models 
python3 download_image_captioning_model.py

# 4. Install the Playwright browsers
playwright install

# 5. Run commend to start the server in terminal
python app.py or python3 app.py




