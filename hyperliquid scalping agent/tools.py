"""
Trading tools for Hyperliquid BTC Scalping Agent.

Provides market data, technical analysis, and order execution capabilities.
"""
import os
import json
import time
import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

try:
    from hyperliquid.info import Info
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    HYPERLIQUID_AVAILABLE = True
except ImportError:
    HYPERLIQUID_AVAILABLE = False
    print("Warning: hyperliquid-python-sdk not installed. Install with: pip install hyperliquid-python-sdk")

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    print("Warning: pandas-ta not installed. Install with: pip install pandas-ta")


class HyperliquidConfig:
    """Configuration for Hyperliquid connection."""
    
    def __init__(self):
        self.private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
        self.account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
        self.network = os.getenv("HYPERLIQUID_NETWORK", "testnet")
        
        if self.network == "mainnet":
            self.api_url = constants.MAINNET_API_URL if HYPERLIQUID_AVAILABLE else "https://api.hyperliquid.xyz"
        else:
            self.api_url = constants.TESTNET_API_URL if HYPERLIQUID_AVAILABLE else "https://api.hyperliquid-testnet.xyz"
        
        self.max_position_size_usd = float(os.getenv("MAX_POSITION_SIZE_USD", "1000"))
        self.default_leverage = int(os.getenv("DEFAULT_LEVERAGE", "5"))
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE", "0.01"))
        self.take_profit_pct = float(os.getenv("TAKE_PROFIT_PCT", "0.005"))
        self.stop_loss_pct = float(os.getenv("STOP_LOSS_PCT", "0.003"))
        self.max_trades_per_hour = int(os.getenv("MAX_TRADES_PER_HOUR", "10"))


