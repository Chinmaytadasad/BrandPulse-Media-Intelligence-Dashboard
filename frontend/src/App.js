import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Search, BookmarkPlus, BookmarkCheck, TrendingUp, X, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Toaster, toast } from 'sonner';
import '@/App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NotificationToast = ({ title, message, type = 'success', onDismiss }) => {
  const icons = {
    success: <CheckCircle2 className="toast-icon" />,
    error: <AlertCircle className="toast-icon" />,
    info: <Info className="toast-icon" />
  };

  return (
    <div className={`custom-toast ${type}`}>
      <div className="toast-icon-container">
        {icons[type]}
      </div>
      <div className="toast-content">
        <div className="toast-title">{title}</div>
        <div className="toast-message">{message}</div>
      </div>
      <button onClick={onDismiss} className="toast-close">
        <X size={16} />
      </button>
    </div>
  );
};

const Dashboard = () => {
  const [keyword, setKeyword] = useState('');
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [savedIds, setSavedIds] = useState(new Set());
  const [stats, setStats] = useState({ positive: 0, negative: 0, neutral: 0 });

  const searchNews = async () => {
    if (!keyword.trim()) {
      toast.custom((t) => (
        <NotificationToast
          title="Search Error"
          message="Please enter a company or keyword to start tracking."
          type="error"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/news/search`, { keyword });
      setArticles(response.data.articles || []);
      calculateStats(response.data.articles || []);

      if (response.data.articles?.length === 0) {
        toast.custom((t) => (
          <NotificationToast
            title="No Results Found"
            message={`We couldn't find any recent news for "${keyword}".`}
            type="info"
            onDismiss={() => toast.dismiss(t)}
          />
        ));
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      toast.custom((t) => (
        <NotificationToast
          title="Connection Error"
          message="Failed to fetch news. Please check your connection and try again."
          type="error"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (articlesList) => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    articlesList.forEach(article => {
      counts[article.sentiment] = (counts[article.sentiment] || 0) + 1;
    });
    setStats(counts);
  };

  const saveArticle = async (article) => {
    try {
      await axios.post(`${API}/watchlist/save`, article);
      setSavedIds(new Set([...savedIds, article.id]));
      toast.custom((t) => (
        <NotificationToast
          title="Article Saved"
          message="This article has been successfully added to your watchlist."
          type="success"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    } catch (error) {
      console.error('Error saving article:', error);
      toast.custom((t) => (
        <NotificationToast
          title="Save Failed"
          message="We couldn't save this article. Please try again."
          type="error"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchNews();
    }
  };

  return (
    <div className="dashboard-container">
      <div className="search-section">
        <div className="search-header">
          <h1 data-testid="dashboard-title">Media Intelligence</h1>
          <p data-testid="dashboard-subtitle">Track brand sentiment across global news sources</p>
        </div>

        <div className="search-bar" data-testid="search-container">
          <Search className="search-icon" />
          <Input
            data-testid="search-input"
            type="text"
            placeholder="Search company or brand (e.g., Tesla, Apple, Microsoft)"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyPress={handleKeyPress}
            className="search-input-field"
          />
          <Button
            data-testid="search-button"
            onClick={searchNews}
            disabled={loading}
            className="search-button"
          >
            {loading ? 'Analyzing...' : 'Search'}
          </Button>
        </div>

        {articles.length > 0 && (
          <div className="stats-container" data-testid="sentiment-stats">
            <div className="stat-card positive">
              <div className="stat-value" data-testid="positive-count">{stats.positive}</div>
              <div className="stat-label">Positive</div>
            </div>
            <div className="stat-card negative">
              <div className="stat-value" data-testid="negative-count">{stats.negative}</div>
              <div className="stat-label">Negative</div>
            </div>
            <div className="stat-card neutral">
              <div className="stat-value" data-testid="neutral-count">{stats.neutral}</div>
              <div className="stat-label">Neutral</div>
            </div>
          </div>
        )}
      </div>

      <div className="articles-grid" data-testid="articles-grid">
        {articles.map((article, index) => (
          <Card key={article.id} className="article-card" data-testid={`article-card-${index}`}>
            <div className="article-header">
              <Badge
                className={`sentiment-badge ${article.sentiment}`}
                data-testid={`sentiment-badge-${index}`}
              >
                {article.sentiment.toUpperCase()}
              </Badge>
              <Button
                data-testid={`save-button-${index}`}
                variant="ghost"
                size="icon"
                onClick={() => saveArticle(article)}
                disabled={savedIds.has(article.id)}
                className="save-button"
              >
                {savedIds.has(article.id) ?
                  <BookmarkCheck className="icon-saved" /> :
                  <BookmarkPlus className="icon-unsaved" />
                }
              </Button>
            </div>

            <h3 className="article-title" data-testid={`article-title-${index}`}>
              {article.title}
            </h3>

            <div className="article-meta" data-testid={`article-meta-${index}`}>
              <span className="article-source">{article.source}</span>
              <span className="article-date">{new Date(article.published).toLocaleDateString()}</span>
            </div>

            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="read-more"
              data-testid={`read-more-${index}`}
            >
              Read Full Article →
            </a>
          </Card>
        ))}
      </div>

      {articles.length === 0 && !loading && (
        <div className="empty-state" data-testid="empty-state">
          <TrendingUp className="empty-icon" />
          <h3>Start Monitoring</h3>
          <p>Enter a company name to track media sentiment</p>
        </div>
      )}
    </div>
  );
};

const Watchlist = () => {
  const [savedArticles, setSavedArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const response = await axios.get(`${API}/watchlist`);
      setSavedArticles(response.data);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
      toast.custom((t) => (
        <NotificationToast
          title="Error Loading Watchlist"
          message="We couldn't load your saved articles. Please refresh the page."
          type="error"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    } finally {
      setLoading(false);
    }
  };

  const removeArticle = async (articleId) => {
    try {
      await axios.delete(`${API}/watchlist/${articleId}`);
      setSavedArticles(savedArticles.filter(a => a.id !== articleId));
      toast.custom((t) => (
        <NotificationToast
          title="Article Removed"
          message="The article has been removed from your watchlist."
          type="info"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    } catch (error) {
      console.error('Error removing article:', error);
      toast.custom((t) => (
        <NotificationToast
          title="Removal Failed"
          message="We couldn't remove this article. Please try again."
          type="error"
          onDismiss={() => toast.dismiss(t)}
        />
      ));
    }
  };

  return (
    <div className="watchlist-container" data-testid="watchlist-page">
      <div className="watchlist-header">
        <h1 data-testid="watchlist-title">My Watchlist</h1>
        <p data-testid="watchlist-count">{savedArticles.length} saved articles</p>
      </div>

      {loading ? (
        <div className="loading-state">Loading...</div>
      ) : savedArticles.length === 0 ? (
        <div className="empty-state" data-testid="watchlist-empty">
          <BookmarkPlus className="empty-icon" />
          <h3>No Saved Articles</h3>
          <p>Articles you save will appear here</p>
          <Link to="/">
            <Button className="cta-button" data-testid="go-to-dashboard-button">Go to Dashboard</Button>
          </Link>
        </div>
      ) : (
        <div className="articles-grid" data-testid="watchlist-articles">
          {savedArticles.map((article, index) => (
            <Card key={article.id} className="article-card" data-testid={`watchlist-article-${index}`}>
              <div className="article-header">
                <Badge className={`sentiment-badge ${article.sentiment}`} data-testid={`watchlist-sentiment-${index}`}>
                  {article.sentiment.toUpperCase()}
                </Badge>
                <Button
                  data-testid={`remove-button-${index}`}
                  variant="ghost"
                  size="icon"
                  onClick={() => removeArticle(article.id)}
                  className="remove-button"
                >
                  <X className="icon-remove" />
                </Button>
              </div>

              <h3 className="article-title" data-testid={`watchlist-article-title-${index}`}>
                {article.title}
              </h3>

              <div className="article-meta">
                <span className="article-source">{article.source}</span>
                <span className="article-keyword">#{article.keyword}</span>
              </div>

              <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                className="read-more"
                data-testid={`watchlist-read-more-${index}`}
              >
                Read Full Article →
              </a>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="navbar" data-testid="navigation">
      <div className="nav-brand">
        <TrendingUp className="brand-icon" />
        <span className="brand-name">BrandPulse</span>
      </div>

      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''} data-testid="nav-dashboard">
          Dashboard
        </Link>
        <Link to="/watchlist" className={location.pathname === '/watchlist' ? 'active' : ''} data-testid="nav-watchlist">
          Watchlist
        </Link>
      </div>
    </nav>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/watchlist" element={<Watchlist />} />
          </Routes>
        </div>
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </div>
  );
}

export default App;