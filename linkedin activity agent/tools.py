"""
LinkedIn activity tools for the LinkedIn Activity Agent.
Provides tools for fetching feed data, analyzing profiles, and engagement actions.

Note: This implementation uses mock data by default. For production use,
integrate with LinkedIn's official API or a third-party service.
"""
import os
import json
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import random


# ============================================================================
# Input Schemas for Tools
# ============================================================================

class FetchFeedInput(BaseModel):
    """Input schema for fetching LinkedIn feed."""
    profile_url: Optional[str] = Field(
        None,
        description="LinkedIn profile URL to fetch feed for (optional)"
    )
    topics: List[str] = Field(
        default=[],
        description="Topics to filter feed by"
    )
    limit: int = Field(
        default=20,
        description="Maximum number of posts to fetch"
    )


class AnalyzeProfileInput(BaseModel):
    """Input schema for analyzing a LinkedIn profile."""
    profile_url: str = Field(
        description="LinkedIn profile URL to analyze"
    )


class GeneratePostInput(BaseModel):
    """Input schema for generating a LinkedIn post."""
    topic: str = Field(
        description="Topic or theme for the post"
    )
    tone: str = Field(
        default="professional",
        description="Tone of the post: professional, casual, thought_leader, educational, inspirational"
    )
    include_hashtags: bool = Field(
        default=True,
        description="Whether to include hashtags"
    )
    max_length: int = Field(
        default=3000,
        description="Maximum character length for the post"
    )


class GenerateCommentInput(BaseModel):
    """Input schema for generating a comment."""
    post_content: str = Field(
        description="Content of the post to comment on"
    )
    author_name: str = Field(
        description="Name of the post author"
    )
    tone: str = Field(
        default="professional",
        description="Tone of the comment"
    )
    intent: str = Field(
        default="engage",
        description="Intent: engage, agree, disagree, question, support"
    )


class SearchPostsInput(BaseModel):
    """Input schema for searching LinkedIn posts."""
    keywords: List[str] = Field(
        description="Keywords to search for"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry to filter by"
    )
    timeframe: str = Field(
        default="week",
        description="Timeframe: day, week, month"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results"
    )


# ============================================================================
# LinkedIn API Service (Mock Implementation)
# ============================================================================

