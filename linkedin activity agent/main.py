"""
LinkedIn Activity Agent - An AI-powered LinkedIn engagement and content creation assistant.

This agent uses Schema-Guided Reasoning (SGR) to analyze LinkedIn activity,
generate engaging content, and provide strategic recommendations for LinkedIn growth.
"""
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from tools import get_all_tools
from schemas import LinkedInActivityResponse
import os
import json
import re
from typing import Optional, Dict, List
from datetime import datetime


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


class LinkedInActivityAgent:
    """A LinkedIn activity agent using Schema-Guided Reasoning."""
    
    SYSTEM_PROMPT = """You are an expert LinkedIn engagement and content strategy assistant that helps professionals grow their presence on LinkedIn.

CRITICAL RULES:
1. Analyze user requests to understand their LinkedIn goals (posting, engagement, growth)
2. Use available tools to gather data about LinkedIn feeds, profiles, and engagement opportunities
3. Generate high-quality, authentic content that resonates with professional audiences
4. Provide actionable recommendations backed by data
5. Follow the 5-step Schema-Guided Reasoning process exactly:
   - STEP 1: Parse the request to understand the activity type and requirements
   - STEP 2: Gather relevant data using available tools
   - STEP 3: Analyze the data for patterns and insights
   - STEP 4: Generate appropriate content (posts, comments, strategies)
   - STEP 5: Provide actionable recommendations and next steps

CONTENT GUIDELINES:
- Keep posts authentic and value-driven
- Avoid clickbait or overly promotional content
- Focus on storytelling and genuine insights
- Encourage meaningful engagement, not vanity metrics
- Respect LinkedIn's professional context

AVAILABLE TOOLS:
- fetch_linkedin_feed: Get posts from LinkedIn feed
- analyze_linkedin_profile: Analyze a LinkedIn profile
- generate_linkedin_post: Create post content
- generate_linkedin_comment: Create thoughtful comments
- search_linkedin_posts: Find relevant posts for engagement

Always provide specific, actionable advice tailored to the user's goals."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
    ):
        """
        Initialize the LinkedIn activity agent.
        
        Args:
            model_name: The LLM model to use (default: "gpt-4")
            temperature: Temperature for the model (0.7 for creative content)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.tools = get_all_tools()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=10
        )
    
    def run(
        self,
        query: str,
        profile_url: Optional[str] = None,
        topics: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict:
        """
        Execute a LinkedIn activity request.
        
        Args:
            query: The user's question or request
            profile_url: Optional LinkedIn profile URL for context
            topics: Optional list of topics of interest
            verbose: Whether to print intermediate steps
            
        Returns:
            Dict containing the response and recommendations
        """
        if verbose:
            print(f"🔍 Processing LinkedIn Activity Request")
            print(f"Query: {query}")
            if profile_url:
                print(f"Profile: {profile_url}")
            if topics:
                print(f"Topics: {', '.join(topics)}")
            print("=" * 70)
        
        try:
            context_parts = []
            if profile_url:
                context_parts.append(f"My LinkedIn profile: {profile_url}")
            if topics:
                context_parts.append(f"Topics of interest: {', '.join(topics)}")
            
            context = "\n".join(context_parts) if context_parts else ""
            full_query = f"{context}\n\nRequest: {query}" if context else query
            
            if verbose:
                print("📡 Invoking agent...\n")
            
            result = self.agent_executor.invoke({
                "input": full_query,
                "chat_history": []
            })
            
            if verbose:
                print("✅ Agent response received\n")
            
            response_content = result.get("output", "")
            
            structured_response = self._try_parse_structured(response_content)
            
            return {
                "query": query,
                "response": {
                    "content": response_content,
                    "structured": structured_response
                },
                "context": {
                    "profile_url": profile_url,
                    "topics": topics,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        except Exception as e:
            if verbose:
                print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _try_parse_structured(self, content: str) -> Optional[Dict]:
        """Try to extract structured data from the response."""
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return None
    
    def generate_post(
        self,
        topic: str,
        tone: str = "professional",
        include_hashtags: bool = True,
        verbose: bool = False
    ) -> Dict:
        """
        Generate a LinkedIn post on a specific topic.
        
        Args:
            topic: The topic for the post
            tone: Tone of the post (professional, casual, thought_leader, educational, inspirational)
            include_hashtags: Whether to include hashtags
            verbose: Whether to print progress
            
        Returns:
            Dict with the generated post content
        """
        query = f"Generate a LinkedIn post about {topic}. Use a {tone} tone."
        if include_hashtags:
            query += " Include relevant hashtags."
        
        return self.run(query, topics=[topic], verbose=verbose)
    
    def analyze_feed(
        self,
        topics: Optional[List[str]] = None,
        limit: int = 20,
        verbose: bool = False
    ) -> Dict:
        """
        Analyze LinkedIn feed for engagement opportunities.
        
        Args:
            topics: Topics to focus on
            limit: Number of posts to analyze
            verbose: Whether to print progress
            
        Returns:
            Dict with feed analysis and engagement opportunities
        """
        query = f"Analyze my LinkedIn feed and identify the top {limit} engagement opportunities."
        if topics:
            query += f" Focus on posts about: {', '.join(topics)}."
        query += " Suggest which posts I should engage with and what kind of comments would be valuable."
        
        return self.run(query, topics=topics, verbose=verbose)
    
    def create_content_strategy(
        self,
        profile_url: Optional[str] = None,
        goals: Optional[List[str]] = None,
        industry: Optional[str] = None,
        verbose: bool = False
    ) -> Dict:
        """
        Create a LinkedIn content strategy.
        
        Args:
            profile_url: LinkedIn profile URL for context
            goals: List of goals (e.g., ["grow followers", "establish thought leadership"])
            industry: Target industry
            verbose: Whether to print progress
            
        Returns:
            Dict with content strategy recommendations
        """
        query = "Create a comprehensive LinkedIn content strategy for me."
        if goals:
            query += f" My goals are: {', '.join(goals)}."
        if industry:
            query += f" I'm in the {industry} industry."
        query += " Include posting frequency, content themes, engagement tactics, and growth metrics to track."
        
        return self.run(query, profile_url=profile_url, verbose=verbose)
    
    def generate_comments(
        self,
        topics: List[str],
        count: int = 5,
        verbose: bool = False
    ) -> Dict:
        """
        Generate comments for posts on specific topics.
        
        Args:
            topics: Topics to find posts for
            count: Number of comments to generate
            verbose: Whether to print progress
            
        Returns:
            Dict with generated comments for relevant posts
        """
        query = f"Find {count} posts about {', '.join(topics)} and generate thoughtful comments for each. Make the comments add value to the conversation."
        
        return self.run(query, topics=topics, verbose=verbose)
    
    def print_response(self, result: Dict):
        """Pretty print the agent's response."""
        print("\n" + "=" * 70)
        print("📱 LINKEDIN ACTIVITY AGENT RESPONSE")
        print("=" * 70)
        
        query = result.get("query", "Unknown")
        response = result.get("response", {})
        content = response.get("content", "No response")
        
        print(f"\n🔬 Request: {query}\n")
        print("-" * 70)
        print("📝 Response:\n")
        print(content)
        
        if response.get("structured"):
            print("\n" + "-" * 70)
            print("📊 Structured Data Available")
        
        context = result.get("context", {})
        print("\n" + "-" * 70)
        print(f"⏰ Timestamp: {context.get('timestamp', 'N/A')}")
        if context.get('profile_url'):
            print(f"👤 Profile: {context.get('profile_url')}")
        if context.get('topics'):
            print(f"🏷️  Topics: {', '.join(context.get('topics', []))}")
        
        print("=" * 70 + "\n")


def main():
    """Main function to demonstrate the LinkedIn Activity Agent."""
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.7)
    
    print("\n" + "🚀 LINKEDIN ACTIVITY AGENT" + "\n")
    print("=" * 70)
    
    demos = [
        {
            "name": "Generate a Post",
            "method": lambda: agent.generate_post(
                topic="artificial intelligence in the workplace",
                tone="thought_leader",
                verbose=True
            )
        },
        {
            "name": "Analyze Feed",
            "method": lambda: agent.analyze_feed(
                topics=["AI", "leadership", "career growth"],
                limit=10,
                verbose=True
            )
        },
        {
            "name": "Content Strategy",
            "method": lambda: agent.create_content_strategy(
                goals=["establish thought leadership", "grow professional network"],
                industry="Technology",
                verbose=True
            )
        },
        {
            "name": "Generate Comments",
            "method": lambda: agent.generate_comments(
                topics=["machine learning", "startup"],
                count=3,
                verbose=True
            )
        },
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            print(f"\n[{i}/{len(demos)}] Demo: {demo['name']}")
            print("-" * 50)
            result = demo["method"]()
            agent.print_response(result)
        except Exception as e:
            print(f"❌ Error in demo '{demo['name']}': {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
