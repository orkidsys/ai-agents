# Hyperliquid BTC Multi-Strategy Scalping Agent

An AI-powered trading agent that scalps BTC perpetual futures on Hyperliquid using GPT-4 with 7 advanced strategies, 15+ technical indicators, multi-timeframe analysis, order flow tracking, and built-in risk management.

## Strategies

### 1. Momentum Scalp
Rides short-term directional moves when trend indicators align.
- **Entry**: EMA 9/21 crossover + MACD histogram direction + RSI 40-65 + Supertrend + ADX > 25
- **TP**: 0.4-0.6% (1.5x ATR) | **SL**: 0.2-0.3% (1x ATR) | **Hold**: 2-10 min

### 2. Mean Reversion
Fades price at Bollinger Band extremes in ranging markets.
- **Entry**: Price at BB extreme + RSI divergence + CMF reversal + Stochastic RSI cross + Heikin Ashi flip
- **TP**: Return to BB middle | **SL**: 0.3% beyond band | **Hold**: 3-15 min

### 3. Volatility Squeeze Breakout
Catches explosive moves when Bollinger Bands compress inside Keltner Channels.
- **Entry**: Squeeze fires (BB exits KC) + momentum direction + OBV confirmation
- **TP**: 0.5-0.8% (2x ATR) | **SL**: 0.3% (back inside squeeze) | **Hold**: 3-10 min

### 4. Order Flow Imbalance
Trades order book pressure and real-time trade flow.
- **Entry**: Book imbalance > 2x + strong CVD delta + large trade detection + tight spread
- **TP**: 0.3-0.5% | **SL**: 0.2% | **Hold**: 1-5 min

### 5. Multi-Timeframe Confluence
Enters on low-timeframe trigger aligned with higher-timeframe trend.
- **Entry**: 1h + 15m trends aligned + 5m EMA crossover + 1m RSI pullback + Ichimoku cloud agreement
- **TP**: 0.5-0.7% | **SL**: 0.3% | **Hold**: 5-15 min

### 6. Funding Rate Fade
Fades overcrowded positions when funding rate is extreme.
- **Entry**: Extreme funding (>0.05%/hr) + price at S/R level + order flow agreement
- **TP**: 0.4-0.6% | **SL**: 0.3% | **Hold**: 5-20 min

### 7. Liquidity Sweep / Market Structure Break
Catches reversals after liquidity grabs at swing highs/lows.
- **Entry**: Swing swept + price reclaims + Break of Structure confirmed + Fibonacci 61.8-78.6% zone + Heikin Ashi reversal + OBV divergence
- **TP**: Previous swing level | **SL**: Beyond swept level | **Hold**: 5-15 min

## Technical Indicators

| Category | Indicators |
|----------|-----------|
| **Trend** | EMA 9/21, MACD, Supertrend, Ichimoku Cloud, Heikin Ashi, ADX |
| **Momentum** | RSI 14, Stochastic RSI, MACD Histogram |
| **Volatility** | ATR, Bollinger Bands, Keltner Channels, Volatility Squeeze |
| **Volume** | OBV, CMF, VWAP, Volume SMA |
| **Structure** | Pivot Points, Fibonacci Retracements, Swing HH/HL/LH/LL, Break of Structure |
| **Order Flow** | CVD (Cumulative Volume Delta), Order Book Imbalance, Bid/Ask Walls, Large Trade Detection |

## Risk Management

- **Equity Curve Protection**: Pauses trading after max daily drawdown (default 5%) or 3 consecutive losses
- **Trailing Stop**: Activates at 0.3% profit, trails at 0.2% distance
- **Partial Take-Profit**: Closes 50-70% at first target, lets remainder run
- **Dynamic Sizing**: Position size calculated from account equity, risk percentage, and ATR
- **Adaptive Leverage**: Leverage reduced in high-volatility regimes
- **Session Filter**: Kill-zone detection (London open, NY open, overlap) with volatility factor
- **Spread Check**: Rejects trades when spread exceeds 5 basis points
- **Hourly Trade Limit**: Maximum trades per hour enforced
- **Funding Rate Awareness**: Avoids entering positions that pay extreme funding

## Installation

```bash
cd "hyperliquid scalping agent"
pip install -r requirements.txt
```

## Configuration

```bash
cp .env-example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=your_key
HYPERLIQUID_PRIVATE_KEY=0x_your_key
HYPERLIQUID_ACCOUNT_ADDRESS=0x_your_address
HYPERLIQUID_NETWORK=testnet

MAX_POSITION_SIZE_USD=1000
DEFAULT_LEVERAGE=5
RISK_PER_TRADE=0.01
TAKE_PROFIT_PCT=0.005
STOP_LOSS_PCT=0.003
MAX_TRADES_PER_HOUR=10
MAX_DAILY_DRAWDOWN_PCT=0.05
TRAILING_STOP_ACTIVATION_PCT=0.003
TRAILING_STOP_DISTANCE_PCT=0.002
```

## Usage

```bash
# Run the agent
python main.py

# Run interactive examples
python example.py
```

## Architecture

```
hyperliquid scalping agent/
├── main.py            # Agent with 7-strategy system prompt + continuous loop
├── tools.py           # Hyperliquid client, 15+ indicators, 6 LangChain tools
├── schemas.py         # Pydantic schemas for 7-step structured reasoning
├── example.py         # Interactive examples
├── requirements.txt   # Dependencies
├── .env-example       # Config template
└── README.md
```

### LangChain Tools

| Tool | Description |
|------|-------------|
| `get_market_data` | All indicators, orderbook, order flow, session info |
| `multi_timeframe_analysis` | 1m/5m/15m/1h confluence scoring |
| `get_funding_rate` | Funding rate, OI, premium, oracle/mark prices |
| `get_position` | Position + trailing stop + equity protection state |
| `execute_order` | Market/limit/partial-close with auto-sizing & trailing stop init |
| `risk_check` | 8-point pre-trade validation |

### Decision Process (7 Steps)

1. **Market Analysis** — Fetch all indicators, detect regime
2. **Multi-Timeframe** — HTF confluence + funding context
3. **Signal Detection** — Score every signal, compute combined score
4. **Strategy Selection** — Pick best strategy, list supporting/conflicting signals
5. **Risk Sizing** — ATR-based SL/TP, adaptive leverage, partial TP levels
6. **Execution** — Risk check then order
7. **Post-Trade Review** — Summary, trailing stop status, equity protection

## Risk Warnings

1. **Trading perpetual futures involves substantial risk of loss.** Only trade with funds you can afford to lose.
2. **Not financial advice.** This software is for educational purposes.
3. **Always test on testnet first.**
4. **AI can make mistakes.** Monitor the agent and be prepared to intervene.
5. **Past performance does not guarantee future results.**

## References

- [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [Hyperliquid API Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/)
- [LangChain](https://python.langchain.com/)
