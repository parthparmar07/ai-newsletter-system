import feedparser
import tweepy
import requests
from newspaper import Article as NewspaperArticle
from datetime import datetime, timedelta
from typing import List
from loguru import logger
from models import Article
from config import Config

class ContentCollector:
    """Collects content from various sources"""
    
    def __init__(self):
        self.config = Config()
        self.twitter_client = self._setup_twitter_client()
    
    def _setup_twitter_client(self):
        """Setup Twitter API client"""
        if self.config.TWITTER_BEARER_TOKEN:
            return tweepy.Client(bearer_token=self.config.TWITTER_BEARER_TOKEN)
        return None
    
    def collect_rss_articles(self) -> List[Article]:
        """Collect articles from RSS feeds"""
        articles = []
        
        for feed_url in self.config.RSS_FEEDS:
            if not feed_url.strip():
                continue
                
            try:
                logger.info(f"Fetching RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:self.config.MAX_ARTICLES_PER_SOURCE]:
                    try:
                        # Parse publication date
                        pub_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        
                        # Extract content
                        content = ""
                        if hasattr(entry, 'summary'):
                            content = entry.summary
                        elif hasattr(entry, 'description'):
                            content = entry.description
                        
                        article = Article(
                            title=entry.title,
                            url=entry.link,
                            summary=content,
                            source=feed.feed.title if hasattr(feed.feed, 'title') else 'RSS Feed',
                            published_date=pub_date,
                            content=content
                        )
                        
                        articles.append(article)
                        logger.info(f"Collected article: {article.title}")
                        
                    except Exception as e:
                        logger.error(f"Error processing RSS entry: {e}")
                        
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return articles
    
    def collect_twitter_content(self) -> List[Article]:
        """Collect relevant tweets about AI"""
        articles = []
        
        if not self.twitter_client:
            logger.warning("Twitter client not configured")
            return articles
        
        try:
            for keyword in self.config.TWITTER_KEYWORDS:
                if not keyword.strip():
                    continue
                    
                logger.info(f"Searching Twitter for: {keyword}")
                
                # Search for recent tweets
                tweets = self.twitter_client.search_recent_tweets(
                    query=f"{keyword} -is:retweet lang:en",
                    max_results=10,
                    tweet_fields=['created_at', 'author_id', 'public_metrics']
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        # Only include tweets with significant engagement
                        if tweet.public_metrics['like_count'] > 10:
                            article = Article(
                                title=f"Twitter: {tweet.text[:100]}...",
                                url=f"https://twitter.com/i/web/status/{tweet.id}",
                                summary=tweet.text,
                                source="Twitter",
                                published_date=tweet.created_at,
                                content=tweet.text
                            )
                            articles.append(article)
                            
        except Exception as e:
            logger.error(f"Error collecting Twitter content: {e}")
        
        return articles
    
    def enhance_article_content(self, article: Article) -> Article:
        """Extract full article content using newspaper3k"""
        try:
            news_article = NewspaperArticle(article.url)
            news_article.download()
            news_article.parse()
            
            if news_article.text:
                article.content = news_article.text
                logger.info(f"Enhanced content for: {article.title}")
            
        except Exception as e:
            logger.error(f"Error enhancing article content: {e}")
        
        return article
    
    def collect_all_content(self) -> List[Article]:
        """Collect content from all sources"""
        logger.info("Starting content collection...")
        
        articles = []
        
        # Collect from RSS feeds
        rss_articles = self.collect_rss_articles()
        articles.extend(rss_articles)
        
        # Collect from Twitter
        twitter_articles = self.collect_twitter_content()
        articles.extend(twitter_articles)
        
        # Enhance articles with full content
        enhanced_articles = []
        for article in articles:
            enhanced_article = self.enhance_article_content(article)
            enhanced_articles.append(enhanced_article)
        
        # Filter articles from the last week
        week_ago = datetime.now() - timedelta(days=7)
        recent_articles = [a for a in enhanced_articles if a.published_date >= week_ago]
        
        logger.info(f"Collected {len(recent_articles)} recent articles")
        return recent_articles
