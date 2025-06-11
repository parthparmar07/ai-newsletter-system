import openai
import anthropic
from typing import List
from loguru import logger
from models import Article
from config import Config

class AIContentCurator:
    """Uses AI to curate and summarize content"""
    
    def __init__(self):
        self.config = Config()
        self.openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.anthropic_client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY) if self.config.ANTHROPIC_API_KEY else None
    
    def score_article_importance(self, article: Article) -> float:
        """Score article importance using AI"""
        try:
            prompt = f"""
            Rate the importance of this AI/tech article on a scale of 1-10, where:
            1-3: Minor news, incremental updates
            4-6: Moderate importance, interesting developments
            7-8: Significant news, major breakthroughs
            9-10: Groundbreaking, industry-changing news
            
            Article Title: {article.title}
            Source: {article.source}
            Summary: {article.summary[:500]}...
            
            Consider factors like:
            - Innovation level
            - Impact on industry
            - Credibility of source
            - Uniqueness of information
              Respond with only a number between 1-10.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.3
            )
            
            score = float(response.choices[0].message.content.strip())
            return max(1, min(10, score))  # Ensure score is between 1-10
            
        except Exception as e:
            logger.error(f"Error scoring article importance: {e}")
            return 5.0  # Default moderate score
    
    def generate_ai_summary(self, article: Article) -> str:
        """Generate AI summary of article"""
        try:
            content_to_summarize = article.content or article.summary
            
            if len(content_to_summarize) < 100:
                return content_to_summarize
            
            prompt = f"""
            Create a very brief summary of this tech/AI article in 1-2 sentences maximum.
            Be concise and punchy like Superhuman newsletter style. Focus on:
            - The key development (what happened)
            - Why it matters (impact)
            
            Article Title: {article.title}
            Content: {content_to_summarize[:2000]}...
            
            Write 1-2 sentences max:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return article.summary[:200] + "..."
    
    def curate_articles(self, articles: List[Article]) -> List[Article]:
        """Curate and enhance articles with AI"""
        logger.info("Starting AI curation process...")
        
        curated_articles = []
        
        # Filter to AI/tech relevant articles first by keywords in title
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning', 
                      'chatgpt', 'gpt', 'llm', 'openai', 'anthropic', 'google', 'meta', 'tech',
                      'startup', 'algorithm', 'automation', 'robot', 'quantum', 'cloud', 'data']
        
        relevant_articles = []
        for article in articles:
            title_lower = article.title.lower()
            if any(keyword in title_lower for keyword in ai_keywords):
                relevant_articles.append(article)
        
        # If we don't have enough relevant articles, include some general tech articles
        if len(relevant_articles) < 10:
            for article in articles:
                if article not in relevant_articles:
                    relevant_articles.append(article)
                if len(relevant_articles) >= 15:  # Limit to top 15 for processing
                    break
        
        for article in relevant_articles:
            try:
                # Score importance
                article.importance_score = self.score_article_importance(article)
                
                # Generate AI summary
                article.ai_summary = self.generate_ai_summary(article)
                
                curated_articles.append(article)
                logger.info(f"Curated article: {article.title} (Score: {article.importance_score})")                
            except Exception as e:
                logger.error(f"Error curating article {article.title}: {e}")
                # Still include the article with original summary and smart importance scoring
                article.importance_score = self._fallback_importance_score(article)
                article.ai_summary = self._fallback_summary(article)
                curated_articles.append(article)
        
        # Sort by importance score (highest first)
        curated_articles.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Always ensure we have exactly 5 articles for daily digest
        if len(curated_articles) >= 5:
            top_articles = curated_articles[:5]
        else:
            # If we have fewer than 5, duplicate the best ones to reach 5
            logger.warning(f"Only found {len(curated_articles)} articles. Duplicating best ones to reach 5.")
            top_articles = curated_articles.copy()
            while len(top_articles) < 5 and curated_articles:
                # Add the best articles again until we have 5
                for article in curated_articles:
                    if len(top_articles) < 5:
                        # Create a copy with slightly modified title to indicate it's a featured story
                        featured_article = Article(
                            title=f"🔥 Featured: {article.title}",
                            url=article.url,
                            summary=article.summary,
                            content=article.content,
                            source=article.source,
                            published_date=article.published_date,
                            importance_score=article.importance_score,
                            ai_summary=f"⭐ FEATURED STORY: {article.ai_summary}"
                        )
                        top_articles.append(featured_article)
                    else:
                        break
                break
        
        logger.info(f"Selected exactly {len(top_articles)} articles for daily newsletter")
        return top_articles
    
    def _fallback_importance_score(self, article: Article) -> float:
        """Generate importance score based on keywords and source when AI fails"""
        score = 5.0  # Base score
        
        title_lower = article.title.lower()
        source_lower = article.source.lower()
        
        # High importance keywords
        high_keywords = ['breakthrough', 'launches', 'announces', 'release', 'new', 'first', 'major', 'billion', 'funding']
        # AI/tech specific keywords  
        ai_keywords = ['openai', 'anthropic', 'google ai', 'meta ai', 'chatgpt', 'gpt-4', 'claude', 'ai model']
        # Source credibility
        premium_sources = ['techcrunch', 'wired', 'venturebeat', 'ai news', 'google', 'openai', 'anthropic']
        
        # Boost score for high-impact keywords
        for keyword in high_keywords:
            if keyword in title_lower:
                score += 1.0
        
        # Boost score for AI-specific content
        for keyword in ai_keywords:
            if keyword in title_lower:
                score += 1.5
        
        # Boost score for premium sources
        for source in premium_sources:
            if source in source_lower:
                score += 0.5
        
        return min(10.0, score)  # Cap at 10
    
    def _fallback_summary(self, article: Article) -> str:
        """Generate a concise summary when AI fails"""
        content = article.content or article.summary
        if not content:
            return f"Breaking development from {article.source}: {article.title}. This represents a key advancement in the tech sector."
        
        # Take first 1-2 sentences and clean them up
        sentences = content.split('.')[:2]
        summary = '. '.join(sentences).strip() + '.'
        
        # If too short, add brief context
        if len(summary) < 80:
            summary += f" Key development from {article.source}."
          # Ensure it's not too long
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return summary
    
    def generate_newsletter_intro(self, articles: List[Article]) -> str:
        """Generate an engaging newsletter introduction"""
        try:
            article_titles = "\n".join([f"- {article.title}" for article in articles[:3]])
            
            prompt = f"""
            Write a brief intro for a daily AI/tech newsletter. Requirements:
            - 1 sentence only
            - Professional, not overly excited
            - Say "today's" tech developments
            
            Today's top stories:
            {article_titles}
            
            Write 1 sentence:            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            
            intro = response.choices[0].message.content.strip()
            
            # Ensure the intro mentions "today" or "today's"
            if "today" not in intro.lower():
                intro = f"Today's AI digest: {intro}"
            
            return intro
            
        except Exception as e:
            logger.error(f"Error generating newsletter intro: {e}")
            return "Today's most important tech developments."    
    def generate_newsletter_outro(self) -> str:
        """Generate newsletter closing"""
        return "Thanks for reading! Reply with questions or feedback."
