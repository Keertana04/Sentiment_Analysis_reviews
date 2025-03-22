import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules
from crawler import get_crawler_for_url
from analyzer import SentimentAnalyzer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get the product URL from the form
        product_url = request.form.get('product_url')
        
        if not product_url or not ('amazon' in product_url.lower() or 'walmart' in product_url.lower()):
            return jsonify({'error': 'Please provide a valid Amazon or Walmart product URL'}), 400
        
        # Initialize the appropriate crawler and get reviews
        # The crawler will automatically use mock data if it can't retrieve real reviews
        crawler = get_crawler_for_url(product_url)
        reviews = crawler.crawl_reviews(product_url, max_reviews=500)
        
        if not reviews:
            return jsonify({'error': 'Could not retrieve reviews from the provided URL'}), 400
            
        # Save reviews to a JSON file for reference
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        product_id = product_url.split('/dp/')[-1].split('/')[0] if '/dp/' in product_url else product_url.split('/')[-1].split('?')[0]
        reviews_file = os.path.join(data_dir, f'{product_id}_reviews.json')
        
        with open(reviews_file, 'w') as f:
            json.dump(reviews, f, indent=2)
        
        # Analyze the reviews
        analyzer = SentimentAnalyzer()
        analysis_results = analyzer.analyze_reviews(reviews)
        
        return jsonify(analysis_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    # For checking if the server is running
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5004)
