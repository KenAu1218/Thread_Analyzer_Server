# How to build Thread_Analyzer_Server 
1. Install all the Python packages from requirements.txt
   
   pip install -r requirements.txt

2. Download the NLTK 'vader_lexicon' data
   
   python3 download_nltk_data.py

3. Download the two AI models
   
   python3 download_ai_twitter_model.py

4. Download the two AI models
   
   python3 download_image_captioning_model.py

5. Install the Playwright browsers
   
   playwright install

6. Run commend to start the server in terminal
   
   python app.py or python3 app.py



# Production

https://threadsentimentanalyer.netlify.app/

PS: This project only support threads in english language, the model for sentiment analyzing using is cardiffnlp/twitter-roberta-base-sentiment-latest

# Demo link

https://drive.google.com/file/d/1App419NbEbT6__zRbD3PBKeuKHd1vxWn/view?usp=sharing



