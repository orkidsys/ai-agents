"""
Trading tools for Hyperliquid BTC Scalping Agent.

Provides market data, technical analysis, order execution, multi-timeframe
analysis, funding rate tracking, volatility regime detection, and
advanced order flow capabilities.
"""
import os
import json
import time
import math
import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Any, Callable, Tuple
from datetime import datetime, timedelta
from collections import deque
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


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

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
        self.max_daily_drawdown_pct = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "0.05"))
        self.trailing_stop_activation_pct = float(os.getenv("TRAILING_STOP_ACTIVATION_PCT", "0.003"))
        self.trailing_stop_distance_pct = float(os.getenv("TRAILING_STOP_DISTANCE_PCT", "0.002"))


# ---------------------------------------------------------------------------
# Hyperliquid client
# ---------------------------------------------------------------------------

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
            "trades": [],
            "funding_rates": {},
        }

    @property
    def info(self) -> Any:
        if self._info is None and HYPERLIQUID_AVAILABLE:
            self._info = Info(self.config.api_url, skip_ws=False)
        return self._info

    @property
    def exchange(self) -> Any:
        if self._exchange is None and HYPERLIQUID_AVAILABLE:
            if not self.config.private_key:
                raise ValueError("Private key required for exchange operations")
            self._exchange = Exchange(
                self.config.private_key,
                self.config.api_url,
                account_address=self.config.account_address,
            )
        return self._exchange

    # -- WebSocket subscriptions --

    def subscribe_to_market_data(self, coin: str = "BTC"):
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
                self._latest_data["trades"] = self._latest_data["trades"][-500:]

        def on_candle(data):
            if "data" in data:
                self._latest_data["candles"].append(data["data"])
                self._latest_data["candles"] = self._latest_data["candles"][-500:]

        self.info.subscribe({"type": "allMids"}, on_all_mids)
        self.info.subscribe({"type": "l2Book", "coin": coin}, on_l2_book)
        self.info.subscribe({"type": "trades", "coin": coin}, on_trades)
        self.info.subscribe({"type": "candle", "coin": coin, "interval": "1m"}, on_candle)

        if self.config.account_address:
            def on_user_events(data):
                self._latest_data["user_state"] = data
            self.info.subscribe({"type": "userEvents", "user": self.config.account_address}, on_user_events)

    # -- Data fetchers --

    def get_mid_price(self, coin: str = "BTC") -> Optional[float]:
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
        if self._latest_data["l2_book"]:
            return self._latest_data["l2_book"]
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                return self.info.l2_snapshot(coin)
            except Exception as e:
                print(f"Error fetching L2 snapshot: {e}")
        return None

    def get_candles(self, coin: str = "BTC", interval: str = "1m", limit: int = 100) -> List[Dict]:
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                end_time = int(time.time() * 1000)
                interval_ms_map = {
                    "1m": 60_000, "3m": 180_000, "5m": 300_000,
                    "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000,
                    "4h": 14_400_000, "1d": 86_400_000,
                }
                ms_per = interval_ms_map.get(interval, 60_000)
                start_time = end_time - (limit * ms_per)
                return self.info.candles_snapshot(coin, interval, start_time, end_time)
            except Exception as e:
                print(f"Error fetching candles: {e}")
        return self._latest_data["candles"][-limit:] if self._latest_data["candles"] else []

    def get_user_state(self) -> Optional[Dict]:
        if not self.config.account_address:
            return None
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                return self.info.user_state(self.config.account_address)
            except Exception as e:
                print(f"Error fetching user state: {e}")
        return self._latest_data["user_state"]

    def get_position(self, coin: str = "BTC") -> Optional[Dict]:
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
                            "leverage": int(position.get("leverage", {}).get("value", 1)),
                        }
        return None

    def get_funding_rate(self, coin: str = "BTC") -> Optional[Dict]:
        """Get current and predicted funding rate."""
        if HYPERLIQUID_AVAILABLE and self.info:
            try:
                meta = self.info.meta_and_asset_ctxs()
                if meta and len(meta) > 1:
                    asset_ctxs = meta[1]
                    universe = meta[0].get("universe", [])
                    for i, asset in enumerate(universe):
                        if asset.get("name") == coin and i < len(asset_ctxs):
                            ctx = asset_ctxs[i]
                            return {
                                "coin": coin,
                                "funding_rate": float(ctx.get("funding", 0)),
                                "open_interest": float(ctx.get("openInterest", 0)),
                                "premium": float(ctx.get("premium", 0)),
                                "oracle_price": float(ctx.get("oraclePrice", 0)),
                                "mark_price": float(ctx.get("markPx", 0)),
                            }
            except Exception as e:
                print(f"Error fetching funding rate: {e}")
        return None

    def get_recent_trades(self, coin: str = "BTC") -> List[Dict]:
        return self._latest_data["trades"][-100:]

    # -- Order execution --

    def place_market_order(self, coin: str, is_buy: bool, size: float, slippage: float = 0.01) -> Dict:
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        try:
            return self.exchange.market_open(coin, is_buy, size, None, slippage)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def place_limit_order(self, coin: str, is_buy: bool, size: float, price: float, tif: str = "Gtc") -> Dict:
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        try:
            return self.exchange.order(coin, is_buy, size, price, {"limit": {"tif": tif}})
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def close_position(self, coin: str) -> Dict:
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        try:
            return self.exchange.market_close(coin)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def set_leverage(self, coin: str, leverage: int, is_cross: bool = True) -> Dict:
        if not HYPERLIQUID_AVAILABLE or not self.exchange:
            return {"status": "error", "error": "Exchange not available"}
        try:
            return self.exchange.update_leverage(leverage, coin, is_cross)
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Technical analysis engine
# ---------------------------------------------------------------------------

