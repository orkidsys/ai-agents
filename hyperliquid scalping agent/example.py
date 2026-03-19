"""
Example usage of the Hyperliquid BTC Scalping Agent.

This file demonstrates various ways to use the agent:
1. Single analysis cycle
2. Continuous trading mode
3. Manual signal checking
4. Position management
"""
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

from main import BTCScalpingAgent
from tools import HyperliquidClient, TechnicalAnalyzer


def example_single_analysis():
    """Run a single market analysis without trading."""
    print("\n" + "=" * 60)
    print("📊 SINGLE ANALYSIS EXAMPLE")
    print("=" * 60)
    
    agent = BTCScalpingAgent(
        model_name="gpt-4",
        temperature=0.1,
        verbose=True
    )
    
    result = agent.run_single_cycle()
    
    print("\n📋 Analysis Result:")
    print("-" * 40)
    if result.get("success"):
        print(result.get("output", "No output"))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


def example_market_data_only():
    """Fetch market data without the AI agent."""
    print("\n" + "=" * 60)
    print("📈 MARKET DATA EXAMPLE (No AI)")
    print("=" * 60)
    
    client = HyperliquidClient()
    analyzer = TechnicalAnalyzer()
    
    mid_price = client.get_mid_price("BTC")
    print(f"\n💰 BTC Mid Price: ${mid_price:,.2f}" if mid_price else "\n⚠️  Could not fetch price")
    
    l2_data = client.get_l2_snapshot("BTC")
    if l2_data:
        orderbook = analyzer.analyze_orderbook(l2_data)
        print(f"\n📊 Order Book Analysis:")
        print(f"   Bid Depth: ${orderbook['bid_depth_usd']:,.2f}")
        print(f"   Ask Depth: ${orderbook['ask_depth_usd']:,.2f}")
        print(f"   Imbalance: {orderbook['imbalance_ratio']:.2f}")
        print(f"   Pressure: {orderbook['pressure']}")
    
    candles = client.get_candles("BTC", "1m", 100)
    if candles:
        analyzer.load_candles(candles)
        indicators = analyzer.calculate_indicators()
        
        print(f"\n📉 Technical Indicators:")
        print(f"   EMA 9: ${indicators['ema_9']:,.2f}")
        print(f"   EMA 21: ${indicators['ema_21']:,.2f}")
        print(f"   RSI 14: {indicators['rsi_14']:.2f}")
        print(f"   MACD: {indicators['macd_line']:.2f}")
        print(f"   MACD Signal: {indicators['macd_signal']:.2f}")
        print(f"   MACD Histogram: {indicators['macd_histogram']:.2f}")
        print(f"   ATR 14: ${indicators['atr_14']:,.2f}")
        print(f"   Bollinger Upper: ${indicators['bollinger_upper']:,.2f}")
        print(f"   Bollinger Middle: ${indicators['bollinger_middle']:,.2f}")
        print(f"   Bollinger Lower: ${indicators['bollinger_lower']:,.2f}")
        
        ema_signal = "BULLISH" if indicators['ema_9'] > indicators['ema_21'] else "BEARISH"
        rsi_signal = "OVERSOLD" if indicators['rsi_14'] < 30 else "OVERBOUGHT" if indicators['rsi_14'] > 70 else "NEUTRAL"
        macd_signal = "BULLISH" if indicators['macd_histogram'] > 0 else "BEARISH"
        
        print(f"\n🎯 Quick Signals:")
        print(f"   EMA Crossover: {ema_signal}")
        print(f"   RSI: {rsi_signal} ({indicators['rsi_14']:.1f})")
        print(f"   MACD: {macd_signal}")


def example_check_position():
    """Check current position status."""
    print("\n" + "=" * 60)
    print("📍 POSITION CHECK EXAMPLE")
    print("=" * 60)
    
    client = HyperliquidClient()
    
    position = client.get_position("BTC")
    
    if position:
        print(f"\n✅ Open Position Found:")
        print(f"   Side: {position['side'].upper()}")
        print(f"   Size: {position['size']:.6f} BTC")
        print(f"   Entry: ${position['entry_price']:,.2f}")
        print(f"   PnL: ${position['unrealized_pnl']:,.2f}")
        print(f"   Leverage: {position['leverage']}x")
    else:
        print("\n📭 No open position")
    
    user_state = client.get_user_state()
    if user_state:
        margin = user_state.get("marginSummary", {})
        print(f"\n💼 Account Summary:")
        print(f"   Equity: ${float(margin.get('accountValue', 0)):,.2f}")
        print(f"   Margin Used: ${float(margin.get('totalMarginUsed', 0)):,.2f}")


def example_continuous_mode():
    """Run in continuous mode for a limited number of cycles."""
    print("\n" + "=" * 60)
    print("🔄 CONTINUOUS MODE EXAMPLE (5 cycles)")
    print("=" * 60)
    
    agent = BTCScalpingAgent(
        model_name="gpt-4",
        temperature=0.1,
        verbose=True
    )
    
    agent.run_continuous(
        interval_seconds=60,
        max_cycles=5
    )


def example_custom_analysis():
    """Custom analysis prompt example."""
    print("\n" + "=" * 60)
    print("🔧 CUSTOM ANALYSIS EXAMPLE")
    print("=" * 60)
    
    agent = BTCScalpingAgent(
        model_name="gpt-4",
        temperature=0.1,
        verbose=True
    )
    
    custom_prompt = """Analyze the current BTC market for a potential scalping opportunity.

Focus specifically on:
1. Is the spread tight enough for scalping? (< 5 bps is ideal)
2. Is there clear directional momentum in the last 5 candles?
3. What's the order book imbalance telling us?

Do NOT execute any trades - just provide analysis.
Call get_market_data and provide your assessment."""
    
    result = agent.executor.invoke({
        "input": custom_prompt,
        "chat_history": []
    })
    
    print("\n📋 Custom Analysis Result:")
    print("-" * 40)
    print(result.get("output", "No output"))


if __name__ == "__main__":
    print("\n🤖 Hyperliquid BTC Scalping Agent - Examples")
    print("=" * 60)
    
    examples = {
        "1": ("Market Data Only (No AI)", example_market_data_only),
        "2": ("Check Position", example_check_position),
        "3": ("Single Analysis (with AI)", example_single_analysis),
        "4": ("Custom Analysis", example_custom_analysis),
        "5": ("Continuous Mode (5 cycles)", example_continuous_mode),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n  0. Run all examples")
    print("  q. Quit")
    
    choice = input("\nSelect example (0-5, q): ").strip().lower()
    
    if choice == "q":
        print("Goodbye!")
    elif choice == "0":
        for key, (name, func) in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
            print("\n")
    elif choice in examples:
        name, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice")
