"""
Schema-Guided Reasoning (SGR) schemas for LinkedIn Activity Agent.

This implements a 5-step reasoning process enforced by Pydantic models
for analyzing LinkedIn profiles and generating engagement content.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# LinkedIn Data Schemas
# ============================================================================

class LinkedInPost(BaseModel):
    """Individual LinkedIn post data."""
    post_id: str = Field(description="Unique identifier for the post")
    author_name: str = Field(description="Name of the post author")
    author_headline: str = Field(description="Author's LinkedIn headline")
    content: str = Field(description="Post content/text")
    post_type: Literal["text", "image", "video", "article", "poll", "document"] = Field(
        description="Type of the post"
    )
    likes_count: int = Field(default=0, description="Number of likes/reactions")
    comments_count: int = Field(default=0, description="Number of comments")
    shares_count: int = Field(default=0, description="Number of shares")
    posted_at: str = Field(description="When the post was published")
    engagement_rate: float = Field(default=0.0, description="Engagement rate percentage")


class LinkedInProfile(BaseModel):
    """LinkedIn profile information."""
    profile_url: str = Field(description="LinkedIn profile URL")
    name: str = Field(description="Full name")
    headline: str = Field(description="Professional headline")
    location: str = Field(default="", description="Location")
    industry: str = Field(default="", description="Industry")
    connections_count: int = Field(default=0, description="Number of connections")
    followers_count: int = Field(default=0, description="Number of followers")
    about: str = Field(default="", description="About/summary section")
    current_position: str = Field(default="", description="Current job title and company")
    skills: List[str] = Field(default=[], description="Listed skills")


class EngagementOpportunity(BaseModel):
    """An opportunity for engagement on LinkedIn."""
    post: LinkedInPost = Field(description="The post to engage with")
    relevance_score: float = Field(description="Relevance score 0-1 for engagement priority")
    suggested_action: Literal["like", "comment", "share", "connect", "skip"] = Field(
        description="Suggested engagement action"
    )
    reasoning: str = Field(description="Why this engagement is recommended")


class GeneratedComment(BaseModel):
    """A generated comment for a LinkedIn post."""
    post_id: str = Field(description="ID of the post to comment on")
    comment_text: str = Field(description="The generated comment text")
    tone: Literal["professional", "friendly", "insightful", "supportive", "curious"] = Field(
        description="Tone of the comment"
    )
    personalization_elements: List[str] = Field(
        description="Elements used to personalize the comment"
    )


class GeneratedPost(BaseModel):
    """A generated LinkedIn post."""
    content: str = Field(description="The post content")
    post_type: Literal["text", "image", "video", "article", "poll"] = Field(
        description="Recommended post type"
    )
    hashtags: List[str] = Field(description="Suggested hashtags")
    best_posting_time: str = Field(description="Recommended time to post")
    target_audience: str = Field(description="Target audience description")
    estimated_reach: str = Field(description="Estimated reach/engagement")


# ============================================================================
# 5-Step SGR Schema for LinkedIn Activity Analysis
# ============================================================================

class Step1RequestParsing(BaseModel):
    """STEP 1: Request Parsing"""
    user_query: str = Field(description="The original user request")
    activity_type: Literal[
        "analyze_feed", 
        "generate_post", 
        "generate_comments",
        "find_engagement_opportunities",
        "analyze_profile",
        "content_strategy"
    ] = Field(description="Type of LinkedIn activity requested")
    target_profile: Optional[str] = Field(
        default=None, 
        description="Target LinkedIn profile URL if specified"
    )
    content_topics: List[str] = Field(
        default=[], 
        description="Topics of interest extracted from the query"
    )
    tone_preference: Literal["professional", "casual", "thought_leader", "educational", "inspirational"] = Field(
        default="professional",
        description="Preferred tone for generated content"
    )
    parsing_reasoning: str = Field(
        description="Explain how you interpreted the user's request"
    )


class Step2DataGathering(BaseModel):
    """STEP 2: Data Gathering"""
    tools_used: List[str] = Field(
        description="List of tools used (e.g., ['fetch_linkedin_feed', 'analyze_profile'])"
    )
    profiles_analyzed: List[LinkedInProfile] = Field(
        default=[],
        description="LinkedIn profiles that were analyzed"
    )
    posts_collected: List[LinkedInPost] = Field(
        default=[],
        description="LinkedIn posts collected for analysis"
    )
    data_gathering_notes: str = Field(
        description="Notes about data collection: sources, quality, any limitations"
    )


class Step3AnalysisAndInsights(BaseModel):
    """STEP 3: Analysis and Insights"""
    engagement_patterns: dict = Field(
        description="Patterns in engagement (best times, content types, etc.)"
    )
    trending_topics: List[str] = Field(
        description="Trending topics in the user's network/industry"
    )
    top_performing_content: List[str] = Field(
        description="Types of content performing well"
    )
    engagement_opportunities: List[EngagementOpportunity] = Field(
        default=[],
        description="Identified opportunities for engagement"
    )
    analysis_summary: str = Field(
        description="Summary of the analysis findings"
    )


class Step4ContentGeneration(BaseModel):
    """STEP 4: Content Generation"""
    generated_posts: List[GeneratedPost] = Field(
        default=[],
        description="Generated LinkedIn posts"
    )
    generated_comments: List[GeneratedComment] = Field(
        default=[],
        description="Generated comments for engagement"
    )
    content_calendar: List[dict] = Field(
        default=[],
        description="Suggested content calendar with topics and timing"
    )
    generation_approach: str = Field(
        description="Explanation of the content generation approach"
    )


class Step5RecommendationsAndActions(BaseModel):
    """STEP 5: Recommendations and Action Items"""
    immediate_actions: List[str] = Field(
        description="Actions to take immediately (e.g., posts to engage with now)"
    )
    content_recommendations: List[str] = Field(
        description="Recommendations for content strategy"
    )
    engagement_strategy: str = Field(
        description="Overall engagement strategy recommendation"
    )
    metrics_to_track: List[str] = Field(
        description="Key metrics to monitor"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the recommendations"
    )
    limitations: List[str] = Field(
        description="Limitations and caveats of the analysis"
    )
    summary: str = Field(
        description="Executive summary of recommendations"
    )


class LinkedInActivityResponse(BaseModel):
    """Complete 5-step Schema-Guided Reasoning response for LinkedIn activity."""
    step1_request_parsing: Step1RequestParsing = Field(
        description="STEP 1 (MANDATORY): Parse user request to understand the activity type and requirements."
    )
    step2_data_gathering: Step2DataGathering = Field(
        description="STEP 2 (MANDATORY): Gather relevant LinkedIn data using available tools."
    )
    step3_analysis_and_insights: Step3AnalysisAndInsights = Field(
        description="STEP 3 (MANDATORY): Analyze collected data for patterns and insights."
    )
    step4_content_generation: Step4ContentGeneration = Field(
        description="STEP 4 (MANDATORY): Generate relevant content based on analysis."
    )
    step5_recommendations: Step5RecommendationsAndActions = Field(
        description="STEP 5 (MANDATORY): Provide actionable recommendations and strategy."
    )
