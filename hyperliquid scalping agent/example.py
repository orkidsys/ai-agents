"""
Example usage of the Hyperliquid BTC Multi-Strategy Scalping Agent.

Demonstrations:
1. Market data + all advanced indicators (no AI)
2. Multi-timeframe confluence analysis (no AI)
3. Funding rate check (no AI)
4. Position / trailing stop / equity status
5. Single AI analysis cycle
6. Strategy-specific analysis (choose strategy)
7. Continuous mode (5 cycles)
"""
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from main import BTCScalpingAgent
from tools import (
    HyperliquidClient,
    TechnicalAnalyzer,
    MultiTimeframeEngine,
    SessionFilter,
)


def example_market_data():
    """Fetch full market data + all advanced indicators."""
    print(f"\n{'='*60}")
    print("  MARKET DATA + ADVANCED INDICATORS")
    print(f"{'='*60}")

    client = HyperliquidClient()
    analyzer = TechnicalAnalyzer()

    mid_price = client.get_mid_price("BTC")
    print(f"\n  BTC Mid Price: ${mid_price:,.2f}" if mid_price else "\n  Could not fetch price")

    candles = client.get_candles("BTC", "1m", 200)
    if candles:
        analyzer.load_candles(candles)
        core = analyzer.calculate_indicators()
        advanced = analyzer.compute_all_advanced(client.get_recent_trades("BTC"))

        print(f"\n  --- Core Indicators ---")
        print(f"  EMA 9/21      : ${core['ema_9']:,.2f} / ${core['ema_21']:,.2f}  "
              f"({'BULL' if core['ema_9'] > core['ema_21'] else 'BEAR'})")
        print(f"  RSI 14        : {core['rsi_14']:.1f}")
        print(f"  MACD Hist     : {core['macd_histogram']:.2f}")
        print(f"  ATR 14        : ${core['atr_14']:,.2f}")
        print(f"  Bollinger     : ${core['bollinger_lower']:,.2f} | ${core['bollinger_middle']:,.2f} | ${core['bollinger_upper']:,.2f}")

        ich = advanced["ichimoku"]
        print(f"\n  --- Ichimoku Cloud ---")
        print(f"  Tenkan/Kijun  : ${ich['tenkan']:,.2f} / ${ich['kijun']:,.2f}")
        print(f"  Cloud Signal  : {ich['cloud_signal']}")

        srsi = advanced["stochastic_rsi"]
        print(f"\n  --- Stochastic RSI ---")
        print(f"  K/D           : {srsi['stoch_rsi_k']:.1f} / {srsi['stoch_rsi_d']:.1f}")
        print(f"  Signal        : {srsi['stoch_rsi_signal']}")

        adx = advanced["adx"]
        print(f"\n  --- ADX ---")
        print(f"  ADX           : {adx['adx']:.1f}  ({adx['trend_strength']})")
        print(f"  +DI / -DI     : {adx['plus_di']:.1f} / {adx['minus_di']:.1f}")

        st = advanced["supertrend"]
        print(f"\n  --- Supertrend ---")
        print(f"  Direction     : {st['supertrend_direction']}")
        print(f"  Level         : ${st['supertrend']:,.2f}")

        obv = advanced["obv"]
        print(f"\n  --- OBV ---")
        print(f"  Divergence    : {obv['obv_divergence']}")

        cmf = advanced["cmf"]
        print(f"\n  --- CMF ---")
        print(f"  CMF           : {cmf['cmf']:.4f}  ({cmf['cmf_signal']})")

        ha = advanced["heikin_ashi"]
        print(f"\n  --- Heikin Ashi ---")
        print(f"  Trend         : {ha['ha_trend']}  (streak: {ha['ha_streak']})")
        print(f"  Reversal      : {ha['ha_reversal']}  Strong: {ha.get('ha_strong_trend', False)}")

        sq = advanced["volatility_squeeze"]
        print(f"\n  --- Volatility Squeeze ---")
        print(f"  Squeeze On    : {sq['squeeze_on']}")
        print(f"  Signal        : {sq['squeeze_signal']}")

        div = advanced["divergences"]
        print(f"\n  --- Divergences ---")
        print(f"  RSI           : {div['rsi_divergence']}")
        print(f"  MACD          : {div['macd_divergence']}")

        ms = advanced["market_structure"]
        print(f"\n  --- Market Structure ---")
        print(f"  Structure     : {ms['structure']}")
        print(f"  Last BOS      : {ms['last_bos']}")

        of = advanced["order_flow"]
        print(f"\n  --- Order Flow ---")
        print(f"  Delta         : ${of['delta']:,.0f}")
        print(f"  CVD Trend     : {of['cvd_trend']}")
        print(f"  Large Trades  : {of['large_trades']}")

        pp = advanced["pivot_points"]
        print(f"\n  --- Pivot Points ---")
        print(f"  S3/S2/S1      : ${pp['s3']:,.2f} / ${pp['s2']:,.2f} / ${pp['s1']:,.2f}")
        print(f"  Pivot         : ${pp['pivot']:,.2f}")
        print(f"  R1/R2/R3      : ${pp['r1']:,.2f} / ${pp['r2']:,.2f} / ${pp['r3']:,.2f}")

        fib = advanced["fibonacci"]
        print(f"\n  --- Fibonacci ({fib['fib_trend']}) ---")
        print(f"  0% / 23.6%    : ${fib['fib_0']:,.2f} / ${fib['fib_236']:,.2f}")
        print(f"  38.2% / 50%   : ${fib['fib_382']:,.2f} / ${fib['fib_500']:,.2f}")
        print(f"  61.8% / 78.6% : ${fib['fib_618']:,.2f} / ${fib['fib_786']:,.2f}")
        print(f"  Nearest       : {fib.get('nearest_level', 'N/A')}")

    l2 = client.get_l2_snapshot("BTC")
    if l2:
        ob = analyzer.analyze_orderbook(l2)
        print(f"\n  --- Order Book ---")
        print(f"  Bid/Ask Depth : ${ob['bid_depth_usd']:,.0f} / ${ob['ask_depth_usd']:,.0f}")
        print(f"  Imbalance     : {ob['imbalance_ratio']:.2f}  ({ob['pressure']})")
        print(f"  Spread        : {ob['spread_bps']:.1f} bps")
        if ob.get("bid_wall"):
            print(f"  Bid Wall      : ${ob['bid_wall']['price']:,.2f} ({ob['bid_wall']['size']:.4f} BTC)")
        if ob.get("ask_wall"):
            print(f"  Ask Wall      : ${ob['ask_wall']['price']:,.2f} ({ob['ask_wall']['size']:.4f} BTC)")

    session = SessionFilter.current_session()
    print(f"\n  --- Session ---")
    print(f"  UTC Hour      : {session['utc_hour']}")
    print(f"  Sessions      : {', '.join(session['active_sessions']) or 'none'}")
    print(f"  Kill Zones    : {', '.join(session['in_kill_zone']) or 'none'}")
    print(f"  Vol Factor    : {session['volatility_factor']}")
    print(f"  Trade?        : {'YES' if session['recommended_trading'] else 'NO'}")


