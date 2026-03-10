# Research Agent

A comprehensive research assistant built with LangChain that uses multiple tools to gather and synthesize information from various sources.

## Features

- 🔍 **Multi-Source Research**: Uses both Wikipedia and web search (DuckDuckGo) for comprehensive information gathering
- 📊 **Structured Output**: Returns well-formatted research results with summaries, key points, and sources
- 🛠️ **Tool Integration**: Automatically uses appropriate tools based on the research query
- 🎯 **Smart Synthesis**: Combines information from multiple sources for complete coverage
- 📝 **Clean Formatting**: Pretty-printed results with clear sections

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt --index-url https://pypi.org/simple/
```

3. Set up environment variables:
```bash
cp .env-example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here (optional)
```

## Usage

### Basic Usage

```python
from main import ResearchAgent

# Initialize the agent
agent = ResearchAgent(model_name="gpt-4", temperature=0.3)

# Conduct research
result = agent.research("What are the latest developments in quantum computing?")

# Print results
agent.print_research(result)
```

### Advanced Usage

```python
from main import ResearchAgent

# Create agent with custom settings
agent = ResearchAgent(
    model_name="gpt-4",
    temperature=0.3,  # Lower = more focused, Higher = more creative
    tools=[...]  # Optional: specify custom tools
)

# Research with verbose output
result = agent.research(
    "Explain the history of Greek mythology",
    verbose=True  # Shows progress during research
)

# Access structured data
print(f"Topic: {result.topic}")
print(f"Summary: {result.summary}")
print(f"Key Points: {result.key_points}")
print(f"Sources: {result.sources}")
print(f"Tools Used: {result.tools_used}")
```

### Running Examples

```bash
# Run the main script
python main.py

# Run example usage
python example.py
```

## Architecture

### Components

1. **ResearchAgent Class**: Main agent class that orchestrates research
2. **Tools Module**: Provides Wikipedia and DuckDuckGo search tools
3. **ResearchResponse Model**: Pydantic model for structured output

### How It Works

1. **Query Processing**: Takes a research question/topic
2. **Tool Selection**: Agent automatically decides which tools to use
3. **Information Gathering**: Uses Wikipedia for foundational knowledge and web search for current info
4. **Synthesis**: Combines information from multiple sources
5. **Structured Output**: Formats results with summary, key points, and sources

## Response Format

The agent returns a `ResearchResponse` object with:

- **topic**: The research topic/question
- **summary**: Comprehensive summary of findings
- **key_points**: List of important points discovered
- **sources**: List of sources used (URLs, article titles)
- **tools_used**: Tools that were utilized
- **timestamp**: When the research was conducted

## Configuration

### Model Selection

```python
# Use GPT-4 (default, recommended)
agent = ResearchAgent(model_name="gpt-4")

# Use GPT-3.5 (faster, cheaper)
agent = ResearchAgent(model_name="gpt-3.5-turbo")
```

### Temperature Control

```python
# Lower temperature (0.1-0.3): More focused, factual
agent = ResearchAgent(temperature=0.2)

# Higher temperature (0.7-1.0): More creative, varied
agent = ResearchAgent(temperature=0.7)
```

## Tools

### Available Tools

1. **WikipediaQueryRun**: Searches Wikipedia for detailed articles
   - Best for: Foundational knowledge, historical information, established facts
   
2. **DuckDuckGoSearchRun**: Web search for current information
   - Best for: Recent developments, current events, specific details

The agent automatically selects and uses the appropriate tools based on the query.

## Error Handling

The agent includes robust error handling:
- Graceful fallbacks if structured parsing fails
- Clear error messages for debugging
- Continues operation even if one tool fails

## Requirements

- Python 3.12+
- OpenAI API key
- Internet connection (for web search and Wikipedia)

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
