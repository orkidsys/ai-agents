"""
Research Agent - A comprehensive research assistant using LangChain agents.

This agent can:
- Search the web for current information
- Query Wikipedia for detailed articles
- Synthesize information from multiple sources
- Provide structured research responses
"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools import all_tools
import os
import json
from typing import Optional, List
from datetime import datetime


# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


class ResearchResponse(BaseModel):
    """Structured response format for research results."""
    topic: str = Field(description="The research topic or question")
    summary: str = Field(description="Comprehensive summary of the research findings")
    key_points: List[str] = Field(description="Key points or facts discovered", default_factory=list)
    sources: List[str] = Field(description="List of sources used (URLs, article titles, etc.)", default_factory=list)
    tools_used: List[str] = Field(description="Tools used during research", default_factory=list)
    timestamp: str = Field(description="When the research was conducted", default_factory=lambda: datetime.now().isoformat())


class ResearchAgent:
    """A research agent that uses multiple tools to gather and synthesize information."""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        tools: Optional[List] = None
    ):
        """
        Initialize the research agent.
        
        Args:
            model_name: The LLM model to use (default: "gpt-4")
            temperature: Temperature for the model (lower = more focused)
            tools: List of tools to use (default: all available tools)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.tools = tools if tools else all_tools
        
        # Create the agent with an optimized system prompt
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the optimized system prompt for research tasks."""
        return """You are an expert research assistant with access to multiple information sources.

Your capabilities:
- Search the web for current information and recent developments
- Query Wikipedia for detailed, well-sourced articles
- Synthesize information from multiple sources
- Provide comprehensive, accurate, and well-structured research

Research Guidelines:
1. Always use tools to gather information before responding
2. Use multiple sources when possible for comprehensive coverage
3. Cite your sources clearly
4. Provide accurate, factual information
5. If information is uncertain or conflicting, mention this
6. Structure your response clearly with key points
7. Be thorough but concise

When researching:
- Start with Wikipedia for foundational knowledge
- Use web search for current information, recent events, or specific details
- Combine information from multiple sources for a complete picture
- Always verify important claims with multiple sources when possible

Format your response as a comprehensive research summary that includes:
- A clear summary of the topic
- Key points and important facts
- Sources used (tool names and any URLs/article titles available)
- Any relevant context or background information"""
    
    def research(self, query: str, verbose: bool = False) -> ResearchResponse:
        """
        Conduct research on a given query.
        
        Args:
            query: The research question or topic
            verbose: Whether to print intermediate steps
            
        Returns:
            ResearchResponse: Structured research results
        """
        if verbose:
            print(f"🔍 Researching: {query}\n")
            print("=" * 60)
        
        try:
            # Invoke the agent
            if verbose:
                print("📡 Gathering information from sources...\n")
            
            result = self.agent.invoke({
                "messages": [HumanMessage(content=query)]
            })
            
            # Extract the final message content
            if verbose:
                print("✅ Information gathered. Processing response...\n")
            
            # The agent returns messages, get the last one
            messages = result.get("messages", [])
            if not messages:
                raise ValueError("No messages returned from agent")
            
            # Get the final assistant message
            final_message = messages[-1]
            research_content = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            # Extract tool usage information
            tools_used = []
            sources = []
            
            # Check for tool calls in messages
            for msg in messages:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        if tool_name not in tools_used:
                            tools_used.append(tool_name)
            
            # Try to extract sources from the content
            # Look for URLs or source mentions
            if "http" in research_content:
                import re
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', research_content)
                sources.extend(urls)
            
            # Parse the response into structured format
            try:
                # Try to extract structured information using the LLM
                structured_prompt = f"""Based on the following research content, extract and format the information:

{research_content}

Please provide:
1. Topic: {query}
2. Summary: A comprehensive summary
3. Key Points: List 3-5 key points
4. Sources: Any sources mentioned
5. Tools Used: {', '.join(tools_used) if tools_used else 'web_search, wikipedia'}

Format as JSON matching this structure:
{{
    "topic": "...",
    "summary": "...",
    "key_points": ["...", "..."],
    "sources": ["..."],
    "tools_used": ["..."]
}}"""
                
                structured_result = self.llm.invoke(structured_prompt)
                structured_text = structured_result.content if hasattr(structured_result, 'content') else str(structured_result)
                
                # Try to parse JSON from the response
                # Look for JSON block
                import re
                json_match = re.search(r'\{.*\}', structured_text, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return ResearchResponse(**parsed_data)
                else:
                    # Fallback: create response from content
                    return ResearchResponse(
                        topic=query,
                        summary=research_content[:500] + "..." if len(research_content) > 500 else research_content,
                        key_points=self._extract_key_points(research_content),
                        sources=sources,
                        tools_used=tools_used if tools_used else ["web_search", "wikipedia"]
                    )
            except Exception as e:
                if verbose:
                    print(f"⚠️  Could not parse structured response: {e}")
                # Fallback to basic response
                return ResearchResponse(
                    topic=query,
                    summary=research_content,
                    key_points=self._extract_key_points(research_content),
                    sources=sources,
                    tools_used=tools_used if tools_used else ["web_search", "wikipedia"]
                )
        
        except Exception as e:
            if verbose:
                print(f"❌ Error during research: {e}")
            raise
    
    def _extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from research text."""
        # Simple extraction: split by sentences and take important ones
        sentences = text.split('. ')
        # Filter for sentences that seem important (contain keywords, are not too short)
        key_points = []
        for sentence in sentences:
            if len(sentence) > 30 and len(key_points) < max_points:
                # Simple heuristic: sentences with numbers, important words, etc.
                if any(word in sentence.lower() for word in ['important', 'key', 'significant', 'major', 'main', 'primary']):
                    key_points.append(sentence.strip())
                elif len(sentence) > 50:  # Longer sentences often contain key info
                    key_points.append(sentence.strip())
        
        return key_points[:max_points]
    
    def print_research(self, response: ResearchResponse):
        """Pretty print research results."""
        print("\n" + "=" * 70)
        print("📊 RESEARCH RESULTS")
        print("=" * 70)
        print(f"\n🔬 Topic: {response.topic}")
        print(f"\n📝 Summary:")
        print("-" * 70)
        print(response.summary)
        print("\n" + "-" * 70)
        
        if response.key_points:
            print(f"\n🔑 Key Points:")
            for i, point in enumerate(response.key_points, 1):
                print(f"   {i}. {point}")
        
        if response.sources:
            print(f"\n📚 Sources:")
            for source in response.sources:
                print(f"   • {source}")
        
        if response.tools_used:
            print(f"\n🛠️  Tools Used: {', '.join(response.tools_used)}")
        
        print(f"\n⏰ Research Date: {response.timestamp}")
        print("=" * 70 + "\n")


def main():
    """Main function to run the research agent."""
    # Initialize the research agent
    agent = ResearchAgent(model_name="gpt-4", temperature=0.3)
    
    # Example research queries
    queries = [
        "Explain the history of Greek mythology",
        # Add more queries here for testing
    ]
    
    # Process each query
    for query in queries:
        try:
            # Conduct research
            result = agent.research(query, verbose=True)
            
            # Print results
            agent.print_research(result)
            
        except Exception as e:
            print(f"❌ Error researching '{query}': {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
