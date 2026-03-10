"""
Research tools for the research agent.
Provides web search and Wikipedia search capabilities.
"""
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper


# Initialize Wikipedia wrapper
wikipedia_wrapper = WikipediaAPIWrapper(
    top_k_results=3,
    doc_content_chars_max=2000
)

# Initialize tools
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_wrapper)
web_search_tool = DuckDuckGoSearchRun()

# Export all tools
all_tools = [wikipedia_tool, web_search_tool]
