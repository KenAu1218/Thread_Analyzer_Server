# Dockerfile

# 1. Use the official Playwright base image from Microsoft.
# This image includes Python AND all browser dependencies.
FROM mcr.microsoft.com/playwright/python:v1.44.0

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the files needed for installation
COPY requirements.txt .
COPY download_nltk_data.py .

# 4. Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Download the NLTK data
RUN python download_nltk_data.py

# Download language twitter model
COPY download_ai_twitter_model.py .
#    ...and then runs it.
RUN python download_ai_twitter_model.py

# 6. Copy the rest of your application code into the container
COPY . .

# 7. Install the Playwright browsers inside the container
RUN playwright install

# 8. Set the command to run your app
# We use Gunicorn (the production server) to run the 'app' object from 'app.py'
# It binds to 0.0.0.0 and a $PORT variable, which Cloud Run will provide.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]