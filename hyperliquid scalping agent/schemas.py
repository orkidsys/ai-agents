"""
Schema-Guided Reasoning (SGR) schemas for Hyperliquid BTC Scalping Agent.

Includes schemas for 7 advanced strategies:
1. Momentum Scalp (EMA/MACD/RSI alignment)
2. Mean Reversion (Bollinger Band + RSI extremes)
3. Volatility Squeeze Breakout (BB squeeze + Keltner)
4. Order Flow Imbalance (CVD + orderbook delta)
5. Multi-Timeframe Confluence (HTF trend + LTF entry)
6. Funding Rate Fade (overcrowded positioning)
7. Liquidity Sweep / Market Structure Break
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


# ===========================================================================
# Market data & indicator schemas
# ===========================================================================

class MarketData(BaseModel):
    symbol: str = Field(default="BTC")
    mid_price: float = Field(description="Current mid-market price")
    best_bid: float = Field(description="Best bid price")
    best_ask: float = Field(description="Best ask price")
    spread: float = Field(description="Bid-ask spread")
    spread_bps: float = Field(description="Spread in basis points")
    timestamp: datetime = Field(description="Data timestamp")


class CoreIndicators(BaseModel):
    ema_9: float = Field(description="9-period EMA")
    ema_21: float = Field(description="21-period EMA")
    rsi_14: float = Field(description="14-period RSI")
    macd_line: float = Field(description="MACD line")
    macd_signal: float = Field(description="MACD signal")
    macd_histogram: float = Field(description="MACD histogram")
    atr_14: float = Field(description="14-period ATR")
    volume_sma: float = Field(description="Volume SMA 20")
    bollinger_upper: float = Field(description="Upper BB")
    bollinger_middle: float = Field(description="Middle BB (SMA 20)")
    bollinger_lower: float = Field(description="Lower BB")
    vwap: Optional[float] = Field(default=None, description="VWAP")


class IchimokuData(BaseModel):
    tenkan: float = 0
    kijun: float = 0
    senkou_a: float = 0
    senkou_b: float = 0
    chikou: float = 0
    cloud_signal: Literal["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"] = "neutral"


class StochasticRSIData(BaseModel):
    stoch_rsi_k: float = 50
    stoch_rsi_d: float = 50
    stoch_rsi_signal: Literal["oversold_reversal", "overbought_reversal", "oversold", "overbought", "neutral"] = "neutral"


class ADXData(BaseModel):
    adx: float = 0
    plus_di: float = 0
    minus_di: float = 0
    trend_strength: Literal["weak", "moderate", "strong", "very_strong", "none"] = "none"


class OBVData(BaseModel):
    obv: float = 0
    obv_ema: float = 0
    obv_divergence: Literal["bullish_divergence", "bearish_divergence", "none"] = "none"


class SupertrendData(BaseModel):
    supertrend: float = 0
    supertrend_direction: Literal["bullish", "bearish", "neutral"] = "neutral"


class PivotPoints(BaseModel):
    pivot: float = 0
    r1: float = 0
    r2: float = 0
    r3: float = 0
    s1: float = 0
    s2: float = 0
    s3: float = 0


class FibonacciLevels(BaseModel):
    fib_0: float = 0
    fib_236: float = 0
    fib_382: float = 0
    fib_500: float = 0
    fib_618: float = 0
    fib_786: float = 0
    fib_100: float = 0
    fib_trend: Literal["uptrend", "downtrend", "neutral"] = "neutral"
    nearest_level: Optional[str] = None
    distance_to_nearest: float = 0


class CMFData(BaseModel):
    cmf: float = 0
    cmf_signal: Literal["strong_accumulation", "accumulation", "neutral", "distribution", "strong_distribution"] = "neutral"


class HeikinAshiData(BaseModel):
    ha_trend: Literal["bullish", "bearish", "neutral"] = "neutral"
    ha_streak: int = 0
    ha_reversal: bool = False
    ha_strong_trend: bool = False


class VolatilitySqueezeData(BaseModel):
    squeeze_on: bool = False
    squeeze_momentum: float = 0
    squeeze_signal: Literal["squeeze_building", "squeeze_fire_long", "squeeze_fire_short", "no_squeeze", "no_data"] = "no_data"


class DivergenceData(BaseModel):
    rsi_divergence: Literal["bullish", "bearish", "none"] = "none"
    macd_divergence: Literal["bullish", "bearish", "none"] = "none"


class MarketStructureData(BaseModel):
    structure: Literal["bullish", "bearish", "expanding", "contracting", "mixed", "unknown"] = "unknown"
    swing_highs: List[Dict[str, Any]] = Field(default_factory=list)
    swing_lows: List[Dict[str, Any]] = Field(default_factory=list)
    last_bos: Literal["bullish_bos", "bearish_bos", "none"] = "none"


class OrderFlowData(BaseModel):
    buy_volume: float = 0
    sell_volume: float = 0
    delta: float = 0
    cvd_trend: Literal["strong_buying", "buying", "neutral", "selling", "strong_selling"] = "neutral"
    large_trades: int = 0


class OrderBookAnalysis(BaseModel):
    bid_depth_usd: float = 0
    ask_depth_usd: float = 0
    imbalance_ratio: float = 1.0
    pressure: Literal["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"] = "neutral"
    bid_wall: Optional[Dict[str, float]] = None
    ask_wall: Optional[Dict[str, float]] = None
    spread_bps: float = 0


class FundingRateData(BaseModel):
    funding_rate: float = 0
    annualised_rate: float = 0
    open_interest: float = 0
    premium: float = 0
    oracle_price: float = 0
    mark_price: float = 0
    funding_signal: Literal["extreme_long_pay", "longs_paying", "neutral", "shorts_paying", "extreme_short_pay"] = "neutral"


class SessionInfo(BaseModel):
    utc_hour: int = 0
    active_sessions: List[str] = Field(default_factory=list)
    in_kill_zone: List[str] = Field(default_factory=list)
    is_overlap: bool = False
    volatility_factor: float = 1.0
    recommended_trading: bool = False


class MultiTimeframeResult(BaseModel):
    confluence: Literal["strong_bullish", "bullish", "mixed", "bearish", "strong_bearish"] = "mixed"
    bullish_count: int = 0
    bearish_count: int = 0
    htf_aligned: bool = False
    timeframes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


# ===========================================================================
# Advanced indicators bundle
# ===========================================================================

class AdvancedIndicators(BaseModel):
    ichimoku: IchimokuData = Field(default_factory=IchimokuData)
    stochastic_rsi: StochasticRSIData = Field(default_factory=StochasticRSIData)
    adx: ADXData = Field(default_factory=ADXData)
    obv: OBVData = Field(default_factory=OBVData)
    supertrend: SupertrendData = Field(default_factory=SupertrendData)
    pivot_points: PivotPoints = Field(default_factory=PivotPoints)
    fibonacci: FibonacciLevels = Field(default_factory=FibonacciLevels)
    cmf: CMFData = Field(default_factory=CMFData)
    heikin_ashi: HeikinAshiData = Field(default_factory=HeikinAshiData)
    volatility_squeeze: VolatilitySqueezeData = Field(default_factory=VolatilitySqueezeData)
    divergences: DivergenceData = Field(default_factory=DivergenceData)
    market_structure: MarketStructureData = Field(default_factory=MarketStructureData)
    order_flow: OrderFlowData = Field(default_factory=OrderFlowData)


# ===========================================================================
# Position & risk schemas
# ===========================================================================

class PositionState(BaseModel):
    has_position: bool = False
    side: Optional[Literal["long", "short"]] = None
    size: float = 0
    entry_price: Optional[float] = None
    unrealized_pnl: float = 0
    leverage: int = 1


class TrailingStopState(BaseModel):
    trailing_active: bool = False
    should_close: bool = False
    stop_price: Optional[float] = None
    peak_price: Optional[float] = None


class EquityProtectionState(BaseModel):
    can_trade: bool = True
    daily_drawdown_pct: float = 0
    drawdown_breached: bool = False
    consecutive_losses: int = 0
    loss_cooldown_active: bool = False
    trades_today: int = 0
    pnl_today: float = 0


class RiskAssessment(BaseModel):
    account_equity: float = Field(description="Account equity in USD")
    risk_amount: float = Field(description="Max risk for this trade in USD")
    position_size_btc: float = Field(description="Calculated position size")
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    atr_based_sl: Optional[float] = Field(default=None, description="ATR-derived stop loss distance")
    trailing_stop_config: Optional[TrailingStopState] = None


# ===========================================================================
# Strategy classification
# ===========================================================================

STRATEGY_TYPES = Literal[
    "momentum_scalp",
    "mean_reversion",
    "volatility_squeeze",
    "order_flow_imbalance",
    "multi_timeframe_confluence",
    "funding_rate_fade",
    "liquidity_sweep",
]


class StrategySelection(BaseModel):
    """Which strategy was selected and why."""
    selected_strategy: STRATEGY_TYPES = Field(description="The strategy being applied")
    confidence: Literal["low", "medium", "high", "very_high"] = Field(description="Confidence in this setup")
    reasoning: str = Field(description="Why this strategy was chosen over others")
    supporting_signals: List[str] = Field(description="List of indicators/signals supporting this strategy")
    conflicting_signals: List[str] = Field(default_factory=list, description="Signals that disagree")


# ===========================================================================
# 7-step SGR decision process
# ===========================================================================

class Step1MarketAnalysis(BaseModel):
    """STEP 1: Comprehensive market snapshot."""
    market_data: MarketData = Field(description="Price / spread snapshot")
    core_indicators: CoreIndicators = Field(description="EMA, RSI, MACD, BB, ATR, VWAP")
    advanced_indicators: AdvancedIndicators = Field(description="All advanced indicators")
    orderbook: OrderBookAnalysis = Field(description="Order book depth & pressure")
    session: SessionInfo = Field(description="Session / kill-zone info")
    market_regime: Literal["trending_up", "trending_down", "ranging", "volatile", "low_volatility"] = Field(
        description="Detected market regime")
    analysis_reasoning: str = Field(description="Reasoning about current conditions")


class Step2MultiTimeframe(BaseModel):
    """STEP 2: Multi-timeframe confluence."""
    mtf_result: MultiTimeframeResult = Field(description="Confluence across 1m/5m/15m/1h")
    htf_bias: Literal["bullish", "bearish", "neutral"] = Field(description="Higher-timeframe directional bias")
    funding_rate: FundingRateData = Field(description="Funding rate context")
    mtf_reasoning: str = Field(description="How timeframes align or conflict")


class Step3SignalDetection(BaseModel):
    """STEP 3: Detect and score signals per strategy."""
    ema_crossover: Literal["bullish", "bearish", "none"] = "none"
    rsi_signal: Literal["oversold", "overbought", "neutral", "oversold_reversal", "overbought_reversal"] = "neutral"
    macd_signal: Literal["bullish", "bearish", "none"] = "none"
    bollinger_signal: Literal["buy", "sell", "none"] = "none"
    orderbook_signal: Literal["buy", "sell", "none"] = "none"
    stoch_rsi_signal: Literal["oversold_reversal", "overbought_reversal", "oversold", "overbought", "neutral"] = "neutral"
    ichimoku_signal: Literal["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"] = "neutral"
    supertrend_signal: Literal["bullish", "bearish", "neutral"] = "neutral"
    divergence_signal: Literal["bullish", "bearish", "none"] = "none"
    squeeze_signal: Literal["squeeze_fire_long", "squeeze_fire_short", "squeeze_building", "no_squeeze"] = "no_squeeze"
    structure_signal: Literal["bullish_bos", "bearish_bos", "none"] = "none"
    order_flow_signal: Literal["strong_buying", "buying", "neutral", "selling", "strong_selling"] = "neutral"
    funding_signal: Literal["fade_longs", "fade_shorts", "neutral"] = "neutral"
    combined_signal: Literal["strong_buy", "buy", "neutral", "sell", "strong_sell"] = "neutral"
    signal_score: float = Field(default=0, description="Numeric signal score -100 to +100")
    signal_reasoning: str = Field(description="Explanation of signal detection")


class Step4StrategySelection(BaseModel):
    """STEP 4: Pick the best strategy for current conditions."""
    strategy: StrategySelection = Field(description="Selected strategy with reasoning")
    position_state: PositionState = Field(description="Current position")
    action: Literal["open_long", "open_short", "close", "partial_close", "hold", "no_action"] = Field(
        description="Recommended action")
    strategy_reasoning: str = Field(description="Full reasoning for strategy and action")


class Step5RiskSizing(BaseModel):
    """STEP 5: Position sizing and risk parameters."""
    risk_assessment: RiskAssessment = Field(description="Size, SL, TP, R:R")
    adaptive_leverage: int = Field(description="Leverage adjusted for volatility")
    dynamic_tp_pct: float = Field(description="Take profit % adjusted for ATR")
    dynamic_sl_pct: float = Field(description="Stop loss % adjusted for ATR")
    partial_tp_levels: List[float] = Field(default_factory=list, description="Price levels for partial take-profits")
    sizing_reasoning: str = Field(description="How size/SL/TP were determined")


class Step6Execution(BaseModel):
    """STEP 6: Execution plan."""
    should_execute: bool = False
    order_type: Literal["market", "limit", "none"] = "none"
    side: Optional[Literal["buy", "sell"]] = None
    size: float = 0
    limit_price: Optional[float] = None
    slippage_tolerance: float = 0.001
    execution_reasoning: str = Field(description="Execution plan details")


class Step7PostTradeReview(BaseModel):
    """STEP 7: Post-trade risk checks and summary."""
    pre_trade_checks: List[str] = Field(description="Risk check results")
    checks_passed: bool = False
    trade_executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    trailing_stop_set: bool = False
    equity_protection_status: EquityProtectionState = Field(default_factory=EquityProtectionState)
    final_summary: str = Field(description="Complete decision summary")


class ScalpingDecisionResponse(BaseModel):
    """Complete 7-step Schema-Guided Reasoning for advanced scalping."""
    timestamp: datetime = Field(default_factory=datetime.now)
    step1_market_analysis: Step1MarketAnalysis
    step2_multi_timeframe: Step2MultiTimeframe
    step3_signal_detection: Step3SignalDetection
    step4_strategy_selection: Step4StrategySelection
    step5_risk_sizing: Step5RiskSizing
    step6_execution: Step6Execution
    step7_post_trade_review: Step7PostTradeReview


# ===========================================================================
# Trade records & agent state
# ===========================================================================

class TradeRecord(BaseModel):
    timestamp: datetime
    side: Literal["buy", "sell"]
    size: float
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    strategy: Optional[STRATEGY_TYPES] = None
    status: Literal["open", "closed", "stopped_out", "take_profit", "trailing_stop", "partial_close"] = "open"
    hold_duration_seconds: Optional[int] = None


class AgentState(BaseModel):
    is_running: bool = False
    active_strategy: Optional[STRATEGY_TYPES] = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0
    best_trade_pnl: float = 0
    worst_trade_pnl: float = 0
    current_position: Optional[PositionState] = None
    recent_trades: List[TradeRecord] = Field(default_factory=list)
    trades_this_hour: int = 0
    last_trade_time: Optional[datetime] = None
    equity_curve: List[float] = Field(default_factory=list)
    daily_pnl: float = 0
    session_start: Optional[datetime] = None
