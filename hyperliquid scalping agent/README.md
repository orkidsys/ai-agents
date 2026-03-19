# Hyperliquid BTC Scalping Agent

An AI-powered trading agent that scalps BTC perpetual futures on Hyperliquid exchange using GPT-4 for decision making.

## Features

- **AI-Powered Analysis**: Uses GPT-4 with Schema-Guided Reasoning (SGR) for structured trading decisions
- **Technical Indicators**: EMA, RSI, MACD, Bollinger Bands, ATR, VWAP
- **Order Book Analysis**: Real-time depth and imbalance detection
- **Risk Management**: Position sizing, stop-loss, take-profit, trade limits
- **Real-Time Data**: WebSocket subscriptions for live market data
- **Automated Trading**: Continuous mode with configurable intervals

## Installation

```bash
cd "hyperliquid scalping agent"
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env-example .env
```

2. Configure your API keys in `.env`:
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Hyperliquid Configuration
HYPERLIQUID_PRIVATE_KEY=0x_your_private_key
HYPERLIQUID_ACCOUNT_ADDRESS=0x_your_account_address
HYPERLIQUID_NETWORK=testnet  # or mainnet

# Trading Parameters
MAX_POSITION_SIZE_USD=1000
DEFAULT_LEVERAGE=5
RISK_PER_TRADE=0.01
TAKE_PROFIT_PCT=0.005
STOP_LOSS_PCT=0.003
MAX_TRADES_PER_HOUR=10
```

## Usage

### Run the Agent

```bash
python main.py
```

### Run Examples

```bash
python example.py
```

### Example Options

1. **Market Data Only** - Fetch and display market data without AI
2. **Check Position** - View current position and account status
3. **Single Analysis** - Run one analysis cycle with AI
4. **Custom Analysis** - Run custom prompts
5. **Continuous Mode** - Run multiple cycles automatically

## Trading Strategy

The agent implements a scalping strategy with the following characteristics:

### Entry Signals

**Long Entry:**
- RSI between 30-45 (recovering from oversold)
- MACD histogram turning positive
- EMA 9 > EMA 21 (or crossing up)
- Order book shows bullish pressure
- Price near lower Bollinger Band

**Short Entry:**
- RSI between 55-70 (pulling back from overbought)
- MACD histogram turning negative
- EMA 9 < EMA 21 (or crossing down)
- Order book shows bearish pressure
- Price near upper Bollinger Band

### Exit Rules

- Take profit: 0.3-0.5% gain
- Stop loss: 0.2-0.3% loss
- Signal reversal
- Time-based exit (5-10 minutes without profit)

## Architecture

```
hyperliquid scalping agent/
├── main.py          # Main agent with continuous trading loop
├── tools.py         # Hyperliquid client and trading tools
├── schemas.py       # Pydantic schemas for structured reasoning
├── example.py       # Usage examples
├── requirements.txt # Python dependencies
├── .env-example     # Environment configuration template
└── README.md        # This file
```

### Components

- **BTCScalpingAgent**: Main agent class with LLM integration
- **HyperliquidClient**: Wrapper for Hyperliquid SDK
- **TechnicalAnalyzer**: Technical indicator calculations
- **Tools**: LangChain tools for market data, positions, orders, risk checks

## Risk Warnings

⚠️ **IMPORTANT DISCLAIMERS:**

1. **Financial Risk**: Trading perpetual futures involves substantial risk of loss. Only trade with funds you can afford to lose.

2. **Not Financial Advice**: This software is for educational purposes. The trading decisions made by this AI are not financial advice.

3. **Testnet First**: Always test on testnet before using real funds.

4. **AI Limitations**: AI can make mistakes. Monitor the agent and be prepared to intervene.

5. **Market Risk**: Past performance does not guarantee future results. Markets can be unpredictable.

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_POSITION_SIZE_USD` | 1000 | Maximum position value in USD |
| `DEFAULT_LEVERAGE` | 5 | Default leverage multiplier |
| `RISK_PER_TRADE` | 0.01 | Risk 1% of account per trade |
| `TAKE_PROFIT_PCT` | 0.005 | Take profit at 0.5% gain |
| `STOP_LOSS_PCT` | 0.003 | Stop loss at 0.3% loss |
| `MAX_TRADES_PER_HOUR` | 10 | Maximum trades per hour |

## API References

- [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [Hyperliquid API Documentation](https://hyperliquid.gitbook.io/hyperliquid-docs/)
- [LangChain Documentation](https://python.langchain.com/)

## License

MIT License - Use at your own risk.
