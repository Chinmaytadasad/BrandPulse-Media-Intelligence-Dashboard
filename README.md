# BrandPulse - Media Intelligence Dashboard

BrandPulse is a full-stack media monitoring dashboard designed to simulate professional PR tools. It allows users to track news about specific brands or keywords in real-time and analyzes the sentiment of those articles to provide actionable insights.

## Features

*   **Live News Feed:** Real-time news tracking for any company or keyword (e.g., "Tesla", "Apple").
*   **AI Sentiment Analysis:** Automatically analyzes news headlines to determine sentiment (Positive, Negative, Neutral).
*   **Sentiment Badges:** Visual indicators for quick sentiment assessment:
    *   🟢 **Positive:** Growth, profit, success.
    *   🔴 **Negative:** Loss, crash, scandal.
    *   ⚪ **Neutral:** General reporting.
*   **Watchlist:** Save important articles to a personal watchlist for later review.
*   **Media Intelligence Stats:** Real-time breakdown of sentiment distribution (Positive vs. Negative vs. Neutral).
*   **Professional UI:** Dark-mode SaaS aesthetic with data-heavy visualization.

## Technology Stack

### Frontend
*   **React:** Modern UI library for building interactive user interfaces.
*   **Tailwind CSS:** Utility-first CSS framework for styling.
*   **Lucide React:** Icon library for consistent visual language.
*   **Axios:** For making HTTP requests to the backend.

### Backend
*   **FastAPI (Python):** High-performance web framework for building APIs.
*   **Motor:** Asynchronous Python driver for MongoDB.
*   **Feedparser:** Library for parsing RSS feeds.
*   **VaderSentiment:** Lexicon and rule-based sentiment analysis tool.

### Database
*   **MongoDB:** NoSQL database for storing watchlist articles.

## How It Works

### 1. News Fetching
BrandPulse uses **Google News RSS feeds** to fetch real-time articles without requiring complex API keys.
*   When a user searches for a keyword, the backend constructs a query URL: `https://news.google.com/rss/search?q={keyword}...`
*   The `feedparser` library parses the returned XML feed to extract article metadata (Title, Link, Summary, Source, Published Date).

### 2. Sentiment Analysis
Sentiment analysis is performed locally on the backend using the **VADER (Valence Aware Dictionary and sEntiment Reasoner)** library.
*   Each article headline is passed through the `SentimentIntensityAnalyzer`.
*   A **Compound Score** is calculated to determine the overall sentiment:
    *   **Positive:** Score ≥ 0.2
    *   **Negative:** Score ≤ -0.2
    *   **Neutral:** Score between -0.2 and 0.2

### 3. Data Persistence
*   Users can save interesting articles to their **Watchlist**.
*   Saved articles are stored in a **MongoDB** collection (`watchlist`), allowing for persistent access across sessions.

## Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.8+
*   MongoDB (running locally or via Atlas)

### Installation

1.  **Clone the repository**
2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn server:app --reload
    ```
3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm start
    ```

## License
This project is open-source and available for personal and educational use.