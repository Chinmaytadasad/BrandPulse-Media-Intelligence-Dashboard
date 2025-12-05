# BrandPulse - Media Intelligence Dashboard

BrandPulse is a full-stack media monitoring dashboard designed to simulate professional PR tools. It allows users to track news about specific brands or keywords in real-time and analyzes the sentiment of those articles to provide actionable insights.

## Features

* **Live News Feed:** Real-time news tracking for any company or keyword (e.g., "Tesla", "Apple").
* **AI Sentiment Analysis:** Automatically analyzes news headlines to determine sentiment (Positive, Negative, Neutral).
* **Sentiment Badges:** Visual indicators for quick sentiment assessment:
    * 🟢 **Positive:** Growth, profit, success.
    * 🔴 **Negative:** Loss, crash, scandal.
    * ⚪ **Neutral:** General reporting.
* **Watchlist:** Save important articles to a personal watchlist for later review (Persistent Database).
* **Media Intelligence Stats:** Real-time breakdown of sentiment distribution.
* **Professional UI:** Dark-mode SaaS aesthetic with data-heavy visualization.

## Technology Stack

### Frontend
* **React:** Modern UI library for interactive interfaces.
* **Tailwind CSS / Shadcn UI:** For styling and accessible components.
* **Lucide React:** Icon library.
* **Axios:** For API communication.

### Backend (FARM Stack)
* **FastAPI (Python):** High-performance web framework for the API.
* **Motor:** Asynchronous Python driver for MongoDB.
* **Feedparser:** Library for parsing Google News RSS feeds.
* **VaderSentiment:** Lexicon and rule-based sentiment analysis engine.

### Database
* **MongoDB:** NoSQL database for storing the watchlist.

## How It Works

### 1. News Fetching
BrandPulse uses **Google News RSS feeds** to fetch real-time articles.
* The backend constructs a dynamic query: `https://news.google.com/rss/search?q={keyword}...`
* `feedparser` extracts the Title, Link, and Summary from the XML feed.

### 2. Sentiment Analysis (VADER)
Analysis is performed locally on the Python backend.
* Each headline is passed through `SentimentIntensityAnalyzer`.
* A **Compound Score** (-1.0 to +1.0) determines the tag:
    * **Positive:** Score ≥ 0.2
    * **Negative:** Score ≤ -0.2
    * **Neutral:** Score between -0.2 and 0.2

### 3. Data Persistence
* Users can "Bookmark" articles.
* These are saved to a **MongoDB** collection (`watchlist`) for persistent access.

## Getting Started

### Prerequisites
* Node.js & npm
* Python 3.8+
* MongoDB (Locally running or Atlas URI)

### Installation & Setup

#### 1. Backend Setup (FastAPI)
```bash
cd backend
# Create a virtual environment (optional but recommended)
python -m venv venv
# Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac)

# Install dependencies
pip install -r requirements.txt

# Create a .env file in the backend folder
echo "MONGO_URL=mongodb://localhost:27017" > .env
echo "DB_NAME=brandpulse" >> .env
echo "CORS_ORIGINS=http://localhost:3000" >> .env

# Run the server
uvicorn server:app --reload
````
#### 2. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Create a .env file in the frontend folder
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env

# Start the application
npm start
```

#### License
This project is open-source and available for educational use.
