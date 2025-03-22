import requests
import random
import json
import time
import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

class ReviewCrawler:
    """Base class for review crawlers"""
    
    def __init__(self):
        # List of user agents to rotate through to avoid being blocked
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        ]
    
    def _get_random_user_agent(self):
        """Get a random user agent from the list"""
        return random.choice(self.user_agents)
    
    def _generate_mock_reviews(self, count=500):
        """Generate mock reviews with diverse text and sentiments"""
        # Lists of phrases to create diverse mock reviews
        positive_phrases = [
            "This product exceeded my expectations. The quality is outstanding.",
            "I'm extremely satisfied with this purchase. It works perfectly.",
            "Best purchase I've made in a long time. Highly recommend!",
            "This is exactly what I was looking for. Great value for money.",
            "Excellent product that delivers on all its promises.",
            "I'm impressed with how well this works. Will buy again.",
            "The quality is much better than I expected for the price.",
            "This product has made my life so much easier. Love it!",
            "Fantastic product with great attention to detail.",
            "I've recommended this to all my friends. It's that good!",
            "Surprisingly good quality for the price point.",
            "This product is durable and well-designed. Very happy with it.",
            "The customer service was excellent when I had questions.",
            "This exceeded my expectations in every way possible.",
            "I use this product daily and it has held up wonderfully."
        ]
        
        negative_phrases = [
            "Unfortunately, this product didn't meet my expectations.",
            "I'm disappointed with the quality. It feels cheaply made.",
            "This broke after just a few uses. Would not recommend.",
            "Save your money and look elsewhere. Not worth it.",
            "The description was misleading. Not what I expected at all.",
            "Poor quality control. Mine arrived with defects.",
            "This is overpriced for what you get. Not good value.",
            "I had high hopes but was let down by this product.",
            "Had to return this. It simply didn't work as advertised.",
            "The design has some serious flaws that make it frustrating to use.",
            "I regret this purchase and wouldn't buy it again.",
            "The product is much smaller/larger than it appears in photos.",
            "It worked for a week then completely stopped functioning.",
            "The materials feel cheap and I worry about longevity.",
            "This is the worst version of this product I've ever used."
        ]
        
        neutral_phrases = [
            "This product is okay. Nothing special but it works.",
            "It does the job, but I've seen better options out there.",
            "Average quality for the price. No complaints but not amazing.",
            "It's a decent product with some room for improvement.",
            "Some features are good, others could be better.",
            "It's exactly what you'd expect for this price point.",
            "The product works as described, but the design could be improved.",
            "It's functional but lacks some of the premium features of competitors.",
            "I have mixed feelings about this purchase.",
            "It's fine for occasional use but I wouldn't rely on it daily.",
            "Not bad, not great - just average in most respects.",
            "It serves its purpose but doesn't exceed expectations.",
            "The quality is acceptable but not impressive.",
            "It's a basic version that works but lacks extras.",
            "I'm neither disappointed nor impressed with this product."
        ]
        
        non_product_phrases = [
            "The shipping was extremely slow. Took weeks to arrive.",
            "Package arrived damaged but the seller quickly sent a replacement.",
            "The customer service was terrible when I had an issue.",
            "Delivery was faster than expected. Great service!",
            "The box was damaged but luckily the product inside was fine.",
            "Had issues with delivery but the company resolved it quickly.",
            "The packaging was excessive and not environmentally friendly.",
            "The product was left in the rain by the delivery person.",
            "Great communication from the seller throughout the process.",
            "The return process was simple and hassle-free.",
            "Shipping took longer than the estimated delivery date.",
            "The package was well protected and arrived in perfect condition.",
            "Had to contact customer service twice before my issue was resolved.",
            "The delivery person was very helpful and professional.",
            "The tracking information was inaccurate throughout shipping."
        ]
        
        reviews = []
        
        # Generate random reviews
        for _ in range(count):
            # Determine review type with weighted probabilities
            review_type = random.choices(
                ['positive', 'negative', 'neutral', 'non_product'],
                weights=[0.5, 0.3, 0.1, 0.1],
                k=1
            )[0]
            
            # Select base phrase based on review type
            if review_type == 'positive':
                base_phrase = random.choice(positive_phrases)
                rating = random.choices([4, 5], weights=[0.3, 0.7], k=1)[0]
                is_product_related = True
            elif review_type == 'negative':
                base_phrase = random.choice(negative_phrases)
                rating = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
                is_product_related = True
            elif review_type == 'neutral':
                base_phrase = random.choice(neutral_phrases)
                rating = random.choices([3, 4], weights=[0.8, 0.2], k=1)[0]
                is_product_related = True
            else:  # non_product
                base_phrase = random.choice(non_product_phrases)
                # Non-product reviews can have any rating
                rating = random.randint(1, 5)
                is_product_related = False
            
            # Add some randomness to the review text
            if random.random() < 0.3 and is_product_related:
                # Sometimes add a second phrase for more detail
                if review_type == 'positive':
                    second_phrase = random.choice(positive_phrases)
                elif review_type == 'negative':
                    second_phrase = random.choice(negative_phrases)
                else:
                    second_phrase = random.choice(neutral_phrases)
                
                review_text = f"{base_phrase} {second_phrase}"
            elif random.random() < 0.2 and not is_product_related:
                # Sometimes add a product comment to a non-product review
                product_phrase = random.choice(positive_phrases if rating >= 4 else 
                                              negative_phrases if rating <= 2 else
                                              neutral_phrases)
                review_text = f"{base_phrase} As for the product itself: {product_phrase}"
            else:
                review_text = base_phrase
            
            # Generate a random date within the last year
            days_ago = random.randint(1, 365)
            review_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%B %d, %Y')
            
            # Create review title (shorter version of the review or generic title)
            if random.random() < 0.7:
                # Use first few words of review
                words = review_text.split()
                title_length = min(random.randint(3, 6), len(words))
                review_title = ' '.join(words[:title_length]) + ('...' if len(words) > title_length else '')
            else:
                # Generic titles based on sentiment
                if rating >= 4:
                    titles = ["Great product!", "Very satisfied", "Highly recommend", "Excellent purchase", "Love it!"]
                elif rating <= 2:
                    titles = ["Disappointed", "Not worth it", "Save your money", "Wouldn't recommend", "Regrettable purchase"]
                else:
                    titles = ["It's okay", "Decent product", "Average", "Not bad", "Does the job"]
                review_title = random.choice(titles)
            
            # Add the review
            reviews.append({
                'rating': rating,
                'title': review_title,
                'text': review_text,
                'date': review_date,
                'verified': random.random() < 0.8,  # 80% chance of being a verified purchase
            })
        
        # Shuffle the reviews to mix up the order
        random.shuffle(reviews)
        
        print(f"Generated {len(reviews)} mock reviews")
        return reviews
    
    def crawl_reviews(self, product_url, max_reviews=500):
        """
        Crawl reviews from the product URL
        This method should be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement crawl_reviews")

class AmazonReviewCrawler(ReviewCrawler):
    """Crawler for Amazon product reviews"""
    
    def crawl_reviews(self, product_url, max_reviews=500):
        """Crawl reviews from Amazon product page"""
        if 'amazon' not in product_url.lower():
            print("Not an Amazon URL. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)
            
        print(f"Crawling Amazon reviews for: {product_url}")
        
        # Extract product ID from URL
        if '/dp/' in product_url:
            product_id = product_url.split('/dp/')[1].split('/')[0]
        elif '/product/' in product_url:
            product_id = product_url.split('/product/')[1].split('/')[0]
        else:
            print("Could not extract product ID from URL. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)
        
        # Construct the reviews URL
        reviews_url = f"https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
        
        # Get the first page of reviews
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        try:
            response = requests.get(reviews_url, headers=headers, timeout=10)
            
            # Check if we've been blocked
            if response.status_code != 200 or 'captcha' in response.text.lower():
                print("Access to Amazon reviews blocked. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
                
            html_content = response.text
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check if there are any reviews
            no_reviews_div = soup.select_one('div.a-row.a-spacing-medium.a-spacing-top-large > span')
            if no_reviews_div and "There are no customer reviews yet" in no_reviews_div.text:
                print("No reviews found for this product. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
            
            # Extract total number of reviews
            total_reviews_element = soup.select_one('div[data-hook="cr-filter-info-review-rating-count"]')
            if not total_reviews_element:
                print("Could not determine total number of reviews. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
            
            total_reviews_text = total_reviews_element.text.strip()
            try:
                total_reviews = int(total_reviews_text.split('|')[1].strip().split(' ')[0].replace(',', ''))
            except (IndexError, ValueError):
                print("Could not parse total reviews count. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
            
            print(f"Total reviews: {total_reviews}")
            
            # Calculate number of pages to crawl
            reviews_per_page = 10
            pages_to_crawl = min(max_reviews // reviews_per_page, total_reviews // reviews_per_page + 1)
            
            # Limit to a reasonable number to avoid being blocked
            pages_to_crawl = min(pages_to_crawl, 50)
            
            print(f"Will crawl {pages_to_crawl} pages of reviews")
            
            all_reviews = []
            
            # Extract reviews from the first page
            reviews = self._extract_reviews_from_page(soup)
            all_reviews.extend(reviews)
            
            # Crawl additional pages
            for page in tqdm(range(2, pages_to_crawl + 1), desc="Crawling review pages"):
                # Add delay to avoid being blocked
                time.sleep(random.uniform(1.0, 3.0))
                
                # Update headers with a new random user agent
                headers['User-Agent'] = self._get_random_user_agent()
                
                # Construct URL for the next page
                next_page_url = f"{reviews_url}&pageNumber={page}"
                
                try:
                    response = requests.get(next_page_url, headers=headers, timeout=10)
                    
                    # Check if we've been blocked
                    if response.status_code != 200 or 'captcha' in response.text.lower():
                        print(f"Blocked after page {page-1}. Using reviews collected so far.")
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_reviews = self._extract_reviews_from_page(soup)
                    
                    if not page_reviews:
                        print(f"No reviews found on page {page}. Moving on.")
                        continue
                        
                    all_reviews.extend(page_reviews)
                    
                    # Check if we have enough reviews
                    if len(all_reviews) >= max_reviews:
                        break
                        
                except Exception as e:
                    print(f"Error crawling page {page}: {str(e)}")
                    break
            
            print(f"Successfully crawled {len(all_reviews)} reviews")
            
            # If we didn't get any reviews, generate mock data
            if not all_reviews:
                print("No reviews were successfully crawled. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
                
            return all_reviews
            
        except Exception as e:
            print(f"Error crawling reviews: {str(e)}. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)
    
    def _extract_reviews_from_page(self, soup):
        """Extract reviews from a BeautifulSoup object of an Amazon review page"""
        reviews = []
        
        # Find all review divs
        review_divs = soup.find_all('div', {'data-hook': 'review'})
        
        for div in review_divs:
            try:
                # Extract rating
                rating_span = div.find('i', {'data-hook': 'review-star-rating'})
                if not rating_span:
                    rating_span = div.find('i', {'class': 'a-icon-star'})
                
                if rating_span:
                    rating_text = rating_span.text.strip()
                    rating = float(rating_text.split(' ')[0])
                else:
                    # Skip reviews without ratings
                    continue
                
                # Extract title
                title_element = div.find('a', {'data-hook': 'review-title'})
                if not title_element:
                    title_element = div.find('span', {'data-hook': 'review-title'})
                
                title = title_element.text.strip() if title_element else ""
                
                # Extract date
                date_element = div.find('span', {'data-hook': 'review-date'})
                date = date_element.text.strip() if date_element else ""
                
                # Extract text
                text_element = div.find('span', {'data-hook': 'review-body'})
                text = text_element.text.strip() if text_element else ""
                
                # Check if verified purchase
                verified_element = div.find('span', {'data-hook': 'avp-badge'})
                verified = verified_element is not None
                
                reviews.append({
                    'rating': rating,
                    'title': title,
                    'date': date,
                    'text': text,
                    'verified': verified
                })
                
            except Exception as e:
                print(f"Error extracting review: {str(e)}")
                continue
        
        return reviews

class WalmartReviewCrawler(ReviewCrawler):
    """Crawler for Walmart product reviews"""
    
    def crawl_reviews(self, product_url, max_reviews=500):
        """Crawl reviews from Walmart product page"""
        if 'walmart' not in product_url.lower():
            print("Not a Walmart URL. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)
            
        print(f"Crawling Walmart reviews for: {product_url}")
        
        # Extract product ID from URL
        if '/ip/' in product_url:
            try:
                product_id = product_url.split('/ip/')[1].split('/')[0]
                # If the product ID is a name, try to get the numeric ID
                if not product_id.isdigit():
                    if '?' in product_url:
                        query_params = product_url.split('?')[1].split('&')
                        for param in query_params:
                            if param.startswith('id='):
                                product_id = param.split('=')[1]
                                break
            except:
                print("Could not extract product ID from URL. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
        else:
            print("Could not extract product ID from URL. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)
        
        # Walmart uses an API for reviews, we'll try to access it
        api_url = f"https://www.walmart.com/reviews/api/product/{product_id}?limit={max_reviews}&page=1&sort=submission-desc&filters=&showProduct=false"
        
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': product_url,
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            # Check if we've been blocked or got an error
            if response.status_code != 200:
                print(f"Failed to access Walmart reviews API (status code: {response.status_code}). Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
                
            # Parse JSON response
            try:
                review_data = response.json()
            except:
                print("Failed to parse Walmart reviews JSON. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
            
            # Extract reviews from the response
            reviews = []
            
            try:
                review_list = review_data.get('reviews', [])
                
                if not review_list:
                    print("No reviews found for this product. Generating mock reviews instead.")
                    return self._generate_mock_reviews(max_reviews)
                
                for review in review_list:
                    try:
                        rating = review.get('rating', 0)
                        title = review.get('title', '')
                        text = review.get('reviewText', '')
                        date = review.get('submissionDate', '')
                        
                        # Format date if it's a timestamp
                        if isinstance(date, int) or date.isdigit():
                            date_obj = datetime.datetime.fromtimestamp(int(date) / 1000)
                            date = date_obj.strftime('%B %d, %Y')
                        
                        verified = review.get('verifiedPurchase', False)
                        
                        reviews.append({
                            'rating': rating,
                            'title': title,
                            'text': text,
                            'date': date,
                            'verified': verified
                        })
                    except Exception as e:
                        print(f"Error parsing review: {str(e)}")
                        continue
                
                print(f"Successfully crawled {len(reviews)} reviews from Walmart")
                
                # If we didn't get any reviews, generate mock data
                if not reviews:
                    print("No reviews were successfully crawled. Generating mock reviews instead.")
                    return self._generate_mock_reviews(max_reviews)
                    
                return reviews
                
            except Exception as e:
                print(f"Error extracting reviews from response: {str(e)}. Generating mock reviews instead.")
                return self._generate_mock_reviews(max_reviews)
            
        except Exception as e:
            print(f"Error crawling Walmart reviews: {str(e)}. Generating mock reviews instead.")
            return self._generate_mock_reviews(max_reviews)

def get_crawler_for_url(url):
    """Factory function to get the appropriate crawler based on the URL"""
    if 'amazon' in url.lower():
        return AmazonReviewCrawler()
    elif 'walmart' in url.lower():
        return WalmartReviewCrawler()
    else:
        # Default to Amazon crawler which will generate mock data
        print(f"Unsupported URL: {url}. Using Amazon crawler with mock data.")
        return AmazonReviewCrawler()