def example_multi_timeframe():
    """Multi-timeframe confluence analysis."""
    print(f"\n{'='*60}")
    print("  MULTI-TIMEFRAME CONFLUENCE")
    print(f"{'='*60}")

    client = HyperliquidClient()
    engine = MultiTimeframeEngine(client)
    result = engine.analyze("BTC")

    print(f"\n  Overall confluence: {result['confluence']}")
    print(f"  Bullish TFs: {result['bullish_count']}  Bearish TFs: {result['bearish_count']}")
    print(f"  HTF aligned: {result['htf_aligned']}")

    for tf, data in result["timeframes"].items():
        print(f"\n  [{tf}]  Trend: {data['trend']}  RSI: {data['rsi']:.1f}  "
              f"MACD: {data['macd_histogram']:.2f}  ADX: {data['adx']:.1f}  "
              f"Supertrend: {data['supertrend']}  Ichimoku: {data['ichimoku']}")


def example_funding_rate():
    """Check funding rate."""
    print(f"\n{'='*60}")
    print("  FUNDING RATE")
    print(f"{'='*60}")

    client = HyperliquidClient()
    data = client.get_funding_rate("BTC")
    if data:
        print(f"\n  Funding Rate    : {data['funding_rate']*100:.6f}%")
        print(f"  Annualised      : {data.get('annualised_rate', data['funding_rate']*8760)*100:.2f}%")
        print(f"  Open Interest   : ${data['open_interest']:,.0f}")
        print(f"  Premium         : {data['premium']*100:.4f}%")
        print(f"  Oracle Price    : ${data['oracle_price']:,.2f}")
        print(f"  Mark Price      : ${data['mark_price']:,.2f}")
    else:
        print("\n  Could not fetch funding rate")