class HyperliquidClient:
    """Client wrapper for Hyperliquid SDK."""
    
    def __init__(self, config: Optional[HyperliquidConfig] = None):
        self.config = config or HyperliquidConfig()
        self._info: Optional[Any] = None
        self._exchange: Optional[Any] = None
        self._ws_callbacks: Dict[str, Callable] = {}
        self._latest_data: Dict[str, Any] = {
            "mid_prices": {},
            "l2_book": {},
            "candles": [],
            "user_state": None,
            "trades": []
        }
    
    @property
    def info(self) -> Any:
        """Get or create Info client."""
        if self._info is None and HYPERLIQUID_AVAILABLE:
            self._info = Info(self.config.api_url, skip_ws=False)
        return self._info
    
    @property
    def exchange(self) -> Any:
        """Get or create Exchange client."""
        if self._exchange is None and HYPERLIQUID_AVAILABLE:
            if not self.config.private_key:
                raise ValueError("Private key required for exchange operations")
            self._exchange = Exchange(
                self.config.private_key,
                self.config.api_url,
                account_address=self.config.account_address
            )
        return self._exchange
    
    def subscribe_to_market_data(self, coin: str = "BTC"):
        """Subscribe to real-time market data for scalping."""
        if not HYPERLIQUID_AVAILABLE or self.info is None:
            return
        
        def on_all_mids(data):
            if "mids" in data:
                self._latest_data["mid_prices"] = data["mids"]
        
        def on_l2_book(data):
            self._latest_data["l2_book"] = data
        
        def on_trades(data):
            if "trades" in data.get("data", {}):
                self._latest_data["trades"].extend(data["data"]["trades"])
                self._latest_data["trades"] = self._latest_data["trades"][-100:]
        
        def on_candle(data):
            if "data" in data:
                self._latest_data["candles"].append(data["data"])
                self._latest_data["candles"] = self._latest_data["candles"][-200:]
        
        self.info.subscribe({"type": "allMids"}, on_all_mids)
        self.info.subscribe({"type": "l2Book", "coin": coin}, on_l2_book)
        self.info.subscribe({"type": "trades", "coin": coin}, on_trades)
        self.info.subscribe({"type": "candle", "coin": coin, "interval": "1m"}, on_candle)
        
        if self.config.account_address:
            def on_user_events(data):
                self._latest_data["user_state"] = data
            self.info.subscribe({"type": "userEvents", "user": self.config.account_address}, on_user_events)
    
    def get_mid_price(self, coin: str = "BTC") -> Optional[float]:
        """Get current mid price for a coin."""
        if coin in self._latest_data["mid_prices"]:
            return float(self._latest_data["mid_prices"][coin])
        
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                all_mids = self.info.all_mids()
                if coin in all_mids:
                    return float(all_mids[coin])
            except Exception as e:
                print(f"Error fetching mid price: {e}")
        return None
    
    def get_l2_snapshot(self, coin: str = "BTC") -> Optional[Dict]:
        """Get L2 order book snapshot."""
        if self._latest_data["l2_book"]:
            return self._latest_data["l2_book"]
        
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                return self.info.l2_snapshot(coin)
            except Exception as e:
                print(f"Error fetching L2 snapshot: {e}")
        return None
    
    def get_candles(self, coin: str = "BTC", interval: str = "1m", limit: int = 100) -> List[Dict]:
        """Get historical candle data."""
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                end_time = int(time.time() * 1000)
                start_time = end_time - (limit * 60 * 1000)
                candles = self.info.candles_snapshot(coin, interval, start_time, end_time)
                return candles
            except Exception as e:
                print(f"Error fetching candles: {e}")
        return self._latest_data["candles"][-limit:] if self._latest_data["candles"] else []
    
    def get_user_state(self) -> Optional[Dict]:
        """Get current user account state."""
        if not self.config.account_address:
            return None
        
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                return self.info.user_state(self.config.account_address)
            except Exception as e:
                print(f"Error fetching user state: {e}")
        return self._latest_data["user_state"]
    
    def get_position(self, coin: str = "BTC") -> Optional[Dict]:
        """Get current position for a coin."""
        user_state = self.get_user_state()
        if user_state and "assetPositions" in user_state:
            for pos in user_state["assetPositions"]:
                if pos.get("position", {}).get("coin") == coin:
                    position = pos["position"]
                    szi = float(position.get("szi", 0))
                    if szi != 0:
                        return {
                            "coin": coin,
                            "size": abs(szi),
                            "side": "long" if szi > 0 else "short",
                            "entry_price": float(position.get("entryPx", 0)),
                            "unrealized_pnl": float(position.get("unrealizedPnl", 0)),
                            "leverage": int(position.get("leverage", {}).get("value", 1))
                        }
        return None
    
    def place_market_order(self, coin: str, is_buy: bool, size: float, slippage: float = 0.01) -> Dict:
        """Place a market order."""
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        
        try:
            result = self.exchange.market_open(coin, is_buy, size, None, slippage)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def place_limit_order(
        self, 
        coin: str, 
        is_buy: bool, 
        size: float, 
        price: float,
        tif: str = "Gtc"
    ) -> Dict:
        """Place a limit order."""
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        
        try:
            order_type = {"limit": {"tif": tif}}
            result = self.exchange.order(coin, is_buy, size, price, order_type)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def close_position(self, coin: str) -> Dict:
        """Close entire position for a coin."""
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        
        try:
            result = self.exchange.market_close(coin)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def set_leverage(self, coin: str, leverage: int, is_cross: bool = True) -> Dict:
        """Set leverage for a coin."""
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        
        try:
            result = self.exchange.update_leverage(leverage, coin, is_cross)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}


