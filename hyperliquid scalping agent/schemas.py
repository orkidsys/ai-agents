"""
Schema-Guided Reasoning (SGR) schemas for Hyperliquid BTC Scalping Agent.

This implements a structured reasoning process for scalping decisions.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class MarketData(BaseModel):
    """Current market data snapshot."""
    symbol: str = Field(default="BTC", description="Trading symbol")
    mid_price: float = Field(description="Current mid-market price")
    best_bid: float = Field(description="Best bid price")
    best_ask: float = Field(description="Best ask price")
    spread: float = Field(description="Bid-ask spread")
    spread_bps: float = Field(description="Spread in basis points")
    timestamp: datetime = Field(description="Data timestamp")


class TechnicalIndicators(BaseModel):
    """Technical indicators for analysis."""
    ema_9: float = Field(description="9-period EMA")
    ema_21: float = Field(description="21-period EMA")
    rsi_14: float = Field(description="14-period RSI")
    macd_line: float = Field(description="MACD line value")
    macd_signal: float = Field(description="MACD signal line")
    macd_histogram: float = Field(description="MACD histogram")
    atr_14: float = Field(description="14-period ATR for volatility")
    volume_sma: float = Field(description="Volume SMA")
    bollinger_upper: float = Field(description="Upper Bollinger Band")
    bollinger_middle: float = Field(description="Middle Bollinger Band (SMA 20)")
    bollinger_lower: float = Field(description="Lower Bollinger Band")
    vwap: Optional[float] = Field(default=None, description="Volume Weighted Average Price")


class OrderBookAnalysis(BaseModel):
    """Order book depth analysis."""
    bid_depth_usd: float = Field(description="Total bid depth in USD (top 5 levels)")
    ask_depth_usd: float = Field(description="Total ask depth in USD (top 5 levels)")
    imbalance_ratio: float = Field(description="Order book imbalance ratio (bid/ask)")
    pressure: Literal["bullish", "bearish", "neutral"] = Field(
        description="Order book pressure direction"
    )


class PositionState(BaseModel):
    """Current position state."""
    has_position: bool = Field(description="Whether there's an open position")
    side: Optional[Literal["long", "short"]] = Field(default=None, description="Position side")
    size: float = Field(default=0, description="Position size in BTC")
    entry_price: Optional[float] = Field(default=None, description="Entry price")
    unrealized_pnl: float = Field(default=0, description="Unrealized PnL in USD")
    leverage: int = Field(default=1, description="Current leverage")


class RiskAssessment(BaseModel):
    """Risk parameters for the trade."""
    account_equity: float = Field(description="Account equity in USD")
    risk_amount: float = Field(description="Max risk amount for this trade in USD")
    position_size_btc: float = Field(description="Calculated position size in BTC")
    stop_loss_price: Optional[float] = Field(default=None, description="Stop loss price")
    take_profit_price: Optional[float] = Field(default=None, description="Take profit price")
    risk_reward_ratio: Optional[float] = Field(default=None, description="Risk/Reward ratio")


class Step1MarketAnalysis(BaseModel):
    """STEP 1: Analyze current market conditions."""
    market_data: MarketData = Field(description="Current market snapshot")
    indicators: TechnicalIndicators = Field(description="Technical indicators")
    orderbook: OrderBookAnalysis = Field(description="Order book analysis")
    market_regime: Literal["trending_up", "trending_down", "ranging", "volatile"] = Field(
        description="Current market regime"
    )
    analysis_reasoning: str = Field(
        description="Detailed reasoning about market conditions"
    )


class Step2SignalDetection(BaseModel):
    """STEP 2: Detect trading signals."""
    ema_crossover: Literal["bullish", "bearish", "none"] = Field(
        description="EMA crossover signal"
    )
    rsi_signal: Literal["oversold", "overbought", "neutral"] = Field(
        description="RSI-based signal"
    )
    macd_signal: Literal["bullish", "bearish", "none"] = Field(
        description="MACD crossover signal"
    )
    bollinger_signal: Literal["buy", "sell", "none"] = Field(
        description="Bollinger Band signal"
    )
    orderbook_signal: Literal["buy", "sell", "none"] = Field(
        description="Order book imbalance signal"
    )
    combined_signal: Literal["strong_buy", "buy", "neutral", "sell", "strong_sell"] = Field(
        description="Combined signal strength"
    )
    signal_reasoning: str = Field(
        description="Explanation of signal detection logic"
    )


class Step3PositionManagement(BaseModel):
    """STEP 3: Manage existing position or prepare new entry."""
    current_position: PositionState = Field(description="Current position state")
    action: Literal["open_long", "open_short", "close", "hold", "no_action"] = Field(
        description="Recommended action"
    )
    risk_assessment: RiskAssessment = Field(description="Risk parameters")
    position_reasoning: str = Field(
        description="Reasoning for position management decision"
    )


class Step4ExecutionPlan(BaseModel):
    """STEP 4: Create execution plan."""
    should_execute: bool = Field(description="Whether to execute the trade")
    order_type: Literal["market", "limit", "none"] = Field(description="Order type to use")
    side: Optional[Literal["buy", "sell"]] = Field(default=None, description="Order side")
    size: float = Field(default=0, description="Order size in BTC")
    limit_price: Optional[float] = Field(default=None, description="Limit price if applicable")
    slippage_tolerance: float = Field(default=0.001, description="Slippage tolerance (0.1%)")
    execution_reasoning: str = Field(
        description="Detailed execution plan explanation"
    )


class Step5RiskManagement(BaseModel):
    """STEP 5: Final risk checks and trade execution summary."""
    pre_trade_checks: List[str] = Field(
        description="List of pre-trade risk checks performed"
    )
    checks_passed: bool = Field(description="Whether all risk checks passed")
    trade_executed: bool = Field(description="Whether trade was executed")
    execution_result: Optional[dict] = Field(
        default=None, 
        description="Execution result from exchange"
    )
    final_summary: str = Field(
        description="Summary of the scalping decision and outcome"
    )


class ScalpingDecisionResponse(BaseModel):
    """Complete 5-step Schema-Guided Reasoning response for scalping decisions."""
    timestamp: datetime = Field(default_factory=datetime.now, description="Decision timestamp")
    step1_market_analysis: Step1MarketAnalysis = Field(
        description="STEP 1: Market condition analysis"
    )
    step2_signal_detection: Step2SignalDetection = Field(
        description="STEP 2: Trading signal detection"
    )
    step3_position_management: Step3PositionManagement = Field(
        description="STEP 3: Position and risk management"
    )
    step4_execution_plan: Step4ExecutionPlan = Field(
        description="STEP 4: Trade execution plan"
    )
    step5_risk_management: Step5RiskManagement = Field(
        description="STEP 5: Final risk checks and execution"
    )


class TradeRecord(BaseModel):
    """Record of executed trade."""
    timestamp: datetime = Field(description="Trade execution time")
    side: Literal["buy", "sell"] = Field(description="Trade side")
    size: float = Field(description="Trade size in BTC")
    entry_price: float = Field(description="Entry price")
    exit_price: Optional[float] = Field(default=None, description="Exit price if closed")
    pnl: Optional[float] = Field(default=None, description="Realized PnL")
    status: Literal["open", "closed", "stopped_out", "take_profit"] = Field(
        description="Trade status"
    )


class AgentState(BaseModel):
    """Overall agent state."""
    is_running: bool = Field(default=False, description="Whether agent is running")
    total_trades: int = Field(default=0, description="Total trades executed")
    winning_trades: int = Field(default=0, description="Number of winning trades")
    losing_trades: int = Field(default=0, description="Number of losing trades")
    total_pnl: float = Field(default=0, description="Total realized PnL")
    current_position: Optional[PositionState] = Field(
        default=None, 
        description="Current open position"
    )
    recent_trades: List[TradeRecord] = Field(
        default_factory=list,
        description="Recent trade history"
    )
    trades_this_hour: int = Field(default=0, description="Trades executed this hour")
    last_trade_time: Optional[datetime] = Field(
        default=None, 
        description="Time of last trade"
    )
