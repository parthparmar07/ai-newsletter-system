from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Article:
    """Represents a news article"""
    title: str
    url: str
    summary: str
    source: str
    published_date: datetime
    content: Optional[str] = None
    ai_summary: Optional[str] = None
    importance_score: Optional[float] = None
    
@dataclass
class Newsletter:
    """Represents a newsletter edition"""
    date: datetime
    articles: List[Article]
    intro: str
    outro: str
    subject: str
