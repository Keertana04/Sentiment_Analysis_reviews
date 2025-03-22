# Amazon/Walmart Review Analyzer

This web application crawls Amazon and Walmart product reviews and performs sentiment analysis using an open-source GenAI model.

## Features

- Takes an Amazon or Walmart product URL as input
- Crawls up to 500 reviews across different rating categories
- Analyzes sentiment in multiple dimensions:
  - Rating: Positive, Negative, Neutral
  - Detailed summary (50 words)
  - Identifies non-product related feedback (shipping, returns, etc.)
  - Overall sentiment score with visual indicator

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5004`

## Technologies Used

- Flask: Web framework
- BeautifulSoup4: Web scraping
- Transformers: Sentiment analysis with open-source models
- Bootstrap: Frontend styling

## Notes

- The application automatically falls back to mock data if it encounters issues with crawling real reviews
- User-agent rotation is implemented to reduce the chance of being blocked by Amazon or Walmart
