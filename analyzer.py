import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from tqdm import tqdm

class SentimentAnalyzer:
    def __init__(self):
        # Load pre-trained model and tokenizer
        # Using DistilBERT which is smaller and faster than BERT but still effective
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Check if GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"Using device: {self.device}")
    
    def _classify_text(self, text):
        """Classify text as positive, negative, or neutral"""
        # Truncate text if it's too long to avoid tokenizer errors
        max_length = 512
        if len(text) > max_length * 4:  # Rough character estimate
            text = text[:max_length * 4]
            
        # Tokenize and get prediction
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Get prediction (0 = negative, 1 = positive)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        
        # Convert to sentiment label with confidence
        neg_prob = probabilities[0][0].item()
        pos_prob = probabilities[0][1].item()
        
        # Determine sentiment based on probability
        if pos_prob > 0.7:
            sentiment = "Positive"
        elif neg_prob > 0.7:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        return {
            "sentiment": sentiment,
            "confidence": max(neg_prob, pos_prob),
            "positive_score": pos_prob,
            "negative_score": neg_prob
        }
    
    def _is_product_related(self, text):
        """Check if review is about the product or about shipping/service/etc."""
        shipping_keywords = [
            "shipping", "delivery", "arrived", "package", "box", "damaged",
            "return", "refund", "customer service", "late", "delay"
        ]
        
        # Count occurrences of shipping-related keywords
        shipping_count = sum(1 for keyword in shipping_keywords if keyword.lower() in text.lower())
        
        # If more than 2 shipping keywords are found and they make up a significant portion of the text
        words = text.split()
        if shipping_count >= 2 and shipping_count / len(words) > 0.05:
            return False
            
        return True
    
    def _generate_summary(self, text, max_words=50):
        """Generate a simple summary of the review text"""
        # For a more sophisticated summary, we would use a summarization model
        # But for simplicity, we'll just take the first few sentences
        
        sentences = text.split('.')
        summary = ""
        word_count = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            words = sentence.split()
            if word_count + len(words) <= max_words:
                summary += sentence.strip() + ". "
                word_count += len(words)
            else:
                # Add words until we reach the limit
                remaining_words = max_words - word_count
                if remaining_words > 0:
                    summary += " ".join(words[:remaining_words]) + "..."
                break
                
        return summary.strip()
    
    def analyze_reviews(self, reviews):
        """Analyze a list of reviews and return sentiment analysis"""
        if not reviews:
            return {
                "error": "No reviews to analyze"
            }
            
        results = {
            "total_reviews": len(reviews),
            "sentiment_distribution": {
                "Positive": 0,
                "Negative": 0,
                "Neutral": 0
            },
            "average_rating": 0,
            "product_related": 0,
            "non_product_related": 0,
            "detailed_analysis": []
        }
        
        total_rating = 0
        total_positive_score = 0
        total_negative_score = 0
        
        print(f"Analyzing {len(reviews)} reviews...")
        for review in tqdm(reviews):
            # Get the review text and rating
            review_text = review.get('text', '')
            rating = review.get('rating', 0)
            
            if not review_text:
                continue
                
            # Add to total rating
            total_rating += rating
            
            # Check if review is product-related
            is_product_related = self._is_product_related(review_text)
            
            if is_product_related:
                results["product_related"] += 1
            else:
                results["non_product_related"] += 1
            
            # Analyze sentiment
            sentiment_result = self._classify_text(review_text)
            sentiment = sentiment_result["sentiment"]
            
            # Accumulate sentiment scores
            total_positive_score += sentiment_result["positive_score"]
            total_negative_score += sentiment_result["negative_score"]
            
            # Update sentiment distribution
            results["sentiment_distribution"][sentiment] += 1
            
            # Generate summary
            summary = self._generate_summary(review_text)
            
            # Add to detailed analysis
            results["detailed_analysis"].append({
                "rating": rating,
                "sentiment": sentiment,
                "confidence": sentiment_result["confidence"],
                "product_related": is_product_related,
                "summary": summary,
                "review_title": review.get('title', ''),
                "review_date": review.get('date', '')
            })
        
        # Calculate average rating
        if results["total_reviews"] > 0:
            results["average_rating"] = total_rating / results["total_reviews"]
            
            # Calculate overall sentiment score (0-100 scale)
            avg_positive_score = total_positive_score / results["total_reviews"]
            avg_negative_score = total_negative_score / results["total_reviews"]
            
            # Convert to a 0-100 scale where 50 is neutral
            # Higher values are more positive, lower values are more negative
            results["overall_sentiment_score"] = int(avg_positive_score * 100)
            
            # Determine overall sentiment category
            if results["overall_sentiment_score"] >= 75:
                results["overall_sentiment"] = "Very Positive"
            elif results["overall_sentiment_score"] >= 60:
                results["overall_sentiment"] = "Positive"
            elif results["overall_sentiment_score"] >= 40:
                results["overall_sentiment"] = "Neutral"
            elif results["overall_sentiment_score"] >= 25:
                results["overall_sentiment"] = "Negative"
            else:
                results["overall_sentiment"] = "Very Negative"
        
        # Add overall summary
        results["overall_summary"] = self._generate_overall_summary(results)
        
        return results
    
    def _generate_overall_summary(self, results):
        """Generate an overall summary of the analysis"""
        total = results["total_reviews"]
        if total == 0:
            return "No reviews to analyze."
            
        pos_percent = (results["sentiment_distribution"]["Positive"] / total) * 100
        neg_percent = (results["sentiment_distribution"]["Negative"] / total) * 100
        neutral_percent = (results["sentiment_distribution"]["Neutral"] / total) * 100
        
        product_related_percent = (results["product_related"] / total) * 100
        
        summary = f"Analysis of {total} reviews shows {pos_percent:.1f}% positive, {neg_percent:.1f}% negative, and {neutral_percent:.1f}% neutral sentiment. "
        summary += f"Average rating is {results['average_rating']:.1f}/5. "
        summary += f"{product_related_percent:.1f}% of reviews are product-related, while {100-product_related_percent:.1f}% discuss shipping, service, or other non-product aspects."
        
        return summary