class LinkedInService:
    """
    Service for interacting with LinkedIn.
    
    Note: This is a mock implementation. For production use, integrate with:
    - LinkedIn Marketing API (for company pages)
    - LinkedIn API with OAuth 2.0 (for personal profiles)
    - Third-party services like Proxycurl, PhantomBuster, or RapidAPI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LINKEDIN_API_KEY")
        self.base_url = "https://api.linkedin.com/v2"
        
    def _generate_mock_post(self, index: int, topics: List[str] = None) -> Dict[str, Any]:
        """Generate a mock LinkedIn post for testing."""
        authors = [
            ("Sarah Chen", "VP of Engineering at TechCorp | AI Enthusiast"),
            ("Marcus Johnson", "Founder & CEO | Building the future of work"),
            ("Elena Rodriguez", "Product Manager | Ex-Google, Ex-Meta"),
            ("David Kim", "Software Engineer | Open Source Contributor"),
            ("Rachel Thompson", "Data Scientist | Machine Learning Expert"),
            ("James Wilson", "Startup Advisor | Angel Investor"),
            ("Priya Sharma", "HR Director | People Operations Leader"),
            ("Michael Brown", "Sales Executive | Revenue Growth Specialist"),
        ]
        
        post_types = ["text", "image", "article", "video", "poll"]
        
        sample_posts = [
            "Just wrapped up an amazing quarter! Our team delivered 3 major product launches and grew revenue by 40%. Here's what I learned about leading high-performing teams...",
            "Unpopular opinion: The best code is the code you don't write. Before adding features, ask yourself if you can solve the problem with existing solutions.",
            "Excited to announce that I'm starting a new role as VP of Engineering! Thank you to everyone who supported me on this journey.",
            "5 things I wish I knew before starting my entrepreneurship journey:\n\n1. Cash flow is king\n2. Hire slow, fire fast\n3. Your network is your net worth\n4. Embrace failure as learning\n5. Take care of your mental health",
            "AI won't replace you. A person using AI will. Here's how to stay ahead of the curve...",
            "We're hiring! Looking for passionate engineers who want to work on cutting-edge technology. DM me if interested!",
            "Just finished reading 'The Lean Startup' - highly recommend for anyone building products. Key takeaway: Build, Measure, Learn.",
            "Remote work isn't going away. Companies that don't adapt will lose top talent. What's your take?",
        ]
        
        author = authors[index % len(authors)]
        content = sample_posts[index % len(sample_posts)]
        
        if topics:
            content = f"{content}\n\n#{' #'.join(topics[:3])}"
        
        days_ago = random.randint(0, 14)
        posted_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        likes = random.randint(10, 5000)
        comments = random.randint(5, 200)
        shares = random.randint(0, 100)
        
        return {
            "post_id": f"post_{index}_{random.randint(1000, 9999)}",
            "author_name": author[0],
            "author_headline": author[1],
            "content": content,
            "post_type": random.choice(post_types),
            "likes_count": likes,
            "comments_count": comments,
            "shares_count": shares,
            "posted_at": posted_at,
            "engagement_rate": round((likes + comments * 2 + shares * 3) / random.randint(1000, 10000) * 100, 2)
        }
    
    def _generate_mock_profile(self, profile_url: str) -> Dict[str, Any]:
        """Generate a mock LinkedIn profile for testing."""
        profiles = {
            "tech_leader": {
                "name": "Alex Morgan",
                "headline": "CTO at InnovateTech | Building scalable systems | Speaker & Mentor",
                "location": "San Francisco Bay Area",
                "industry": "Technology",
                "connections_count": 5000,
                "followers_count": 12500,
                "about": "Passionate technologist with 15+ years of experience building products used by millions. I write about engineering leadership, system design, and career growth.",
                "current_position": "CTO at InnovateTech",
                "skills": ["Leadership", "System Design", "Python", "Cloud Architecture", "Team Building"]
            },
            "entrepreneur": {
                "name": "Jordan Lee",
                "headline": "Serial Entrepreneur | 3x Founder | Helping startups scale",
                "location": "New York City",
                "industry": "Entrepreneurship",
                "connections_count": 8000,
                "followers_count": 25000,
                "about": "Built and sold 2 companies. Now helping early-stage founders navigate the startup journey. Angel investor in 20+ companies.",
                "current_position": "Founder & CEO at StartupAccelerator",
                "skills": ["Entrepreneurship", "Fundraising", "Business Strategy", "Mentoring", "Networking"]
            }
        }
        
        profile_type = "entrepreneur" if "entrepreneur" in profile_url.lower() else "tech_leader"
        profile = profiles[profile_type].copy()
        profile["profile_url"] = profile_url
        
        return profile
    
    def fetch_feed(self, profile_url: Optional[str] = None, topics: List[str] = None, limit: int = 20) -> List[Dict]:
        """Fetch LinkedIn feed posts."""
        posts = []
        for i in range(min(limit, 20)):
            posts.append(self._generate_mock_post(i, topics))
        return posts
    
    def analyze_profile(self, profile_url: str) -> Dict[str, Any]:
        """Analyze a LinkedIn profile."""
        return self._generate_mock_profile(profile_url)
    
    def search_posts(self, keywords: List[str], industry: Optional[str] = None, 
                     timeframe: str = "week", limit: int = 10) -> List[Dict]:
        """Search for LinkedIn posts by keywords."""
        posts = []
        for i in range(min(limit, 10)):
            post = self._generate_mock_post(i, keywords)
            posts.append(post)
        return posts


# ============================================================================
# LangChain Tools
# ============================================================================

class FetchLinkedInFeedTool(BaseTool):
    """Tool for fetching LinkedIn feed posts."""
    
    name: str = "fetch_linkedin_feed"
    description: str = """Fetch posts from LinkedIn feed.
    
    Use this to get recent posts from the user's network or a specific profile.
    Returns post content, engagement metrics, and author information.
    
    Parameters:
    - profile_url (optional): Specific profile to get posts from
    - topics: List of topics to filter by
    - limit: Maximum number of posts to fetch (default: 20)
    """
    
    args_schema: type[BaseModel] = FetchFeedInput
    
    def __init__(self):
        super().__init__()
        self._linkedin = LinkedInService()
    
    def _run(
        self,
        profile_url: Optional[str] = None,
        topics: List[str] = None,
        limit: int = 20
    ) -> str:
        """Execute the tool."""
        try:
            posts = self._linkedin.fetch_feed(profile_url, topics or [], limit)
            return json.dumps({
                "success": True,
                "posts_count": len(posts),
                "posts": posts
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class AnalyzeLinkedInProfileTool(BaseTool):
    """Tool for analyzing a LinkedIn profile."""
    
    name: str = "analyze_linkedin_profile"
    description: str = """Analyze a LinkedIn profile to understand their content strategy and engagement patterns.
    
    Returns profile information, posting patterns, and content themes.
    
    Parameters:
    - profile_url: The LinkedIn profile URL to analyze
    """
    
    args_schema: type[BaseModel] = AnalyzeProfileInput
    
    def __init__(self):
        super().__init__()
        self._linkedin = LinkedInService()
    
    def _run(self, profile_url: str) -> str:
        """Execute the tool."""
        try:
            profile = self._linkedin.analyze_profile(profile_url)
            
            recent_posts = self._linkedin.fetch_feed(profile_url, limit=5)
            avg_engagement = sum(p["engagement_rate"] for p in recent_posts) / len(recent_posts) if recent_posts else 0
            
            return json.dumps({
                "success": True,
                "profile": profile,
                "engagement_analysis": {
                    "average_engagement_rate": round(avg_engagement, 2),
                    "recent_posts_count": len(recent_posts),
                    "most_common_post_type": "text",
                    "posting_frequency": "2-3 times per week"
                }
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class GenerateLinkedInPostTool(BaseTool):
    """Tool for generating LinkedIn post content."""
    
    name: str = "generate_linkedin_post"
    description: str = """Generate a LinkedIn post based on a topic and tone.
    
    Creates engaging content optimized for LinkedIn's algorithm.
    
    Parameters:
    - topic: The main topic or theme for the post
    - tone: Tone of the post (professional, casual, thought_leader, educational, inspirational)
    - include_hashtags: Whether to add relevant hashtags
    - max_length: Maximum character length
    """
    
    args_schema: type[BaseModel] = GeneratePostInput
    
    def _run(
        self,
        topic: str,
        tone: str = "professional",
        include_hashtags: bool = True,
        max_length: int = 3000
    ) -> str:
        """Execute the tool."""
        try:
            tone_templates = {
                "professional": f"I've been reflecting on {topic} lately, and here are my key insights:\n\n1. [Key point 1]\n2. [Key point 2]\n3. [Key point 3]\n\nWhat's your experience with this? I'd love to hear your thoughts.",
                "casual": f"Can we talk about {topic} for a second? 🤔\n\nI've noticed something interesting...\n\n[Share observation]\n\nAnyone else experiencing this?",
                "thought_leader": f"Hot take on {topic}:\n\nThe conventional wisdom is wrong. Here's why...\n\n[Challenge assumption]\n\n[Provide evidence]\n\n[New perspective]\n\nAgree or disagree? Let's discuss.",
                "educational": f"Want to learn about {topic}? Here's a quick guide:\n\n📌 What it is\n📌 Why it matters\n📌 How to get started\n📌 Common mistakes to avoid\n\nSave this post for later! ✅",
                "inspirational": f"My journey with {topic} taught me something valuable:\n\n[Personal story]\n\n[Challenge faced]\n\n[Lesson learned]\n\nRemember: [Inspirational message]"
            }
            
            post_content = tone_templates.get(tone, tone_templates["professional"])
            
            hashtags = []
            if include_hashtags:
                base_hashtags = ["#" + word.replace(" ", "") for word in topic.split()[:2]]
                common_hashtags = ["#LinkedInTips", "#CareerGrowth", "#ProfessionalDevelopment"]
                hashtags = base_hashtags + common_hashtags[:2]
            
            return json.dumps({
                "success": True,
                "generated_post": {
                    "content": post_content,
                    "suggested_hashtags": hashtags,
                    "tone": tone,
                    "topic": topic,
                    "estimated_read_time": "30 seconds",
                    "best_posting_times": ["Tuesday 10am", "Wednesday 12pm", "Thursday 9am"],
                    "tips": [
                        "Add a hook in the first line",
                        "Use line breaks for readability",
                        "End with a question to encourage engagement",
                        "Consider adding an image or video"
                    ]
                }
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class GenerateCommentTool(BaseTool):
    """Tool for generating comments for LinkedIn posts."""
    
    name: str = "generate_linkedin_comment"
    description: str = """Generate a thoughtful comment for a LinkedIn post.
    
    Creates personalized, engaging comments that add value to the conversation.
    
    Parameters:
    - post_content: The content of the post to comment on
    - author_name: Name of the post author
    - tone: Desired tone of the comment
    - intent: Purpose of the comment (engage, agree, disagree, question, support)
    """
    
    args_schema: type[BaseModel] = GenerateCommentInput
    
    def _run(
        self,
        post_content: str,
        author_name: str,
        tone: str = "professional",
        intent: str = "engage"
    ) -> str:
        """Execute the tool."""
        try:
            intent_templates = {
                "engage": f"Great insights, {author_name}! This resonates with my experience. [Specific point from post] is particularly important because [add value]. What do you think about [related question]?",
                "agree": f"Couldn't agree more, {author_name}! [Point from post] is spot on. In my experience, [supporting evidence]. Thanks for sharing this perspective!",
                "disagree": f"Interesting perspective, {author_name}. While I see your point about [topic], I've found that [alternative view]. Would love to discuss this further - what led you to this conclusion?",
                "question": f"Thanks for sharing this, {author_name}! I'm curious about [specific aspect]. How do you handle [related scenario]? I'd love to learn from your experience.",
                "support": f"This is so valuable, {author_name}! 🙌 [Specific point] is exactly what I needed to hear today. Sharing this with my network!"
            }
            
            comment = intent_templates.get(intent, intent_templates["engage"])
            
            return json.dumps({
                "success": True,
                "generated_comment": {
                    "text": comment,
                    "tone": tone,
                    "intent": intent,
                    "personalization_tips": [
                        f"Reference specific points from {author_name}'s post",
                        "Add your own experience or insight",
                        "Ask a follow-up question if appropriate",
                        "Keep it concise but substantive"
                    ]
                }
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class SearchLinkedInPostsTool(BaseTool):
    """Tool for searching LinkedIn posts by keywords."""
    
    name: str = "search_linkedin_posts"
    description: str = """Search for LinkedIn posts by keywords and filters.
    
    Find relevant posts for engagement opportunities.
    
    Parameters:
    - keywords: List of keywords to search for
    - industry: Industry to filter by (optional)
    - timeframe: Time period (day, week, month)
    - limit: Maximum number of results
    """
    
    args_schema: type[BaseModel] = SearchPostsInput
    
    def __init__(self):
        super().__init__()
        self._linkedin = LinkedInService()
    
    def _run(
        self,
        keywords: List[str],
        industry: Optional[str] = None,
        timeframe: str = "week",
        limit: int = 10
    ) -> str:
        """Execute the tool."""
        try:
            posts = self._linkedin.search_posts(keywords, industry, timeframe, limit)
            
            return json.dumps({
                "success": True,
                "search_params": {
                    "keywords": keywords,
                    "industry": industry,
                    "timeframe": timeframe
                },
                "results_count": len(posts),
                "posts": posts
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


# ============================================================================
# Export all tools
# ============================================================================

def get_all_tools() -> List[BaseTool]:
    """Get all LinkedIn activity tools."""
    return [
        FetchLinkedInFeedTool(),
        AnalyzeLinkedInProfileTool(),
        GenerateLinkedInPostTool(),
        GenerateCommentTool(),
        SearchLinkedInPostsTool()
    ]
