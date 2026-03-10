# Portfolio Analysis Agent

A comprehensive cryptocurrency portfolio analysis agent built with LangChain that uses **Schema-Guided Reasoning (SGR)** to provide structured portfolio reports for EVM and Solana wallets.

## Features

- 🔍 **Multi-Chain Support**: Analyze portfolios across EVM networks (Ethereum, Base, BNB) and Solana
- 📊 **Historical Performance Tracking**: Daily, weekly, and monthly performance analysis
- 💰 **Real-Time Data**: Current token balances and price data via CoinGecko API
- 📈 **Comprehensive Analysis**: Portfolio composition, diversification, and performance metrics
- 🤖 **AI-Powered Insights**: Uses OpenAI GPT models for intelligent analysis
- 📋 **Structured Output**: 5-step Schema-Guided Reasoning process with Pydantic models

## Architecture

### Schema-Guided Reasoning (SGR)

The agent follows a structured 5-step reasoning process:

1. **Request Parsing** - Extracts time period (daily/weekly/monthly) and wallet addresses
2. **Portfolio Data Fetching** - Retrieves wallet balances and historical price data
3. **Portfolio Composition Analysis** - Analyzes current holdings, top tokens, and diversification
4. **Performance Analysis** - Calculates wins/losses, best/worst performers over the time period
5. **Report Generation** - Provides comprehensive portfolio report with insights and recommendations

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
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# COINGECKO_API_KEY=your_key_here (optional but recommended)
# ALCHEMY_API_KEY=your_key_here (for EVM wallet data)
```

## Usage

### Basic Usage

```python
from main import PortfolioAgent

# Initialize the agent
agent = PortfolioAgent(model_name="gpt-4", temperature=0.3)

# Analyze portfolio
result = agent.analyze(
    query="Review my portfolio",
    evm_wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    solana_wallet_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    verbose=True
)

# Print formatted results
agent.print_analysis(result)
```

### Advanced Usage

```python
from main import PortfolioAgent

# Create agent with custom settings
agent = PortfolioAgent(
    model_name="gpt-4",
    temperature=0.3  # Lower = more focused, Higher = more creative
)

# Multiple queries
queries = [
    "Review my portfolio",
    "Give me a daily report",
    "Analyze my portfolio and show which tokens are underperforming",
    "What is my total profit/loss this month?",
]

for query in queries:
    result = agent.analyze(
        query=query,
        evm_wallet_address="0x...",
        verbose=True
    )
    agent.print_analysis(result)
```

### Running Examples

```bash
# Run the main script
python main.py

# Run example usage
python example.py
```

## Response Structure

The agent returns a structured response with 5 steps:

```python
{
    "question": "Review my portfolio",
    "response": {
        "messages": [...],
        "structuredResponse": {
            "step1_requestParsing": {
                "userQuery": "...",
                "timeframe": "monthly",
                "walletAddresses": {...},
                "parsingReasoning": "..."
            },
            "step2_dataFetching": {
                "toolsUsed": [...],
                "portfolio": [...],
                "fetchingNotes": "..."
            },
            "step3_compositionAnalysis": {
                "totalAmountUsd": 10000,
                "topHoldings": [...],
                "compositionSummary": "..."
            },
            "step4_performanceAnalysis": {
                "periodStartValue": 9500,
                "periodEndValue": 10000,
                "totalDeltaUSD": 500,
                "totalDeltaPercentage": 5.26,
                "performanceSummary": "..."
            },
            "step5_reportGeneration": {
                "confidence": "high",
                "error": "no_error",
                "keyTakeaways": [...],
                "recommendations": [...],
                "summary": "..."
            }
        }
    }
}
```

## Configuration

### Model Selection

```python
# Use GPT-4 (default, recommended)
agent = PortfolioAgent(model_name="gpt-4")

# Use GPT-3.5 (faster, cheaper)
agent = PortfolioAgent(model_name="gpt-3.5-turbo")
```

### Temperature Control

```python
# Lower temperature (0.1-0.3): More focused, factual
agent = PortfolioAgent(temperature=0.2)

# Higher temperature (0.7-1.0): More creative, varied
agent = PortfolioAgent(temperature=0.7)
```

## Tools

### Available Tools

1. **get_historical_portfolio_data**: Fetches portfolio data including:
   - Current token balances
   - Historical prices at start of period
   - Current prices
   - Price changes and percentages
   - Top gainers/losers from the market

### API Integration

- **CoinGecko API**: Cryptocurrency price data and market information
- **Alchemy API**: EVM wallet balance and transaction data (optional)
- **Solana RPC**: Solana wallet data (optional, requires RPC endpoint)

## Project Structure

```
portfolio agent/
├── main.py              # Main PortfolioAgent class
├── tools.py             # Portfolio data fetching tools
├── schemas.py           # 5-step SGR Pydantic schemas
├── example.py           # Usage examples
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Important Notes

- The agent analyzes complete portfolio holdings across EVM and Solana wallets
- Supports daily, weekly, and monthly performance tracking
- Provides market context by comparing portfolio performance against top gainers/losers
- All analysis is for informational purposes only - **not financial advice**
- CoinGecko API key is optional but recommended to avoid rate limits
- Alchemy API key is required for full EVM wallet functionality

## Error Handling

The agent includes robust error handling:
- Graceful fallbacks if structured parsing fails
- Clear error messages for debugging
- Error classification (tool_error, llm_error, user_error, no_error)
- Confidence levels (low, medium, high)

## Requirements

- Python 3.12+
- OpenAI API key (required)
- CoinGecko API key (optional but recommended)
- Alchemy API key (optional, for EVM wallets)
- Internet connection (for API calls)

## Development

### Testing

```bash
# Run the main script
python main.py

# Run examples
python example.py
```

### Adding Custom Tools

To add custom tools, extend the `tools.py` file:

```python
from langchain_core.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "..."
    
    def _run(self, input: str) -> str:
        # Your tool logic
        return result
```

## License

MIT

## References

- Based on [Warden Protocol Portfolio Agent](https://github.com/warden-protocol/community-agents/tree/main/agents/portfolio-agent)
- Uses LangChain for agent orchestration
- Implements Schema-Guided Reasoning (SGR) pattern
- Multi-chain cryptocurrency portfolio analysis
