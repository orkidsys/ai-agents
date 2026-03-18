# LinkedIn Activity Agent

An AI-powered LinkedIn engagement and content creation assistant built with LangChain that uses **Schema-Guided Reasoning (SGR)** to help professionals grow their LinkedIn presence.

## Features

- 📝 **Post Generation**: Create engaging, authentic LinkedIn posts on any topic
- 🔍 **Feed Analysis**: Identify high-value engagement opportunities in your feed
- 💬 **Comment Generation**: Generate thoughtful comments that add value to conversations
- 📊 **Content Strategy**: Develop comprehensive LinkedIn content strategies
- 👤 **Profile Analysis**: Analyze profiles for optimization opportunities
- 🎯 **Personalized Recommendations**: Get tailored advice based on your goals

## Architecture

### Schema-Guided Reasoning (SGR)

The agent follows a structured 5-step reasoning process:

1. **Request Parsing** - Understands the activity type (post, engage, analyze, strategy)
2. **Data Gathering** - Fetches relevant LinkedIn data using tools
3. **Analysis & Insights** - Identifies patterns, trends, and opportunities
4. **Content Generation** - Creates posts, comments, or strategy documents
5. **Recommendations** - Provides actionable next steps

### Available Tools

| Tool | Description |
|------|-------------|
| `fetch_linkedin_feed` | Get posts from LinkedIn feed |
| `analyze_linkedin_profile` | Analyze a LinkedIn profile |
| `generate_linkedin_post` | Create post content |
| `generate_linkedin_comment` | Generate thoughtful comments |
| `search_linkedin_posts` | Find relevant posts for engagement |

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
```

## Usage

### Basic Usage

```python
from main import LinkedInActivityAgent

# Initialize the agent
agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.7)

# Generate a post
result = agent.generate_post(
    topic="artificial intelligence in healthcare",
    tone="thought_leader",
    verbose=True
)

# Print the response
agent.print_response(result)
```

### Generate LinkedIn Posts

```python
from main import LinkedInActivityAgent

agent = LinkedInActivityAgent()

# Different tones available:
# - professional: Formal, business-appropriate
# - casual: Friendly, conversational
# - thought_leader: Bold, opinion-driven
# - educational: Teaching, informative
# - inspirational: Motivating, story-driven

result = agent.generate_post(
    topic="the future of remote work",
    tone="thought_leader",
    include_hashtags=True,
    verbose=True
)
```

### Analyze Feed for Engagement

```python
result = agent.analyze_feed(
    topics=["AI", "leadership", "startups"],
    limit=20,
    verbose=True
)
```

### Create Content Strategy

```python
result = agent.create_content_strategy(
    profile_url="https://www.linkedin.com/in/your-profile",
    goals=["establish thought leadership", "grow to 10K followers"],
    industry="Technology",
    verbose=True
)
```

### Generate Comments

```python
result = agent.generate_comments(
    topics=["machine learning", "career growth"],
    count=5,
    verbose=True
)
```

### Custom Queries

```python
result = agent.run(
    query="Help me transition from software engineer to product manager on LinkedIn",
    topics=["product management", "career transition"],
    verbose=True
)
```

### Running Examples

```bash
# Run default example
python example.py

# Run specific example
python example.py post      # Generate a post
python example.py feed      # Analyze feed
python example.py strategy  # Content strategy
python example.py comments  # Generate comments
python example.py custom    # Custom query
python example.py profile   # Profile analysis
python example.py all       # Run all examples
```

## Configuration

### Model Selection

```python
# GPT-4 (recommended for best quality)
agent = LinkedInActivityAgent(model_name="gpt-4")

# GPT-3.5 Turbo (faster, cheaper)
agent = LinkedInActivityAgent(model_name="gpt-3.5-turbo")

# GPT-4 Turbo (balanced)
agent = LinkedInActivityAgent(model_name="gpt-4-turbo")
```

### Temperature Settings

```python
# Lower (0.3-0.5): More focused, consistent output
agent = LinkedInActivityAgent(temperature=0.4)

# Higher (0.7-0.9): More creative, varied content
agent = LinkedInActivityAgent(temperature=0.8)
```

## Response Structure

```python
{
    "query": "Generate a post about AI",
    "response": {
        "content": "...",  # The main response text
        "structured": {...}  # Parsed structured data (if available)
    },
    "context": {
        "profile_url": "...",
        "topics": ["AI", "technology"],
        "timestamp": "2024-01-15T10:30:00"
    }
}
```

## Project Structure

```
linkedin activity agent/
├── main.py              # LinkedInActivityAgent class
├── tools.py             # LinkedIn tools (feed, profile, content generation)
├── schemas.py           # 5-step SGR Pydantic schemas
├── example.py           # Usage examples
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Content Guidelines

The agent follows best practices for LinkedIn engagement:

- **Authenticity**: Creates genuine, value-driven content
- **No Clickbait**: Avoids sensationalism and empty promises
- **Professional Tone**: Respects LinkedIn's professional context
- **Engagement Focus**: Encourages meaningful conversations
- **Value-First**: Prioritizes audience benefit over self-promotion

## API Integration

### Current Implementation (Mock Data)

The current implementation uses mock data for demonstration. This allows testing without API credentials.

### Production Integration Options

For production use, integrate with:

1. **LinkedIn Marketing API** (for company pages)
2. **LinkedIn API with OAuth 2.0** (for personal profiles)
3. **Third-party services**:
   - [Proxycurl](https://proxycurl.com/) - Profile data
   - [PhantomBuster](https://phantombuster.com/) - Automation
   - [RapidAPI LinkedIn APIs](https://rapidapi.com/) - Various endpoints

Example integration in `tools.py`:

```python
class LinkedInService:
    def __init__(self):
        self.api_key = os.getenv("LINKEDIN_API_KEY")
        # Add your API client initialization
    
    def fetch_feed(self, ...):
        # Replace mock with actual API calls
        pass
```

## Requirements

- Python 3.10+
- OpenAI API key (required)
- Internet connection

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Check API key is valid and has credits

2. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Ensure virtual environment is activated

3. **Rate Limits**
   - Add delays between API calls
   - Use GPT-3.5 Turbo for testing

## Best Practices

1. **Start Small**: Test with single posts before bulk generation
2. **Review Output**: Always review generated content before posting
3. **Personalize**: Edit generated content to add your unique voice
4. **Engage Authentically**: Use generated comments as starting points
5. **Track Results**: Monitor engagement metrics to refine strategy

## License

MIT

## References

- Built with [LangChain](https://langchain.com/)
- Uses [OpenAI GPT-4](https://openai.com/)
- Implements Schema-Guided Reasoning (SGR) pattern
