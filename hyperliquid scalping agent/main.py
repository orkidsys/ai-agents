"""
Hyperliquid BTC Scalping Agent - AI-powered scalping bot for BTC perpetuals.

This agent uses Schema-Guided Reasoning (SGR) to make structured trading decisions
for scalping BTC on Hyperliquid exchange.
"""
import os
import json
import time
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from tools import (
    HyperliquidClient, 
    HyperliquidConfig,
    create_scalping_tools,
    TechnicalAnalyzer
)
from schemas import (
    ScalpingDecisionResponse,
    AgentState,
    TradeRecord,
    PositionState
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


class BTCScalpingAgent:
    """AI-powered BTC scalping agent for Hyperliquid."""
    
    SYSTEM_PROMPT = """You are a professional BTC scalping trading agent operating on Hyperliquid exchange.
Your goal is to identify short-term trading opportunities and execute precise scalping trades.

SCALPING STRATEGY:
1. Focus ONLY on BTC perpetual futures
2. Target small, quick profits (0.3-0.5% per trade)
3. Use tight stop losses (0.2-0.3%)
4. Trade with the short-term momentum
5. Avoid trading during low liquidity periods

CRITICAL RULES:
1. ALWAYS analyze market data before making any trading decision
2. NEVER enter a trade without checking current position first
3. ALWAYS perform risk checks before executing any order
4. Follow the 5-step reasoning process exactly
5. Only trade when signals are clear and align
6. Maximum 1 position at a time
7. Close losing positions quickly - don't hold and hope

SIGNAL CRITERIA FOR ENTRY:
Long Entry:
- RSI between 30-45 (recovering from oversold)
- MACD histogram turning positive
- Price above EMA 9 and EMA 9 > EMA 21 (or crossing)
- Order book shows bullish pressure
- Price near lower Bollinger Band (reversal setup)

Short Entry:
- RSI between 55-70 (pulling back from overbought)
- MACD histogram turning negative  
- Price below EMA 9 and EMA 9 < EMA 21 (or crossing)
- Order book shows bearish pressure
- Price near upper Bollinger Band (reversal setup)

EXIT CRITERIA:
- Take profit at 0.3-0.5% gain
- Stop loss at 0.2-0.3% loss
- Exit if signal reverses
- Exit if position held for more than 5-10 minutes without profit

5-STEP SCHEMA-GUIDED REASONING PROCESS:

STEP 1 - MARKET ANALYSIS:
- Fetch current market data using get_market_data tool
- Analyze price action, spread, and volatility
- Determine market regime (trending/ranging/volatile)

STEP 2 - SIGNAL DETECTION:
- Evaluate EMA crossover signals
- Check RSI levels and divergences
- Analyze MACD crossover and histogram
- Check Bollinger Band position
- Assess order book imbalance

STEP 3 - POSITION MANAGEMENT:
- Check current position using get_position tool
- If in position: evaluate exit conditions
- If no position: evaluate entry conditions
- Calculate position size based on risk parameters

STEP 4 - EXECUTION PLAN:
- Decide whether to execute a trade
- Choose order type (market/limit)
- Set entry price, stop loss, take profit levels
- Confirm all parameters

STEP 5 - RISK MANAGEMENT:
- Run risk_check tool to validate trade
- Execute order if all checks pass
- Log the decision and result

IMPORTANT: Always return your reasoning in a structured format following these 5 steps.
Never skip steps or make assumptions without data."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.1,
        verbose: bool = True
    ):
        """Initialize the scalping agent."""
        self.verbose = verbose
        self.config = HyperliquidConfig()
        self.client = HyperliquidClient(self.config)
        self.tools = create_scalping_tools(self.client)
        self.analyzer = TechnicalAnalyzer()
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            max_iterations=10,
            handle_parsing_errors=True
        )
        
        self.state = AgentState()
        self.chat_history: List = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌",
            "TRADE": "💰"
        }.get(level, "")
        
        if self.verbose:
            print(f"[{timestamp}] {prefix} {message}")
    
    def analyze_market(self) -> Dict:
        """Perform market analysis and return structured decision."""
        self.log("Starting market analysis cycle", "INFO")
        
        prompt = """Analyze the current BTC market conditions and determine if there's a scalping opportunity.

Follow the 5-step reasoning process:
1. First, call get_market_data to fetch current market conditions
2. Analyze the technical indicators and order book
3. Call get_position to check current position status
4. If you identify a trade opportunity, call risk_check to validate
5. If all checks pass and signal is strong, call execute_order

Return your complete analysis with reasoning for each step.

Current time: {timestamp}
""".format(timestamp=datetime.now().isoformat())
        
        try:
            result = self.executor.invoke({
                "input": prompt,
                "chat_history": self.chat_history[-10:]
            })
            
            output = result.get("output", "")
            self.chat_history.append(HumanMessage(content=prompt))
            self.chat_history.append(AIMessage(content=output))
            
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            return {
                "success": True,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"Error in market analysis: {e}", "ERROR")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_position_management(self) -> Dict:
        """Check and manage existing position."""
        position = self.client.get_position("BTC")
        
        if not position:
            return {"has_position": False, "action": "none"}
        
        prompt = """We have an open BTC position that needs management.

Current position details will be fetched. Analyze if we should:
1. Hold the position (signals still valid)
2. Take profit (target reached or momentum fading)
3. Stop loss (signals reversed or max loss reached)

Call get_position and get_market_data, then make a decision.
If closing, call execute_order with action='close'.

Provide clear reasoning for your decision."""
        
        try:
            result = self.executor.invoke({
                "input": prompt,
                "chat_history": self.chat_history[-5:]
            })
            
            return {
                "has_position": True,
                "output": result.get("output", ""),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"Error in position management: {e}", "ERROR")
            return {
                "has_position": True,
                "error": str(e)
            }
    
    def run_single_cycle(self) -> Dict:
        """Run a single analysis and trading cycle."""
        self.log("=" * 60, "INFO")
        self.log("Starting new trading cycle", "INFO")
        
        position_check = self.check_position_management()
        
        if position_check.get("has_position"):
            self.log("Managing existing position", "INFO")
            return position_check
        
        analysis = self.analyze_market()
        
        if analysis.get("success"):
            self.log("Market analysis completed", "SUCCESS")
        else:
            self.log(f"Market analysis failed: {analysis.get('error')}", "ERROR")
        
        return analysis
    
    def run_continuous(
        self,
        interval_seconds: int = 30,
        max_cycles: Optional[int] = None
    ):
        """Run the agent continuously."""
        self.log("Starting continuous scalping mode", "INFO")
        self.log(f"Network: {self.config.network}", "INFO")
        self.log(f"Analysis interval: {interval_seconds}s", "INFO")
        self.log(f"Max position size: ${self.config.max_position_size_usd}", "INFO")
        self.log(f"Leverage: {self.config.default_leverage}x", "INFO")
        self.log(f"Take profit: {self.config.take_profit_pct*100}%", "INFO")
        self.log(f"Stop loss: {self.config.stop_loss_pct*100}%", "INFO")
        
        self.client.subscribe_to_market_data("BTC")
        
        cycle_count = 0
        self.state.is_running = True
        
        try:
            while self.state.is_running:
                cycle_count += 1
                
                if max_cycles and cycle_count > max_cycles:
                    self.log(f"Reached max cycles ({max_cycles})", "INFO")
                    break
                
                self.log(f"Cycle {cycle_count}", "INFO")
                
                result = self.run_single_cycle()
                
                if "execute" in str(result.get("output", "")).lower():
                    self.state.total_trades += 1
                    self.log(f"Trade executed (Total: {self.state.total_trades})", "TRADE")
                
                self.log(f"Sleeping for {interval_seconds}s...", "INFO")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.log("Received interrupt signal", "WARNING")
        finally:
            self.state.is_running = False
            self.log("Agent stopped", "INFO")
            self._print_session_summary()
    
    def _print_session_summary(self):
        """Print session summary."""
        print("\n" + "=" * 60)
        print("📊 SESSION SUMMARY")
        print("=" * 60)
        print(f"Total Trades: {self.state.total_trades}")
        print(f"Winning Trades: {self.state.winning_trades}")
        print(f"Losing Trades: {self.state.losing_trades}")
        print(f"Total PnL: ${self.state.total_pnl:.2f}")
        
        if self.state.total_trades > 0:
            win_rate = (self.state.winning_trades / self.state.total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        
        print("=" * 60 + "\n")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        position = self.client.get_position("BTC")
        user_state = self.client.get_user_state()
        
        account_equity = 0
        if user_state and "marginSummary" in user_state:
            account_equity = float(user_state["marginSummary"].get("accountValue", 0))
        
        return {
            "is_running": self.state.is_running,
            "network": self.config.network,
            "account_equity": account_equity,
            "current_position": position,
            "total_trades": self.state.total_trades,
            "total_pnl": self.state.total_pnl,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point for the scalping agent."""
    print("\n" + "=" * 60)
    print("🤖 HYPERLIQUID BTC SCALPING AGENT")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set in environment")
        print("Please copy .env-example to .env and configure your API keys")
        return
    
    private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    if not private_key:
        print("⚠️  Warning: HYPERLIQUID_PRIVATE_KEY not set")
        print("Agent will run in read-only mode (no trading)")
    
    agent = BTCScalpingAgent(
        model_name="gpt-4",
        temperature=0.1,
        verbose=True
    )
    
    status = agent.get_status()
    print(f"\n📊 Account Status:")
    print(f"   Network: {status['network']}")
    print(f"   Equity: ${status['account_equity']:.2f}")
    print(f"   Position: {status['current_position']}")
    
    print("\n🚀 Starting scalping agent...")
    print("   Press Ctrl+C to stop\n")
    
    agent.run_continuous(
        interval_seconds=30,
        max_cycles=None
    )


if __name__ == "__main__":
    main()
