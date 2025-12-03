from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import feedparser
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (with safe defaults so the app can start without custom env)
mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
db_name = os.environ.get("DB_NAME", "brandpulse")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Sentiment analyzer (local, no external API)
sentiment_analyzer = SentimentIntensityAnalyzer()

# Models
class Article(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    link: str
    published: str
    summary: str
    source: str
    sentiment: str  # positive, negative, neutral
    keyword: str
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ArticleCreate(BaseModel):
    title: str
    link: str
    published: str
    summary: str
    source: str
    sentiment: str
    keyword: str

class NewsSearchRequest(BaseModel):
    keyword: str

class SentimentRequest(BaseModel):
    headline: str

# Utility Functions
async def analyze_sentiment(headline: str) -> str:
    """Analyze sentiment of a headline using VADER (local, no external API)."""
    try:
        scores = sentiment_analyzer.polarity_scores(headline or "")
        compound = scores.get("compound", 0.0)

        if compound >= 0.2:
            return "positive"
        if compound <= -0.2:
            return "negative"
        return "neutral"
    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}")
        return "neutral"

def fetch_google_news(keyword: str, limit: int = 20) -> List[dict]:
    """Fetch news from Google News RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        
        articles = []
        for entry in feed.entries[:limit]:
            articles.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'source': entry.get('source', {}).get('title', 'Google News')
            })
        
        return articles
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return []

# Routes
@api_router.get("/")
async def root():
    return {"message": "BrandPulse API"}

@api_router.post("/news/search")
async def search_news(request: NewsSearchRequest):
    """Search for news about a keyword and analyze sentiment"""
    try:
        articles = fetch_google_news(request.keyword)
        
        if not articles:
            return {"articles": [], "message": "No articles found"}
        
        # Analyze sentiment for each article
        analyzed_articles = []
        for article in articles:
            sentiment = await analyze_sentiment(article['title'])
            analyzed_articles.append({
                'id': str(uuid.uuid4()),
                'title': article['title'],
                'link': article['link'],
                'published': article['published'],
                'summary': article['summary'],
                'source': article['source'],
                'sentiment': sentiment,
                'keyword': request.keyword
            })
        
        return {"articles": analyzed_articles}
    except Exception as e:
        logging.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/news/analyze-sentiment")
async def analyze_headline_sentiment(request: SentimentRequest):
    """Analyze sentiment of a single headline"""
    try:
        sentiment = await analyze_sentiment(request.headline)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/watchlist/save", response_model=Article)
async def save_to_watchlist(article: ArticleCreate):
    """Save an article to watchlist"""
    try:
        article_obj = Article(**article.model_dump())
        doc = article_obj.model_dump()
        doc['saved_at'] = doc['saved_at'].isoformat()
        
        await db.watchlist.insert_one(doc)
        return article_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/watchlist", response_model=List[Article])
async def get_watchlist():
    """Get all saved articles"""
    try:
        articles = await db.watchlist.find({}, {"_id": 0}).to_list(1000)
        
        for article in articles:
            if isinstance(article['saved_at'], str):
                article['saved_at'] = datetime.fromisoformat(article['saved_at'])
        
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/watchlist/{article_id}")
async def delete_from_watchlist(article_id: str):
    """Delete an article from watchlist"""
    try:
        result = await db.watchlist.delete_one({"id": article_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {"message": "Article removed from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()