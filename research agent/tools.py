from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from datetime import datetime

# Use DuckDuckGoSearchRun directly - it's already a tool
search_tool = DuckDuckGoSearchRun()