def example_position():
    """Check position + trailing stop + equity protection."""
    print(f"\n{'='*60}")
    print("  POSITION STATUS")
    print(f"{'='*60}")

    client = HyperliquidClient()
    position = client.get_position("BTC")
    user_state = client.get_user_state()

    if position:
        print(f"\n  Side        : {position['side'].upper()}")
        print(f"  Size        : {position['size']:.6f} BTC")
        print(f"  Entry       : ${position['entry_price']:,.2f}")
        print(f"  PnL         : ${position['unrealized_pnl']:,.2f}")
        print(f"  Leverage    : {position['leverage']}x")
    else:
        print("\n  No open position")

    if user_state:
        margin = user_state.get("marginSummary", {})
        print(f"\n  Equity      : ${float(margin.get('accountValue', 0)):,.2f}")
        print(f"  Margin Used : ${float(margin.get('totalMarginUsed', 0)):,.2f}")


def example_single_analysis():
    """Run one full AI analysis cycle."""
    print(f"\n{'='*60}")
    print("  SINGLE AI ANALYSIS CYCLE")
    print(f"{'='*60}")

    agent = BTCScalpingAgent(model_name="gpt-4", temperature=0.1, verbose=True)
    result = agent.run_single_cycle()

    if result.get("success"):
        print(f"\n  Output:\n{result.get('output', 'N/A')}")
    elif result.get("output"):
        print(f"\n  Output:\n{result.get('output', 'N/A')}")
    else:
        print(f"\n  Error: {result.get('error', 'Unknown')}")


def example_strategy_analysis():
    """Run analysis targeted at a specific strategy."""
    print(f"\n{'='*60}")
    print("  STRATEGY-SPECIFIC ANALYSIS")
    print(f"{'='*60}")

    strategies = {
        "1": "momentum_scalp",
        "2": "mean_reversion",
        "3": "volatility_squeeze",
        "4": "order_flow_imbalance",
        "5": "multi_timeframe_confluence",
        "6": "funding_rate_fade",
        "7": "liquidity_sweep",
    }

    print("\n  Strategies:")
    for k, v in strategies.items():
        print(f"    {k}. {v}")

    choice = input("\n  Select (1-7): ").strip()
    if choice not in strategies:
        print("  Invalid choice")
        return

    strat = strategies[choice]
    agent = BTCScalpingAgent(model_name="gpt-4", temperature=0.1, verbose=True)

    prompt = f"""Evaluate BTC specifically for the {strat} strategy.

1. Call get_market_data for full indicator set.
2. Call multi_timeframe_analysis for HTF context.
3. Call get_funding_rate.
4. Assess whether the {strat} strategy conditions are met right now.
5. Score the setup confidence (low/medium/high/very_high).
6. If confident, call get_position, then risk_check, then execute_order.
7. Provide detailed reasoning.

Do NOT execute if confidence is low or medium — just explain what's missing."""

    result = agent.executor.invoke({"input": prompt, "chat_history": []})
    print(f"\n  Result:\n{result.get('output', 'No output')}")


def example_continuous():
    """Run 5 continuous cycles."""
    print(f"\n{'='*60}")
    print("  CONTINUOUS MODE (5 cycles)")
    print(f"{'='*60}")

    agent = BTCScalpingAgent(model_name="gpt-4", temperature=0.1, verbose=True)
    agent.run_continuous(interval_seconds=60, max_cycles=5)


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("  Hyperliquid BTC Scalping Agent — Examples")
    print(f"{'='*60}")

    examples = {
        "1": ("Market Data + All Indicators", example_market_data),
        "2": ("Multi-Timeframe Confluence", example_multi_timeframe),
        "3": ("Funding Rate", example_funding_rate),
        "4": ("Position Status", example_position),
        "5": ("Single AI Analysis", example_single_analysis),
        "6": ("Strategy-Specific Analysis", example_strategy_analysis),
        "7": ("Continuous Mode (5 cycles)", example_continuous),
    }

    print("\n  Available examples:")
    for k, (name, _) in examples.items():
        print(f"    {k}. {name}")
    print("    0. Run all")
    print("    q. Quit")

    choice = input("\n  Select: ").strip().lower()

    if choice == "q":
        print("  Goodbye!")
    elif choice == "0":
        for k, (name, func) in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n  Error in {name}: {e}")
    elif choice in examples:
        _, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"\n  Error: {e}")
    else:
        print("  Invalid choice")