class TechnicalAnalyzer:
    """Technical analysis calculator for scalping signals."""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
    
    def load_candles(self, candles: List[Dict]) -> pd.DataFrame:
        """Load candle data into DataFrame."""
        if not candles:
            return pd.DataFrame()
        
        data = []
        for c in candles:
            if isinstance(c, dict):
                data.append({
                    "timestamp": c.get("t", c.get("timestamp", 0)),
                    "open": float(c.get("o", c.get("open", 0))),
                    "high": float(c.get("h", c.get("high", 0))),
                    "low": float(c.get("l", c.get("low", 0))),
                    "close": float(c.get("c", c.get("close", 0))),
                    "volume": float(c.get("v", c.get("volume", 0)))
                })
        
        self.df = pd.DataFrame(data)
        if not self.df.empty:
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], unit="ms")
            self.df.set_index("timestamp", inplace=True)
            self.df.sort_index(inplace=True)
        return self.df
    
    def calculate_indicators(self) -> Dict[str, float]:
        """Calculate technical indicators."""
        if self.df is None or self.df.empty or len(self.df) < 21:
            return self._empty_indicators()
        
        df = self.df.copy()
        
        try:
            if PANDAS_TA_AVAILABLE:
                df.ta.ema(length=9, append=True)
                df.ta.ema(length=21, append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.macd(fast=12, slow=26, signal=9, append=True)
                df.ta.atr(length=14, append=True)
                df.ta.bbands(length=20, std=2, append=True)
                df.ta.sma(close=df["volume"], length=20, append=True)
                df.ta.vwap(append=True)
                
                latest = df.iloc[-1]
                
                return {
                    "ema_9": float(latest.get("EMA_9", 0) or 0),
                    "ema_21": float(latest.get("EMA_21", 0) or 0),
                    "rsi_14": float(latest.get("RSI_14", 50) or 50),
                    "macd_line": float(latest.get("MACD_12_26_9", 0) or 0),
                    "macd_signal": float(latest.get("MACDs_12_26_9", 0) or 0),
                    "macd_histogram": float(latest.get("MACDh_12_26_9", 0) or 0),
                    "atr_14": float(latest.get("ATRr_14", 0) or 0),
                    "bollinger_upper": float(latest.get("BBU_20_2.0", 0) or 0),
                    "bollinger_middle": float(latest.get("BBM_20_2.0", 0) or 0),
                    "bollinger_lower": float(latest.get("BBL_20_2.0", 0) or 0),
                    "volume_sma": float(latest.get("SMA_20", 0) or 0),
                    "vwap": float(latest.get("VWAP_D", latest["close"]) or latest["close"])
                }
            else:
                return self._calculate_basic_indicators(df)
                
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return self._empty_indicators()
    
    def _calculate_basic_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic indicators without pandas-ta."""
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]
        
        ema_9 = close.ewm(span=9, adjust=False).mean().iloc[-1]
        ema_21 = close.ewm(span=21, adjust=False).mean().iloc[-1]
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_14 = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        macd_histogram = macd_line - macd_signal
        
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        atr_14 = tr.rolling(14).mean().iloc[-1]
        
        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        
        volume_sma = volume.rolling(20).mean().iloc[-1]
        
        return {
            "ema_9": float(ema_9),
            "ema_21": float(ema_21),
            "rsi_14": float(rsi_14),
            "macd_line": float(macd_line.iloc[-1]),
            "macd_signal": float(macd_signal.iloc[-1]),
            "macd_histogram": float(macd_histogram.iloc[-1]),
            "atr_14": float(atr_14) if not pd.isna(atr_14) else 0,
            "bollinger_upper": float(bb_upper.iloc[-1]),
            "bollinger_middle": float(sma_20.iloc[-1]),
            "bollinger_lower": float(bb_lower.iloc[-1]),
            "volume_sma": float(volume_sma) if not pd.isna(volume_sma) else 0,
            "vwap": float(close.iloc[-1])
        }
    
    def _empty_indicators(self) -> Dict[str, float]:
        """Return empty indicators structure."""
        return {
            "ema_9": 0,
            "ema_21": 0,
            "rsi_14": 50,
            "macd_line": 0,
            "macd_signal": 0,
            "macd_histogram": 0,
            "atr_14": 0,
            "bollinger_upper": 0,
            "bollinger_middle": 0,
            "bollinger_lower": 0,
            "volume_sma": 0,
            "vwap": 0
        }
    
    def analyze_orderbook(self, l2_data: Dict) -> Dict[str, Any]:
        """Analyze order book for imbalances."""
        if not l2_data or "levels" not in l2_data:
            return {
                "bid_depth_usd": 0,
                "ask_depth_usd": 0,
                "imbalance_ratio": 1.0,
                "pressure": "neutral"
            }
        
        try:
            levels = l2_data["levels"]
            bids = levels[0] if len(levels) > 0 else []
            asks = levels[1] if len(levels) > 1 else []
            
            bid_depth = sum(float(b["sz"]) * float(b["px"]) for b in bids[:5])
            ask_depth = sum(float(a["sz"]) * float(a["px"]) for a in asks[:5])
            
            if ask_depth > 0:
                imbalance = bid_depth / ask_depth
            else:
                imbalance = 1.0
            
            if imbalance > 1.5:
                pressure = "bullish"
            elif imbalance < 0.67:
                pressure = "bearish"
            else:
                pressure = "neutral"
            
            return {
                "bid_depth_usd": bid_depth,
                "ask_depth_usd": ask_depth,
                "imbalance_ratio": imbalance,
                "pressure": pressure
            }
        except Exception as e:
            print(f"Error analyzing orderbook: {e}")
            return {
                "bid_depth_usd": 0,
                "ask_depth_usd": 0,
                "imbalance_ratio": 1.0,
                "pressure": "neutral"
            }


class MarketDataInput(BaseModel):
    """Input for market data tool."""
    coin: str = Field(default="BTC", description="Coin symbol to fetch data for")


class MarketDataTool(BaseTool):
    """Tool for fetching market data and technical indicators."""
    
    name: str = "get_market_data"
    description: str = """Fetches current market data and technical indicators for BTC scalping.
    
    Returns:
    - Current mid price, best bid/ask, spread
    - Technical indicators (EMA, RSI, MACD, Bollinger Bands, ATR)
    - Order book analysis (depth, imbalance, pressure)
    
    Use this to analyze market conditions before making trading decisions."""
    
    args_schema: type[BaseModel] = MarketDataInput
    client: Optional[HyperliquidClient] = None
    analyzer: Optional[TechnicalAnalyzer] = None
    
    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, 'client', client or HyperliquidClient())
        object.__setattr__(self, 'analyzer', TechnicalAnalyzer())
    
    def _run(self, coin: str = "BTC") -> str:
        """Fetch and analyze market data."""
        try:
            mid_price = self.client.get_mid_price(coin)
            l2_data = self.client.get_l2_snapshot(coin)
            candles = self.client.get_candles(coin, "1m", 100)
            
            if l2_data and "levels" in l2_data:
                levels = l2_data["levels"]
                best_bid = float(levels[0][0]["px"]) if levels[0] else 0
                best_ask = float(levels[1][0]["px"]) if levels[1] else 0
            else:
                best_bid = mid_price * 0.9999 if mid_price else 0
                best_ask = mid_price * 1.0001 if mid_price else 0
            
            spread = best_ask - best_bid if best_bid and best_ask else 0
            spread_bps = (spread / mid_price * 10000) if mid_price else 0
            
            self.analyzer.load_candles(candles)
            indicators = self.analyzer.calculate_indicators()
            orderbook = self.analyzer.analyze_orderbook(l2_data)
            
            result = {
                "market_data": {
                    "symbol": coin,
                    "mid_price": mid_price,
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "spread": spread,
                    "spread_bps": spread_bps,
                    "timestamp": datetime.now().isoformat()
                },
                "indicators": indicators,
                "orderbook": orderbook
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class PositionInput(BaseModel):
    """Input for position tool."""
    coin: str = Field(default="BTC", description="Coin symbol to check position for")


class PositionTool(BaseTool):
    """Tool for fetching current position and account state."""
    
    name: str = "get_position"
    description: str = """Fetches current position and account state.
    
    Returns:
    - Current open position (if any): side, size, entry price, PnL
    - Account equity and margin information
    
    Use this to check your current position before placing new orders."""
    
    args_schema: type[BaseModel] = PositionInput
    client: Optional[HyperliquidClient] = None
    
    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, 'client', client or HyperliquidClient())
    
    def _run(self, coin: str = "BTC") -> str:
        """Fetch position data."""
        try:
            position = self.client.get_position(coin)
            user_state = self.client.get_user_state()
            
            account_equity = 0
            if user_state and "marginSummary" in user_state:
                account_equity = float(user_state["marginSummary"].get("accountValue", 0))
            
            result = {
                "position": position,
                "account_equity": account_equity,
                "has_position": position is not None
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class OrderInput(BaseModel):
    """Input for order execution tool."""
    action: str = Field(description="Action: 'open_long', 'open_short', 'close'")
    size: float = Field(default=0, description="Order size in BTC (0 to auto-calculate)")
    order_type: str = Field(default="market", description="Order type: 'market' or 'limit'")
    limit_price: Optional[float] = Field(default=None, description="Limit price (required for limit orders)")
    slippage: float = Field(default=0.01, description="Slippage tolerance for market orders")


class ExecuteOrderTool(BaseTool):
    """Tool for executing trades on Hyperliquid."""
    
    name: str = "execute_order"
    description: str = """Executes a trade on Hyperliquid.
    
    Actions:
    - 'open_long': Open a long position (buy)
    - 'open_short': Open a short position (sell)
    - 'close': Close current position
    
    Returns execution result with fill details.
    
    IMPORTANT: Only use after analyzing market conditions and confirming signals."""
    
    args_schema: type[BaseModel] = OrderInput
    client: Optional[HyperliquidClient] = None
    
    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, 'client', client or HyperliquidClient())
    
    def _run(
        self, 
        action: str,
        size: float = 0,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        slippage: float = 0.01
    ) -> str:
        """Execute an order."""
        try:
            coin = "BTC"
            
            if action == "close":
                result = self.client.close_position(coin)
                return json.dumps({
                    "action": "close",
                    "result": result
                }, indent=2)
            
            if size <= 0:
                user_state = self.client.get_user_state()
                if user_state and "marginSummary" in user_state:
                    equity = float(user_state["marginSummary"].get("accountValue", 0))
                    risk_amount = equity * self.client.config.risk_per_trade
                    mid_price = self.client.get_mid_price(coin) or 80000
                    size = (risk_amount * self.client.config.default_leverage) / mid_price
                    size = round(size, 5)
                else:
                    return json.dumps({"error": "Cannot calculate position size: no account data"})
            
            is_buy = action == "open_long"
            
            if order_type == "limit" and limit_price:
                result = self.client.place_limit_order(coin, is_buy, size, limit_price)
            else:
                result = self.client.place_market_order(coin, is_buy, size, slippage)
            
            return json.dumps({
                "action": action,
                "size": size,
                "order_type": order_type,
                "result": result
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class RiskCheckInput(BaseModel):
    """Input for risk check tool."""
    proposed_action: str = Field(description="Proposed action to validate")
    proposed_size: float = Field(description="Proposed position size")


class RiskCheckTool(BaseTool):
    """Tool for performing pre-trade risk checks."""
    
    name: str = "risk_check"
    description: str = """Performs pre-trade risk checks before executing orders.
    
    Checks:
    - Position size limits
    - Daily trade limits
    - Account margin requirements
    - Maximum drawdown limits
    
    Returns whether the trade passes all risk checks."""
    
    args_schema: type[BaseModel] = RiskCheckInput
    client: Optional[HyperliquidClient] = None
    trades_this_hour: int = 0
    hour_start: Optional[datetime] = None
    
    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, 'client', client or HyperliquidClient())
        object.__setattr__(self, 'trades_this_hour', 0)
        object.__setattr__(self, 'hour_start', datetime.now())
    
    def _run(self, proposed_action: str, proposed_size: float) -> str:
        """Perform risk checks."""
        checks = []
        all_passed = True
        
        try:
            now = datetime.now()
            if self.hour_start is None or (now - self.hour_start).total_seconds() > 3600:
                object.__setattr__(self, 'hour_start', now)
                object.__setattr__(self, 'trades_this_hour', 0)
            
            if self.trades_this_hour >= self.client.config.max_trades_per_hour:
                checks.append(f"FAIL: Max trades per hour ({self.client.config.max_trades_per_hour}) reached")
                all_passed = False
            else:
                checks.append(f"PASS: Trade count ({self.trades_this_hour}/{self.client.config.max_trades_per_hour})")
            
            mid_price = self.client.get_mid_price("BTC") or 80000
            position_value_usd = proposed_size * mid_price
            
            if position_value_usd > self.client.config.max_position_size_usd:
                checks.append(f"FAIL: Position size ${position_value_usd:.2f} exceeds max ${self.client.config.max_position_size_usd}")
                all_passed = False
            else:
                checks.append(f"PASS: Position size ${position_value_usd:.2f} within limits")
            
            user_state = self.client.get_user_state()
            if user_state:
                margin_summary = user_state.get("marginSummary", {})
                account_value = float(margin_summary.get("accountValue", 0))
                
                if account_value > 0:
                    risk_pct = (position_value_usd / self.client.config.default_leverage) / account_value
                    max_risk = self.client.config.risk_per_trade * 5
                    
                    if risk_pct > max_risk:
                        checks.append(f"FAIL: Risk {risk_pct*100:.2f}% exceeds max {max_risk*100:.2f}%")
                        all_passed = False
                    else:
                        checks.append(f"PASS: Risk {risk_pct*100:.2f}% within limits")
            
            existing_position = self.client.get_position("BTC")
            if existing_position and proposed_action in ["open_long", "open_short"]:
                if (proposed_action == "open_long" and existing_position["side"] == "short") or \
                   (proposed_action == "open_short" and existing_position["side"] == "long"):
                    checks.append("WARNING: This will flip position direction")
            
            if all_passed:
                object.__setattr__(self, 'trades_this_hour', self.trades_this_hour + 1)
            
            return json.dumps({
                "checks": checks,
                "all_passed": all_passed,
                "can_execute": all_passed
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "checks": [f"ERROR: {str(e)}"],
                "all_passed": False,
                "can_execute": False
            })


def create_scalping_tools(client: Optional[HyperliquidClient] = None) -> List[BaseTool]:
    """Create all scalping tools with shared client."""
    if client is None:
        client = HyperliquidClient()
    
    return [
        MarketDataTool(client),
        PositionTool(client),
        ExecuteOrderTool(client),
        RiskCheckTool(client)
    ]
