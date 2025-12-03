import requests
import sys
import json
from datetime import datetime
import time

class BrandPulseAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        # Default to local FastAPI instance
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"{name} - PASSED")
        else:
            print(f"{name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False

    def test_news_search(self, keyword="Tesla"):
        """Test news search functionality"""
        try:
            payload = {"keyword": keyword}
            response = requests.post(f"{self.api_url}/news/search", json=payload, timeout=30)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                articles = data.get('articles', [])
                details += f", Found {len(articles)} articles"
                
                # Verify article structure
                if articles:
                    article = articles[0]
                    required_fields = ['id', 'title', 'link', 'published', 'summary', 'source', 'sentiment', 'keyword']
                    missing_fields = [field for field in required_fields if field not in article]
                    
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
                    else:
                        # Verify sentiment values
                        sentiments = [a.get('sentiment') for a in articles]
                        valid_sentiments = all(s in ['positive', 'negative', 'neutral'] for s in sentiments)
                        if not valid_sentiments:
                            success = False
                            details += f", Invalid sentiments found: {set(sentiments)}"
                        else:
                            sentiment_counts = {s: sentiments.count(s) for s in set(sentiments)}
                            details += f", Sentiments: {sentiment_counts}"
                
                # Store sample article for watchlist testing
                if articles:
                    self.sample_article = articles[0]
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(f"News Search ({keyword})", success, details)
            return success
        except Exception as e:
            self.log_test(f"News Search ({keyword})", False, str(e))
            return False

    def test_sentiment_analysis(self):
        """Test individual sentiment analysis"""
        try:
            test_headlines = [
                "Apple reports record quarterly profits",
                "Tesla stock crashes amid production concerns", 
                "Microsoft announces new product update"
            ]
            
            all_success = True
            details_list = []
            
            for headline in test_headlines:
                payload = {"headline": headline}
                response = requests.post(f"{self.api_url}/news/analyze-sentiment", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    sentiment = data.get('sentiment')
                    if sentiment in ['positive', 'negative', 'neutral']:
                        details_list.append(f"'{headline[:30]}...' -> {sentiment}")
                    else:
                        all_success = False
                        details_list.append(f"Invalid sentiment: {sentiment}")
                else:
                    all_success = False
                    details_list.append(f"Failed for: {headline[:30]}...")
            
            details = "; ".join(details_list)
            self.log_test("Sentiment Analysis", all_success, details)
            return all_success
        except Exception as e:
            self.log_test("Sentiment Analysis", False, str(e))
            return False

    def test_watchlist_save(self):
        """Test saving article to watchlist"""
        if not hasattr(self, 'sample_article'):
            self.log_test("Watchlist Save", False, "No sample article available")
            return False
        
        try:
            # Prepare article data for saving
            article_data = {
                "title": self.sample_article['title'],
                "link": self.sample_article['link'],
                "published": self.sample_article['published'],
                "summary": self.sample_article['summary'],
                "source": self.sample_article['source'],
                "sentiment": self.sample_article['sentiment'],
                "keyword": self.sample_article['keyword']
            }
            
            response = requests.post(f"{self.api_url}/watchlist/save", json=article_data, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.saved_article_id = data.get('id')
                details += f", Saved with ID: {self.saved_article_id}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Watchlist Save", success, details)
            return success
        except Exception as e:
            self.log_test("Watchlist Save", False, str(e))
            return False

    def test_watchlist_get(self):
        """Test getting watchlist"""
        try:
            response = requests.get(f"{self.api_url}/watchlist", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Found {len(data)} saved articles"
                
                # Verify structure
                if data:
                    article = data[0]
                    required_fields = ['id', 'title', 'link', 'published', 'summary', 'source', 'sentiment', 'keyword', 'saved_at']
                    missing_fields = [field for field in required_fields if field not in article]
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Watchlist Get", success, details)
            return success
        except Exception as e:
            self.log_test("Watchlist Get", False, str(e))
            return False

    def test_watchlist_delete(self):
        """Test deleting from watchlist"""
        if not hasattr(self, 'saved_article_id'):
            self.log_test("Watchlist Delete", False, "No saved article ID available")
            return False
        
        try:
            response = requests.delete(f"{self.api_url}/watchlist/{self.saved_article_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Response: {data}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Watchlist Delete", success, details)
            return success
        except Exception as e:
            self.log_test("Watchlist Delete", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("Starting BrandPulse API Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API connectivity
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Test news search (this is the core functionality)
        print("\nTesting News Search...")
        self.test_news_search("Tesla")
        self.test_news_search("Apple")
        
        # Test sentiment analysis
        print("\nTesting Sentiment Analysis...")
        self.test_sentiment_analysis()
        
        # Test watchlist operations
        print("\nTesting Watchlist Operations...")
        self.test_watchlist_save()
        self.test_watchlist_get()
        self.test_watchlist_delete()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("All tests passed!")
            return True
        else:
            print("Some tests failed. Check details above.")
            return False

def main():
    tester = BrandPulseAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": f"{(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%",
        "test_details": tester.test_results
    }
    
    # Save results next to this script instead of a container-specific path
    results_path = 'backend_test_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_path}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())