class TechnicalAnalyzer:
    """Comprehensive technical analysis engine with advanced indicators."""

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None

    def load_candles(self, candles: List[Dict]) -> pd.DataFrame:
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
                    "volume": float(c.get("v", c.get("volume", 0))),
                })
        self.df = pd.DataFrame(data)
        if not self.df.empty:
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], unit="ms")
            self.df.set_index("timestamp", inplace=True)
            self.df.sort_index(inplace=True)
        return self.df

    # ---- Core indicators ----

    def calculate_indicators(self) -> Dict[str, float]:
        if self.df is None or self.df.empty or len(self.df) < 26:
            return self._empty_indicators()
        df = self.df.copy()
        try:
            if PANDAS_TA_AVAILABLE:
                return self._calc_with_pandas_ta(df)
            return self._calculate_basic_indicators(df)
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return self._empty_indicators()

    def _calc_with_pandas_ta(self, df: pd.DataFrame) -> Dict[str, float]:
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
            "vwap": float(latest.get("VWAP_D", latest["close"]) or latest["close"]),
        }

    def _calculate_basic_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        close, high, low, volume = df["close"], df["high"], df["low"], df["volume"]

        ema_9 = close.ewm(span=9, adjust=False).mean().iloc[-1]
        ema_21 = close.ewm(span=21, adjust=False).mean().iloc[-1]

        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_14 = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        macd_histogram = macd_line - macd_signal

        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr_14 = tr.rolling(14).mean().iloc[-1]

        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)

        volume_sma = volume.rolling(20).mean().iloc[-1]

        return {
            "ema_9": float(ema_9), "ema_21": float(ema_21),
            "rsi_14": float(rsi_14),
            "macd_line": float(macd_line.iloc[-1]),
            "macd_signal": float(macd_signal.iloc[-1]),
            "macd_histogram": float(macd_histogram.iloc[-1]),
            "atr_14": float(atr_14) if not pd.isna(atr_14) else 0,
            "bollinger_upper": float(bb_upper.iloc[-1]),
            "bollinger_middle": float(sma_20.iloc[-1]),
            "bollinger_lower": float(bb_lower.iloc[-1]),
            "volume_sma": float(volume_sma) if not pd.isna(volume_sma) else 0,
            "vwap": float(close.iloc[-1]),
        }

    # ---- Advanced indicators ----

    def calculate_ichimoku(self) -> Dict[str, float]:
        """Ichimoku Cloud (Tenkan, Kijun, Senkou A/B, Chikou)."""
        if self.df is None or len(self.df) < 52:
            return {"tenkan": 0, "kijun": 0, "senkou_a": 0, "senkou_b": 0, "chikou": 0, "cloud_signal": "neutral"}
        df = self.df
        high, low, close = df["high"], df["low"], df["close"]

        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        chikou = close.shift(-26)

        t, k = float(tenkan.iloc[-1]), float(kijun.iloc[-1])
        sa = float(senkou_a.iloc[-1]) if not pd.isna(senkou_a.iloc[-1]) else 0
        sb = float(senkou_b.iloc[-1]) if not pd.isna(senkou_b.iloc[-1]) else 0
        ch = float(chikou.iloc[-27]) if len(chikou) > 27 and not pd.isna(chikou.iloc[-27]) else 0
        price = float(close.iloc[-1])

        cloud_top = max(sa, sb)
        cloud_bottom = min(sa, sb)

        if price > cloud_top and t > k:
            signal = "strong_bullish"
        elif price > cloud_top:
            signal = "bullish"
        elif price < cloud_bottom and t < k:
            signal = "strong_bearish"
        elif price < cloud_bottom:
            signal = "bearish"
        else:
            signal = "neutral"

        return {"tenkan": t, "kijun": k, "senkou_a": sa, "senkou_b": sb, "chikou": ch, "cloud_signal": signal}

    def calculate_stochastic_rsi(self, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Dict[str, float]:
        """Stochastic RSI oscillator."""
        if self.df is None or len(self.df) < period + smooth_k + smooth_d:
            return {"stoch_rsi_k": 50, "stoch_rsi_d": 50, "stoch_rsi_signal": "neutral"}
        close = self.df["close"]
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rsi = 100 - (100 / (1 + gain / loss))

        rsi_min = rsi.rolling(period).min()
        rsi_max = rsi.rolling(period).max()
        stoch_rsi = ((rsi - rsi_min) / (rsi_max - rsi_min)) * 100
        k_line = stoch_rsi.rolling(smooth_k).mean()
        d_line = k_line.rolling(smooth_d).mean()

        k_val = float(k_line.iloc[-1]) if not pd.isna(k_line.iloc[-1]) else 50
        d_val = float(d_line.iloc[-1]) if not pd.isna(d_line.iloc[-1]) else 50

        if k_val < 20 and k_val > d_val:
            sig = "oversold_reversal"
        elif k_val > 80 and k_val < d_val:
            sig = "overbought_reversal"
        elif k_val < 20:
            sig = "oversold"
        elif k_val > 80:
            sig = "overbought"
        else:
            sig = "neutral"

        return {"stoch_rsi_k": k_val, "stoch_rsi_d": d_val, "stoch_rsi_signal": sig}

    def calculate_adx(self, period: int = 14) -> Dict[str, float]:
        """Average Directional Index – trend strength."""
        if self.df is None or len(self.df) < period * 2:
            return {"adx": 0, "plus_di": 0, "minus_di": 0, "trend_strength": "none"}
        high, low, close = self.df["high"], self.df["low"], self.df["close"]

        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()

        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(span=period, adjust=False).mean()

        adx_val = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0
        pdi = float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 0
        mdi = float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 0

        if adx_val < 20:
            strength = "weak"
        elif adx_val < 40:
            strength = "moderate"
        elif adx_val < 60:
            strength = "strong"
        else:
            strength = "very_strong"

        return {"adx": adx_val, "plus_di": pdi, "minus_di": mdi, "trend_strength": strength}

    def calculate_obv(self) -> Dict[str, float]:
        """On-Balance Volume with divergence detection."""
        if self.df is None or len(self.df) < 20:
            return {"obv": 0, "obv_ema": 0, "obv_divergence": "none"}
        close, volume = self.df["close"], self.df["volume"]

        direction = np.sign(close.diff())
        obv = (volume * direction).cumsum()
        obv_ema = obv.ewm(span=20, adjust=False).mean()

        obv_val = float(obv.iloc[-1])
        obv_ema_val = float(obv_ema.iloc[-1])

        price_up = close.iloc[-1] > close.iloc[-5]
        obv_up = obv.iloc[-1] > obv.iloc[-5]

        if price_up and not obv_up:
            div = "bearish_divergence"
        elif not price_up and obv_up:
            div = "bullish_divergence"
        else:
            div = "none"

        return {"obv": obv_val, "obv_ema": obv_ema_val, "obv_divergence": div}

    def calculate_supertrend(self, period: int = 10, multiplier: float = 3.0) -> Dict[str, Any]:
        """Supertrend indicator for trend-following."""
        if self.df is None or len(self.df) < period + 1:
            return {"supertrend": 0, "supertrend_direction": "neutral"}
        high, low, close = self.df["high"], self.df["low"], self.df["close"]
        hl2 = (high + low) / 2

        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)

        supertrend = pd.Series(0.0, index=self.df.index)
        direction = pd.Series(1, index=self.df.index)

        for i in range(period, len(self.df)):
            if close.iloc[i] > upper_band.iloc[i - 1]:
                direction.iloc[i] = 1
            elif close.iloc[i] < lower_band.iloc[i - 1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i - 1]

            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]

        st_val = float(supertrend.iloc[-1])
        st_dir = "bullish" if direction.iloc[-1] == 1 else "bearish"
        return {"supertrend": st_val, "supertrend_direction": st_dir}

    def calculate_pivot_points(self) -> Dict[str, float]:
        """Classic pivot points from the last completed candle."""
        if self.df is None or len(self.df) < 2:
            return {"pivot": 0, "r1": 0, "r2": 0, "r3": 0, "s1": 0, "s2": 0, "s3": 0}
        prev = self.df.iloc[-2]
        h, l, c = float(prev["high"]), float(prev["low"]), float(prev["close"])
        pivot = (h + l + c) / 3
        r1, s1 = 2 * pivot - l, 2 * pivot - h
        r2, s2 = pivot + (h - l), pivot - (h - l)
        r3, s3 = h + 2 * (pivot - l), l - 2 * (h - pivot)
        return {"pivot": pivot, "r1": r1, "r2": r2, "r3": r3, "s1": s1, "s2": s2, "s3": s3}

    def calculate_fibonacci_levels(self) -> Dict[str, float]:
        """Fibonacci retracement levels from swing high/low of last N candles."""
        if self.df is None or len(self.df) < 30:
            return {"fib_0": 0, "fib_236": 0, "fib_382": 0, "fib_500": 0, "fib_618": 0, "fib_786": 0, "fib_100": 0, "fib_trend": "neutral"}
        window = self.df.tail(50)
        swing_high = float(window["high"].max())
        swing_low = float(window["low"].min())
        diff = swing_high - swing_low
        price = float(self.df["close"].iloc[-1])
        is_uptrend = self.df["close"].iloc[-1] > self.df["close"].iloc[-30]

        if is_uptrend:
            fib = {
                "fib_0": swing_high, "fib_236": swing_high - 0.236 * diff,
                "fib_382": swing_high - 0.382 * diff, "fib_500": swing_high - 0.5 * diff,
                "fib_618": swing_high - 0.618 * diff, "fib_786": swing_high - 0.786 * diff,
                "fib_100": swing_low, "fib_trend": "uptrend",
            }
        else:
            fib = {
                "fib_0": swing_low, "fib_236": swing_low + 0.236 * diff,
                "fib_382": swing_low + 0.382 * diff, "fib_500": swing_low + 0.5 * diff,
                "fib_618": swing_low + 0.618 * diff, "fib_786": swing_low + 0.786 * diff,
                "fib_100": swing_high, "fib_trend": "downtrend",
            }

        nearest_fib = None
        min_dist = float("inf")
        for key, val in fib.items():
            if key.startswith("fib_") and key != "fib_trend":
                dist = abs(price - val)
                if dist < min_dist:
                    min_dist = dist
                    nearest_fib = key
        fib["nearest_level"] = nearest_fib
        fib["distance_to_nearest"] = min_dist
        return fib

    def calculate_cmf(self, period: int = 20) -> Dict[str, float]:
        """Chaikin Money Flow – accumulation/distribution pressure."""
        if self.df is None or len(self.df) < period:
            return {"cmf": 0, "cmf_signal": "neutral"}
        high, low, close, volume = self.df["high"], self.df["low"], self.df["close"], self.df["volume"]

        mfm = ((close - low) - (high - close)) / (high - low).replace(0, 1)
        mfv = mfm * volume
        cmf = mfv.rolling(period).sum() / volume.rolling(period).sum()
        cmf_val = float(cmf.iloc[-1]) if not pd.isna(cmf.iloc[-1]) else 0

        if cmf_val > 0.1:
            sig = "strong_accumulation"
        elif cmf_val > 0.05:
            sig = "accumulation"
        elif cmf_val < -0.1:
            sig = "strong_distribution"
        elif cmf_val < -0.05:
            sig = "distribution"
        else:
            sig = "neutral"

        return {"cmf": cmf_val, "cmf_signal": sig}

    def calculate_heikin_ashi(self) -> Dict[str, Any]:
        """Heikin-Ashi candles for noise-filtered trend reading."""
        if self.df is None or len(self.df) < 5:
            return {"ha_trend": "neutral", "ha_streak": 0, "ha_reversal": False}
        o, h, l, c = self.df["open"], self.df["high"], self.df["low"], self.df["close"]

        ha_close = (o + h + l + c) / 4
        ha_open = pd.Series(0.0, index=self.df.index)
        ha_open.iloc[0] = (o.iloc[0] + c.iloc[0]) / 2
        for i in range(1, len(self.df)):
            ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2
        ha_high = pd.concat([h, ha_open, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([l, ha_open, ha_close], axis=1).min(axis=1)

        bullish = ha_close > ha_open
        streak = 0
        trend_dir = "bullish" if bullish.iloc[-1] else "bearish"
        for i in range(len(bullish) - 1, -1, -1):
            if bullish.iloc[i] == bullish.iloc[-1]:
                streak += 1
            else:
                break

        no_lower_wick = ha_low.iloc[-1] == ha_open.iloc[-1] if bullish.iloc[-1] else False
        no_upper_wick = ha_high.iloc[-1] == ha_open.iloc[-1] if not bullish.iloc[-1] else False
        strong_trend = no_lower_wick or no_upper_wick

        reversal = len(bullish) >= 2 and bullish.iloc[-1] != bullish.iloc[-2]

        return {"ha_trend": trend_dir, "ha_streak": streak, "ha_reversal": reversal, "ha_strong_trend": strong_trend}

    def calculate_volatility_squeeze(self) -> Dict[str, Any]:
        """Bollinger Band / Keltner Channel squeeze detection."""
        if self.df is None or len(self.df) < 20:
            return {"squeeze_on": False, "squeeze_momentum": 0, "squeeze_signal": "no_data"}
        close, high, low = self.df["close"], self.df["high"], self.df["low"]

        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)

        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr_20 = tr.rolling(20).mean()
        kc_upper = sma_20 + (atr_20 * 1.5)
        kc_lower = sma_20 - (atr_20 * 1.5)

        squeeze_on = (bb_lower.iloc[-1] > kc_lower.iloc[-1]) and (bb_upper.iloc[-1] < kc_upper.iloc[-1])

        momentum = close - close.rolling(20).mean()
        mom_val = float(momentum.iloc[-1])
        mom_prev = float(momentum.iloc[-2]) if len(momentum) > 1 else mom_val
        mom_increasing = abs(mom_val) > abs(mom_prev)

        if squeeze_on:
            sig = "squeeze_building"
        elif not squeeze_on and mom_val > 0 and mom_increasing:
            sig = "squeeze_fire_long"
        elif not squeeze_on and mom_val < 0 and mom_increasing:
            sig = "squeeze_fire_short"
        else:
            sig = "no_squeeze"

        return {"squeeze_on": squeeze_on, "squeeze_momentum": mom_val, "squeeze_signal": sig}

    def detect_divergences(self) -> Dict[str, Any]:
        """Detect RSI and MACD divergences (bullish/bearish)."""
        if self.df is None or len(self.df) < 30:
            return {"rsi_divergence": "none", "macd_divergence": "none"}
        close = self.df["close"]

        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss))

        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_hist = (ema_12 - ema_26) - (ema_12 - ema_26).ewm(span=9, adjust=False).mean()

        lookback = 14
        price_higher_high = close.iloc[-1] > close.iloc[-lookback:].iloc[:-1].max()
        price_lower_low = close.iloc[-1] < close.iloc[-lookback:].iloc[:-1].min()
        rsi_lower_high = rsi.iloc[-1] < rsi.iloc[-lookback:].iloc[:-1].max() if not rsi.iloc[-lookback:].isna().all() else False
        rsi_higher_low = rsi.iloc[-1] > rsi.iloc[-lookback:].iloc[:-1].min() if not rsi.iloc[-lookback:].isna().all() else False

        rsi_div = "none"
        if price_higher_high and rsi_lower_high:
            rsi_div = "bearish"
        elif price_lower_low and rsi_higher_low:
            rsi_div = "bullish"

        macd_lower_high = macd_hist.iloc[-1] < macd_hist.iloc[-lookback:].iloc[:-1].max() if not macd_hist.iloc[-lookback:].isna().all() else False
        macd_higher_low = macd_hist.iloc[-1] > macd_hist.iloc[-lookback:].iloc[:-1].min() if not macd_hist.iloc[-lookback:].isna().all() else False

        macd_div = "none"
        if price_higher_high and macd_lower_high:
            macd_div = "bearish"
        elif price_lower_low and macd_higher_low:
            macd_div = "bullish"

        return {"rsi_divergence": rsi_div, "macd_divergence": macd_div}

    def calculate_market_structure(self) -> Dict[str, Any]:
        """Detect higher-highs/lower-lows (market structure)."""
        if self.df is None or len(self.df) < 20:
            return {"structure": "unknown", "swing_highs": [], "swing_lows": [], "last_bos": "none"}
        high, low = self.df["high"].values, self.df["low"].values
        n = len(high)

        swing_highs, swing_lows = [], []
        for i in range(2, n - 2):
            if high[i] > high[i - 1] and high[i] > high[i - 2] and high[i] > high[i + 1] and high[i] > high[i + 2]:
                swing_highs.append((i, float(high[i])))
            if low[i] < low[i - 1] and low[i] < low[i - 2] and low[i] < low[i + 1] and low[i] < low[i + 2]:
                swing_lows.append((i, float(low[i])))

        structure = "unknown"
        last_bos = "none"

        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            hh = swing_highs[-1][1] > swing_highs[-2][1]
            hl = swing_lows[-1][1] > swing_lows[-2][1]
            lh = swing_highs[-1][1] < swing_highs[-2][1]
            ll = swing_lows[-1][1] < swing_lows[-2][1]

            if hh and hl:
                structure = "bullish"
            elif lh and ll:
                structure = "bearish"
            elif hh and ll:
                structure = "expanding"
            elif lh and hl:
                structure = "contracting"
            else:
                structure = "mixed"

            price = float(self.df["close"].iloc[-1])
            if price > swing_highs[-1][1] and structure != "bullish":
                last_bos = "bullish_bos"
            elif price < swing_lows[-1][1] and structure != "bearish":
                last_bos = "bearish_bos"

        return {
            "structure": structure,
            "swing_highs": [{"index": s[0], "price": s[1]} for s in swing_highs[-3:]],
            "swing_lows": [{"index": s[0], "price": s[1]} for s in swing_lows[-3:]],
            "last_bos": last_bos,
        }

    def estimate_order_flow(self, trades: List[Dict]) -> Dict[str, Any]:
        """Estimate order flow delta from recent trades."""
        if not trades:
            return {"buy_volume": 0, "sell_volume": 0, "delta": 0, "cvd_trend": "neutral", "large_trades": 0}
        buy_vol, sell_vol, large_count = 0.0, 0.0, 0
        for t in trades:
            sz = float(t.get("sz", 0))
            px = float(t.get("px", 0))
            usd_value = sz * px
            side = t.get("side", "").lower()
            if side == "b" or side == "buy":
                buy_vol += usd_value
            else:
                sell_vol += usd_value
            if usd_value > 50000:
                large_count += 1

        delta = buy_vol - sell_vol
        total = buy_vol + sell_vol
        if total == 0:
            trend = "neutral"
        elif delta / total > 0.2:
            trend = "strong_buying"
        elif delta / total > 0.05:
            trend = "buying"
        elif delta / total < -0.2:
            trend = "strong_selling"
        elif delta / total < -0.05:
            trend = "selling"
        else:
            trend = "neutral"

        return {"buy_volume": buy_vol, "sell_volume": sell_vol, "delta": delta, "cvd_trend": trend, "large_trades": large_count}

    # ---- Order book analysis ----

    def analyze_orderbook(self, l2_data: Dict) -> Dict[str, Any]:
        if not l2_data or "levels" not in l2_data:
            return {"bid_depth_usd": 0, "ask_depth_usd": 0, "imbalance_ratio": 1.0, "pressure": "neutral",
                    "bid_wall": None, "ask_wall": None, "spread_bps": 0}
        try:
            levels = l2_data["levels"]
            bids = levels[0] if len(levels) > 0 else []
            asks = levels[1] if len(levels) > 1 else []

            bid_depth = sum(float(b["sz"]) * float(b["px"]) for b in bids[:10])
            ask_depth = sum(float(a["sz"]) * float(a["px"]) for a in asks[:10])
            imbalance = bid_depth / ask_depth if ask_depth > 0 else 1.0

            if imbalance > 2.0:
                pressure = "strong_bullish"
            elif imbalance > 1.5:
                pressure = "bullish"
            elif imbalance < 0.5:
                pressure = "strong_bearish"
            elif imbalance < 0.67:
                pressure = "bearish"
            else:
                pressure = "neutral"

            bid_wall = max(bids[:20], key=lambda b: float(b["sz"]), default=None) if bids else None
            ask_wall = max(asks[:20], key=lambda a: float(a["sz"]), default=None) if asks else None

            best_bid = float(bids[0]["px"]) if bids else 0
            best_ask = float(asks[0]["px"]) if asks else 0
            mid = (best_bid + best_ask) / 2 if best_bid and best_ask else 1
            spread_bps = ((best_ask - best_bid) / mid) * 10000

            return {
                "bid_depth_usd": bid_depth, "ask_depth_usd": ask_depth,
                "imbalance_ratio": imbalance, "pressure": pressure,
                "bid_wall": {"price": float(bid_wall["px"]), "size": float(bid_wall["sz"])} if bid_wall else None,
                "ask_wall": {"price": float(ask_wall["px"]), "size": float(ask_wall["sz"])} if ask_wall else None,
                "spread_bps": spread_bps,
            }
        except Exception as e:
            print(f"Error analyzing orderbook: {e}")
            return {"bid_depth_usd": 0, "ask_depth_usd": 0, "imbalance_ratio": 1.0, "pressure": "neutral",
                    "bid_wall": None, "ask_wall": None, "spread_bps": 0}

    # ---- Full analysis bundle ----

    def compute_all_advanced(self, trades: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Compute every advanced indicator in one call."""
        return {
            "ichimoku": self.calculate_ichimoku(),
            "stochastic_rsi": self.calculate_stochastic_rsi(),
            "adx": self.calculate_adx(),
            "obv": self.calculate_obv(),
            "supertrend": self.calculate_supertrend(),
            "pivot_points": self.calculate_pivot_points(),
            "fibonacci": self.calculate_fibonacci_levels(),
            "cmf": self.calculate_cmf(),
            "heikin_ashi": self.calculate_heikin_ashi(),
            "volatility_squeeze": self.calculate_volatility_squeeze(),
            "divergences": self.detect_divergences(),
            "market_structure": self.calculate_market_structure(),
            "order_flow": self.estimate_order_flow(trades or []),
        }

    def _empty_indicators(self) -> Dict[str, float]:
        return {
            "ema_9": 0, "ema_21": 0, "rsi_14": 50,
            "macd_line": 0, "macd_signal": 0, "macd_histogram": 0,
            "atr_14": 0, "bollinger_upper": 0, "bollinger_middle": 0,
            "bollinger_lower": 0, "volume_sma": 0, "vwap": 0,
        }


# ---------------------------------------------------------------------------
# Multi-timeframe helper
# ---------------------------------------------------------------------------

class MultiTimeframeEngine:
    """Fetches and analyses multiple timeframes for confluence scoring."""

    TIMEFRAMES = ["1m", "5m", "15m", "1h"]

    def __init__(self, client: HyperliquidClient):
        self.client = client
        self.analyzers: Dict[str, TechnicalAnalyzer] = {}

    def analyze(self, coin: str = "BTC") -> Dict[str, Any]:
        results = {}
        for tf in self.TIMEFRAMES:
            analyzer = TechnicalAnalyzer()
            candles = self.client.get_candles(coin, tf, 100)
            analyzer.load_candles(candles)
            indicators = analyzer.calculate_indicators()
            ichimoku = analyzer.calculate_ichimoku()
            adx = analyzer.calculate_adx()
            supertrend = analyzer.calculate_supertrend()

            if indicators["ema_9"] > indicators["ema_21"]:
                trend = "bullish"
            elif indicators["ema_9"] < indicators["ema_21"]:
                trend = "bearish"
            else:
                trend = "neutral"

            results[tf] = {
                "trend": trend,
                "rsi": indicators["rsi_14"],
                "macd_histogram": indicators["macd_histogram"],
                "adx": adx["adx"],
                "supertrend": supertrend["supertrend_direction"],
                "ichimoku": ichimoku["cloud_signal"],
                "trend_strength": adx["trend_strength"],
            }
            self.analyzers[tf] = analyzer

        bullish_count = sum(1 for r in results.values() if r["trend"] == "bullish")
        bearish_count = sum(1 for r in results.values() if r["trend"] == "bearish")
        total = len(results)

        if bullish_count >= 3:
            confluence = "strong_bullish"
        elif bullish_count >= 2:
            confluence = "bullish"
        elif bearish_count >= 3:
            confluence = "strong_bearish"
        elif bearish_count >= 2:
            confluence = "bearish"
        else:
            confluence = "mixed"

        htf_aligned = results.get("1h", {}).get("trend") == results.get("15m", {}).get("trend")

        return {
            "timeframes": results,
            "confluence": confluence,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "htf_aligned": htf_aligned,
        }


# ---------------------------------------------------------------------------
# Session / Kill-zone helper
# ---------------------------------------------------------------------------

class SessionFilter:
    """Identifies trading sessions and high-probability kill zones."""

    SESSIONS = {
        "asia": {"start": 0, "end": 8},
        "london": {"start": 8, "end": 16},
        "new_york": {"start": 13, "end": 21},
        "london_ny_overlap": {"start": 13, "end": 16},
    }
    KILL_ZONES = {
        "london_open": {"start": 8, "end": 10},
        "ny_open": {"start": 13, "end": 15},
        "london_close": {"start": 15, "end": 17},
        "ny_close": {"start": 20, "end": 22},
    }

    @classmethod
    def current_session(cls) -> Dict[str, Any]:
        hour = datetime.utcnow().hour
        active = [name for name, s in cls.SESSIONS.items() if s["start"] <= hour < s["end"]]
        in_kill_zone = [name for name, kz in cls.KILL_ZONES.items() if kz["start"] <= hour < kz["end"]]
        is_overlap = "london_ny_overlap" in active

        vol_factor = 1.0
        if is_overlap or in_kill_zone:
            vol_factor = 1.5
        elif hour >= 22 or hour < 6:
            vol_factor = 0.6

        return {
            "utc_hour": hour,
            "active_sessions": active,
            "in_kill_zone": in_kill_zone,
            "is_overlap": is_overlap,
            "volatility_factor": vol_factor,
            "recommended_trading": len(in_kill_zone) > 0 or is_overlap,
        }


# ---------------------------------------------------------------------------
# Trailing stop manager
# ---------------------------------------------------------------------------

class TrailingStopManager:
    """Tracks peak price and manages trailing stop logic."""

    def __init__(self, activation_pct: float = 0.003, distance_pct: float = 0.002):
        self.activation_pct = activation_pct
        self.distance_pct = distance_pct
        self.peak_price: Optional[float] = None
        self.is_activated = False
        self.entry_price: Optional[float] = None
        self.side: Optional[str] = None

    def reset(self):
        self.peak_price = None
        self.is_activated = False
        self.entry_price = None
        self.side = None

    def init_trade(self, entry_price: float, side: str):
        self.entry_price = entry_price
        self.side = side
        self.peak_price = entry_price
        self.is_activated = False

    def update(self, current_price: float) -> Dict[str, Any]:
        if self.entry_price is None or self.side is None:
            return {"trailing_active": False, "should_close": False, "stop_price": None}

        if self.side == "long":
            if self.peak_price is None or current_price > self.peak_price:
                self.peak_price = current_price
            pnl_pct = (self.peak_price - self.entry_price) / self.entry_price
            if pnl_pct >= self.activation_pct:
                self.is_activated = True
            if self.is_activated:
                stop_price = self.peak_price * (1 - self.distance_pct)
                return {
                    "trailing_active": True,
                    "should_close": current_price <= stop_price,
                    "stop_price": stop_price,
                    "peak_price": self.peak_price,
                }
        else:
            if self.peak_price is None or current_price < self.peak_price:
                self.peak_price = current_price
            pnl_pct = (self.entry_price - self.peak_price) / self.entry_price
            if pnl_pct >= self.activation_pct:
                self.is_activated = True
            if self.is_activated:
                stop_price = self.peak_price * (1 + self.distance_pct)
                return {
                    "trailing_active": True,
                    "should_close": current_price >= stop_price,
                    "stop_price": stop_price,
                    "peak_price": self.peak_price,
                }

        return {"trailing_active": False, "should_close": False, "stop_price": None}


# ---------------------------------------------------------------------------
# Equity curve protector
# ---------------------------------------------------------------------------

class EquityCurveProtector:
    """Detects drawdowns and pauses trading when equity curve degrades."""

    def __init__(self, max_daily_drawdown_pct: float = 0.05, cooldown_after_losses: int = 3):
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.cooldown_after_losses = cooldown_after_losses
        self.daily_start_equity: Optional[float] = None
        self.day_start: Optional[datetime] = None
        self.consecutive_losses = 0
        self.pnl_today: List[float] = []

    def new_day_check(self, equity: float):
        now = datetime.utcnow()
        if self.day_start is None or now.date() != self.day_start.date():
            self.day_start = now
            self.daily_start_equity = equity
            self.pnl_today = []
            self.consecutive_losses = 0

    def record_trade(self, pnl: float):
        self.pnl_today.append(pnl)
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def should_trade(self, current_equity: float) -> Dict[str, Any]:
        if self.daily_start_equity is None:
            self.new_day_check(current_equity)

        self.new_day_check(current_equity)

        drawdown = (self.daily_start_equity - current_equity) / self.daily_start_equity if self.daily_start_equity else 0
        drawdown_breached = drawdown >= self.max_daily_drawdown_pct
        loss_cooldown = self.consecutive_losses >= self.cooldown_after_losses

        return {
            "can_trade": not drawdown_breached and not loss_cooldown,
            "daily_drawdown_pct": drawdown,
            "max_drawdown_pct": self.max_daily_drawdown_pct,
            "drawdown_breached": drawdown_breached,
            "consecutive_losses": self.consecutive_losses,
            "loss_cooldown_active": loss_cooldown,
            "trades_today": len(self.pnl_today),
            "pnl_today": sum(self.pnl_today),
        }


# ===========================================================================
# LangChain Tools
# ===========================================================================

class MarketDataInput(BaseModel):
    coin: str = Field(default="BTC", description="Coin symbol")


class MarketDataTool(BaseTool):
    """Fetches market data, core + advanced indicators, orderbook, order flow."""

    name: str = "get_market_data"
    description: str = """Fetches comprehensive market data and ALL technical indicators for BTC.

Returns:
- Price data: mid price, best bid/ask, spread
- Core indicators: EMA 9/21, RSI, MACD, Bollinger Bands, ATR, VWAP
- Advanced indicators: Ichimoku Cloud, Stochastic RSI, ADX, OBV, Supertrend,
  Pivot Points, Fibonacci levels, CMF, Heikin Ashi, Volatility Squeeze
- Market microstructure: divergences, market structure (HH/HL/LH/LL), break of structure
- Order book: depth, imbalance, walls, spread
- Order flow: buy/sell volume delta, CVD trend, large trade detection
- Session info: current session, kill zones, volatility factor

Use this as the primary market analysis tool before making any trading decision."""

    args_schema: type[BaseModel] = MarketDataInput
    client: Optional[HyperliquidClient] = None
    analyzer: Optional[TechnicalAnalyzer] = None

    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())
        object.__setattr__(self, "analyzer", TechnicalAnalyzer())

    def _run(self, coin: str = "BTC") -> str:
        try:
            mid_price = self.client.get_mid_price(coin)
            l2_data = self.client.get_l2_snapshot(coin)
            candles = self.client.get_candles(coin, "1m", 200)
            recent_trades = self.client.get_recent_trades(coin)

            if l2_data and "levels" in l2_data:
                levels = l2_data["levels"]
                best_bid = float(levels[0][0]["px"]) if levels[0] else 0
                best_ask = float(levels[1][0]["px"]) if levels[1] else 0
            else:
                best_bid = mid_price * 0.9999 if mid_price else 0
                best_ask = mid_price * 1.0001 if mid_price else 0

            spread = best_ask - best_bid
            spread_bps = (spread / mid_price * 10000) if mid_price else 0

            self.analyzer.load_candles(candles)
            core = self.analyzer.calculate_indicators()
            advanced = self.analyzer.compute_all_advanced(recent_trades)
            orderbook = self.analyzer.analyze_orderbook(l2_data)
            session = SessionFilter.current_session()

            result = {
                "market_data": {
                    "symbol": coin, "mid_price": mid_price,
                    "best_bid": best_bid, "best_ask": best_ask,
                    "spread": spread, "spread_bps": spread_bps,
                    "timestamp": datetime.now().isoformat(),
                },
                "core_indicators": core,
                "advanced_indicators": advanced,
                "orderbook": orderbook,
                "session": session,
            }
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


class MultiTimeframeInput(BaseModel):
    coin: str = Field(default="BTC", description="Coin symbol")


class MultiTimeframeTool(BaseTool):
    """Multi-timeframe confluence analysis across 1m, 5m, 15m, 1h."""

    name: str = "multi_timeframe_analysis"
    description: str = """Analyses BTC across 4 timeframes (1m, 5m, 15m, 1h) for confluence.

Returns per timeframe: trend direction, RSI, MACD histogram, ADX, supertrend, ichimoku.
Also returns an overall confluence score (strong_bullish / bullish / mixed / bearish / strong_bearish)
and whether higher-timeframe trends are aligned.

Use this to confirm scalping signals with higher-timeframe trend direction."""

    args_schema: type[BaseModel] = MultiTimeframeInput
    client: Optional[HyperliquidClient] = None

    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())

    def _run(self, coin: str = "BTC") -> str:
        try:
            engine = MultiTimeframeEngine(self.client)
            return json.dumps(engine.analyze(coin), indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


class FundingRateInput(BaseModel):
    coin: str = Field(default="BTC", description="Coin symbol")


class FundingRateTool(BaseTool):
    """Fetches funding rate data for funding-rate-aware scalping."""

    name: str = "get_funding_rate"
    description: str = """Fetches current funding rate, open interest, premium, oracle and mark prices.

Returns:
- funding_rate: Current hourly funding rate
- open_interest: Total open interest
- premium: Premium of mark over oracle
- oracle_price / mark_price
- funding_signal: whether funding favours long, short, or is neutral
- annualised_rate: The funding rate annualised for context

Use this to:
1. Avoid entering positions that pay high funding
2. Identify overcrowded trades (extreme funding = potential reversal)
3. Spot funding rate arbitrage opportunities"""

    args_schema: type[BaseModel] = FundingRateInput
    client: Optional[HyperliquidClient] = None

    def __init__(self, client: Optional[HyperliquidClient] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())

    def _run(self, coin: str = "BTC") -> str:
        try:
            data = self.client.get_funding_rate(coin)
            if not data:
                return json.dumps({"error": "Could not fetch funding rate"})

            fr = data["funding_rate"]
            annualised = fr * 8760
            if fr > 0.0005:
                signal = "extreme_long_pay"
            elif fr > 0.0001:
                signal = "longs_paying"
            elif fr < -0.0005:
                signal = "extreme_short_pay"
            elif fr < -0.0001:
                signal = "shorts_paying"
            else:
                signal = "neutral"

            data["annualised_rate"] = annualised
            data["funding_signal"] = signal
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


class PositionInput(BaseModel):
    coin: str = Field(default="BTC", description="Coin symbol")


class PositionTool(BaseTool):
    """Fetches position, account state, trailing stop status, and equity protection."""

    name: str = "get_position"
    description: str = """Fetches current position, account equity, trailing stop status, and equity curve protection.

Returns:
- position: side, size, entry price, unrealized PnL, leverage
- account_equity: total account value
- trailing_stop: whether trailing stop is active and current stop price
- equity_protection: daily drawdown, consecutive losses, whether trading is allowed

Use this before every trade decision to know current state."""

    args_schema: type[BaseModel] = PositionInput
    client: Optional[HyperliquidClient] = None
    trailing_manager: Optional[TrailingStopManager] = None
    equity_protector: Optional[EquityCurveProtector] = None

    def __init__(self, client: Optional[HyperliquidClient] = None,
                 trailing_manager: Optional[TrailingStopManager] = None,
                 equity_protector: Optional[EquityCurveProtector] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())
        object.__setattr__(self, "trailing_manager", trailing_manager or TrailingStopManager())
        object.__setattr__(self, "equity_protector", equity_protector or EquityCurveProtector())

    def _run(self, coin: str = "BTC") -> str:
        try:
            position = self.client.get_position(coin)
            user_state = self.client.get_user_state()
            account_equity = 0
            if user_state and "marginSummary" in user_state:
                account_equity = float(user_state["marginSummary"].get("accountValue", 0))

            trailing = {"trailing_active": False, "should_close": False, "stop_price": None}
            if position:
                mid = self.client.get_mid_price(coin)
                if mid:
                    trailing = self.trailing_manager.update(mid)

            equity_check = self.equity_protector.should_trade(account_equity)

            return json.dumps({
                "position": position,
                "account_equity": account_equity,
                "has_position": position is not None,
                "trailing_stop": trailing,
                "equity_protection": equity_check,
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


class OrderInput(BaseModel):
    action: str = Field(description="Action: 'open_long', 'open_short', 'close', 'partial_close'")
    size: float = Field(default=0, description="Order size in BTC (0 to auto-calculate)")
    order_type: str = Field(default="market", description="'market' or 'limit'")
    limit_price: Optional[float] = Field(default=None, description="Limit price (for limit orders)")
    slippage: float = Field(default=0.01, description="Slippage tolerance for market orders")
    close_pct: float = Field(default=1.0, description="For partial_close: fraction 0-1 of position to close")


class ExecuteOrderTool(BaseTool):
    """Executes trades with auto-sizing, trailing stop initialization, and partial close."""

    name: str = "execute_order"
    description: str = """Executes a trade on Hyperliquid with advanced features.

Actions:
- 'open_long': Open a long (buy). Auto-sizes if size=0.
- 'open_short': Open a short (sell). Auto-sizes if size=0.
- 'close': Close entire position.
- 'partial_close': Close a fraction (close_pct) of the position.

Automatically:
- Calculates position size from account equity and risk config
- Initialises trailing stop on new entries
- Records trade for equity curve protection

IMPORTANT: Only use after confirming signals with get_market_data and multi_timeframe_analysis."""

    args_schema: type[BaseModel] = OrderInput
    client: Optional[HyperliquidClient] = None
    trailing_manager: Optional[TrailingStopManager] = None
    equity_protector: Optional[EquityCurveProtector] = None

    def __init__(self, client: Optional[HyperliquidClient] = None,
                 trailing_manager: Optional[TrailingStopManager] = None,
                 equity_protector: Optional[EquityCurveProtector] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())
        object.__setattr__(self, "trailing_manager", trailing_manager or TrailingStopManager())
        object.__setattr__(self, "equity_protector", equity_protector or EquityCurveProtector())

    def _run(self, action: str, size: float = 0, order_type: str = "market",
             limit_price: Optional[float] = None, slippage: float = 0.01, close_pct: float = 1.0) -> str:
        try:
            coin = "BTC"

            if action == "close":
                position = self.client.get_position(coin)
                result = self.client.close_position(coin)
                if position:
                    self.trailing_manager.reset()
                    self.equity_protector.record_trade(position.get("unrealized_pnl", 0))
                return json.dumps({"action": "close", "result": result}, indent=2, default=str)

            if action == "partial_close":
                position = self.client.get_position(coin)
                if not position:
                    return json.dumps({"error": "No position to partially close"})
                partial_size = round(position["size"] * close_pct, 5)
                is_buy = position["side"] == "short"
                result = self.client.place_market_order(coin, is_buy, partial_size, slippage)
                return json.dumps({"action": "partial_close", "size_closed": partial_size, "result": result}, indent=2, default=str)

            if size <= 0:
                user_state = self.client.get_user_state()
                if user_state and "marginSummary" in user_state:
                    equity = float(user_state["marginSummary"].get("accountValue", 0))
                    mid_price = self.client.get_mid_price(coin) or 80000
                    risk_amount = equity * self.client.config.risk_per_trade
                    size = round((risk_amount * self.client.config.default_leverage) / mid_price, 5)
                else:
                    return json.dumps({"error": "Cannot calculate size: no account data"})

            is_buy = action == "open_long"

            if order_type == "limit" and limit_price:
                result = self.client.place_limit_order(coin, is_buy, size, limit_price)
            else:
                result = self.client.place_market_order(coin, is_buy, size, slippage)

            mid_price = self.client.get_mid_price(coin) or 80000
            self.trailing_manager.init_trade(mid_price, "long" if is_buy else "short")

            return json.dumps({"action": action, "size": size, "order_type": order_type, "result": result}, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


class RiskCheckInput(BaseModel):
    proposed_action: str = Field(description="Proposed action to validate")
    proposed_size: float = Field(description="Proposed position size in BTC")


class RiskCheckTool(BaseTool):
    """Comprehensive pre-trade risk validation."""

    name: str = "risk_check"
    description: str = """Performs comprehensive pre-trade risk checks.

Checks:
- Hourly trade limit
- Position size limit (USD)
- Account risk percentage
- Equity curve protection (daily drawdown, loss streaks)
- Session suitability (kill zones)
- Existing position conflict
- Spread check (ensures spread is tight enough for scalping)

Returns pass/fail for each check and an overall can_execute flag."""

    args_schema: type[BaseModel] = RiskCheckInput
    client: Optional[HyperliquidClient] = None
    equity_protector: Optional[EquityCurveProtector] = None
    trades_this_hour: int = 0
    hour_start: Optional[datetime] = None

    def __init__(self, client: Optional[HyperliquidClient] = None,
                 equity_protector: Optional[EquityCurveProtector] = None):
        super().__init__()
        object.__setattr__(self, "client", client or HyperliquidClient())
        object.__setattr__(self, "equity_protector", equity_protector or EquityCurveProtector())
        object.__setattr__(self, "trades_this_hour", 0)
        object.__setattr__(self, "hour_start", datetime.now())

    def _run(self, proposed_action: str, proposed_size: float) -> str:
        checks = []
        all_passed = True

        try:
            now = datetime.now()
            if self.hour_start is None or (now - self.hour_start).total_seconds() > 3600:
                object.__setattr__(self, "hour_start", now)
                object.__setattr__(self, "trades_this_hour", 0)

            if self.trades_this_hour >= self.client.config.max_trades_per_hour:
                checks.append(f"FAIL: Max trades/hour ({self.client.config.max_trades_per_hour}) reached")
                all_passed = False
            else:
                checks.append(f"PASS: Trade count ({self.trades_this_hour}/{self.client.config.max_trades_per_hour})")

            mid_price = self.client.get_mid_price("BTC") or 80000
            position_value = proposed_size * mid_price
            if position_value > self.client.config.max_position_size_usd:
                checks.append(f"FAIL: Position ${position_value:.0f} > max ${self.client.config.max_position_size_usd:.0f}")
                all_passed = False
            else:
                checks.append(f"PASS: Position ${position_value:.0f} within limit")

            user_state = self.client.get_user_state()
            if user_state:
                account_value = float(user_state.get("marginSummary", {}).get("accountValue", 0))
                if account_value > 0:
                    risk_pct = (position_value / self.client.config.default_leverage) / account_value
                    max_risk = self.client.config.risk_per_trade * 5
                    if risk_pct > max_risk:
                        checks.append(f"FAIL: Risk {risk_pct*100:.2f}% > max {max_risk*100:.2f}%")
                        all_passed = False
                    else:
                        checks.append(f"PASS: Risk {risk_pct*100:.2f}%")

                    eq_check = self.equity_protector.should_trade(account_value)
                    if not eq_check["can_trade"]:
                        reason = "daily drawdown" if eq_check["drawdown_breached"] else "loss cooldown"
                        checks.append(f"FAIL: Equity protection – {reason}")
                        all_passed = False
                    else:
                        checks.append(f"PASS: Equity protection OK (drawdown {eq_check['daily_drawdown_pct']*100:.2f}%)")

            session = SessionFilter.current_session()
            if not session["recommended_trading"]:
                checks.append(f"WARNING: Not in kill zone (hour={session['utc_hour']}). Proceed with caution.")
            else:
                checks.append(f"PASS: In kill zone ({', '.join(session['in_kill_zone'])})")

            l2 = self.client.get_l2_snapshot("BTC")
            if l2 and "levels" in l2:
                levels = l2["levels"]
                if levels[0] and levels[1]:
                    bid = float(levels[0][0]["px"])
                    ask = float(levels[1][0]["px"])
                    spread_bps = ((ask - bid) / ((ask + bid) / 2)) * 10000
                    if spread_bps > 5:
                        checks.append(f"FAIL: Spread too wide ({spread_bps:.1f} bps > 5 bps)")
                        all_passed = False
                    else:
                        checks.append(f"PASS: Spread {spread_bps:.1f} bps")

            existing = self.client.get_position("BTC")
            if existing and proposed_action in ["open_long", "open_short"]:
                if (proposed_action == "open_long" and existing["side"] == "short") or \
                   (proposed_action == "open_short" and existing["side"] == "long"):
                    checks.append("WARNING: Will flip position direction")
                elif (proposed_action == "open_long" and existing["side"] == "long") or \
                     (proposed_action == "open_short" and existing["side"] == "short"):
                    checks.append("WARNING: Will add to existing position")

            if all_passed:
                object.__setattr__(self, "trades_this_hour", self.trades_this_hour + 1)

            return json.dumps({"checks": checks, "all_passed": all_passed, "can_execute": all_passed}, indent=2)
        except Exception as e:
            return json.dumps({"checks": [f"ERROR: {str(e)}"], "all_passed": False, "can_execute": False})


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_scalping_tools(client: Optional[HyperliquidClient] = None) -> List[BaseTool]:
    """Create all scalping tools with shared client and state managers."""
    if client is None:
        client = HyperliquidClient()

    trailing = TrailingStopManager(
        activation_pct=client.config.trailing_stop_activation_pct,
        distance_pct=client.config.trailing_stop_distance_pct,
    )
    equity = EquityCurveProtector(
        max_daily_drawdown_pct=client.config.max_daily_drawdown_pct,
    )

    return [
        MarketDataTool(client),
        MultiTimeframeTool(client),
        FundingRateTool(client),
        PositionTool(client, trailing, equity),
        ExecuteOrderTool(client, trailing, equity),
        RiskCheckTool(client, equity),
    ]
