"""
Portfolio Analysis Agent - A comprehensive cryptocurrency portfolio analysis agent.

This agent uses Schema-Guided Reasoning (SGR) to provide structured portfolio reports
for EVM and Solana wallets with historical performance tracking.
"""
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import PortfolioDataTool
from schemas import PortfolioAnalysisResponse
import os
import json
from typing import Optional, Dict, List
from datetime import datetime


# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


class PortfolioAgent:
    """A portfolio analysis agent using Schema-Guided Reasoning."""
    
    SYSTEM_PROMPT = """You are a cryptocurrency portfolio analysis assistant that provides comprehensive portfolio reports and performance analysis.

CRITICAL RULES:
1. You analyze user portfolios based on their EVM and/or Solana wallet addresses
2. In STEP 1, parse the user's request to determine the time period (daily, weekly, or monthly). If no time period is specified, default to "unknown"
3. DO NOT call the tool multiple times with different timeframes - use only the timeframe from STEP 1
4. Calculate portfolio performance by comparing historical vs current values from the tool response
5. Always include "This is not financial advice" in your final answer
6. Be thorough, quantitative, and specific in your analysis
7. Follow the 5-step Schema-Guided Reasoning process exactly:
   - STEP 1: Parse the request and extract timeframe/wallet addresses
   - STEP 2: Fetch portfolio data using the tool ONCE
   - STEP 3: Analyze portfolio composition
   - STEP 4: Analyze performance metrics
   - STEP 5: Generate comprehensive report with insights"""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
    ):
        """
        Initialize the portfolio agent.
        
        Args:
            model_name: The LLM model to use (default: "gpt-4")
            temperature: Temperature for the model (lower = more focused)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.portfolio_tool = PortfolioDataTool()
        
        # Create the agent
        self.agent = create_agent(
            model=self.llm,
            tools=[self.portfolio_tool],
            system_prompt=self.SYSTEM_PROMPT
        )
    
    def analyze(
        self,
        query: str,
        evm_wallet_address: Optional[str] = None,
        solana_wallet_address: Optional[str] = None,
        verbose: bool = False
    ) -> Dict:
        """
        Analyze a portfolio based on the query and wallet addresses.
        
        Args:
            query: The user's question or request
            evm_wallet_address: EVM wallet address (optional)
            solana_wallet_address: Solana wallet address (optional)
            verbose: Whether to print intermediate steps
            
        Returns:
            Dict containing the analysis results
        """
        if verbose:
            print(f"🔍 Analyzing Portfolio")
            print(f"Query: {query}")
            if evm_wallet_address:
                print(f"EVM Address: {evm_wallet_address}")
            if solana_wallet_address:
                print(f"Solana Address: {solana_wallet_address}")
            print("=" * 70)
        
        try:
            # Prepare the user message with wallet addresses
            wallet_info = []
            if evm_wallet_address:
                wallet_info.append(f"EVM: {evm_wallet_address}")
            if solana_wallet_address:
                wallet_info.append(f"Solana: {solana_wallet_address}")
            
            user_message = f"Wallet addresses: {', '.join(wallet_info) if wallet_info else 'Not provided'}\n\nUser question: {query}"
            
            if verbose:
                print("📡 Invoking agent...\n")
            
            # Invoke the agent
            result = self.agent.invoke({
                "messages": [HumanMessage(content=user_message)]
            })
            
            if verbose:
                print("✅ Agent response received\n")
            
            # Extract the final message
            messages = result.get("messages", [])
            if not messages:
                raise ValueError("No messages returned from agent")
            
            # Get the final assistant message
            final_message = messages[-1]
            response_content = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            # Try to parse structured response
            try:
                # The agent should return structured JSON matching our schema
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    structured_response = PortfolioAnalysisResponse(**parsed_data)
                else:
                    # Fallback: create a basic response structure
                    structured_response = self._create_fallback_response(
                        query, response_content, evm_wallet_address, solana_wallet_address
                    )
            except Exception as e:
                if verbose:
                    print(f"⚠️  Could not parse structured response: {e}")
                structured_response = self._create_fallback_response(
                    query, response_content, evm_wallet_address, solana_wallet_address
                )
            
            return {
                "question": query,
                "response": {
                    "messages": [str(msg) for msg in messages],
                    "structuredResponse": structured_response.dict() if hasattr(structured_response, 'dict') else structured_response
                }
            }
        
        except Exception as e:
            if verbose:
                print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_fallback_response(self, query: str, content: str, evm: Optional[str], solana: Optional[str]) -> PortfolioAnalysisResponse:
        """Create a fallback response when structured parsing fails."""
        from schemas import (
            Step1RequestParsing, Step2DataFetching, Step3CompositionAnalysis,
            Step4PerformanceAnalysis, Step5ReportGeneration, TokenHolding, TopToken
        )
        
        return PortfolioAnalysisResponse(
            step1_requestParsing=Step1RequestParsing(
                userQuery=query,
                timeframe="unknown",
                walletAddresses={"evm": evm, "solana": solana},
                parsingReasoning="Unable to parse timeframe from query"
            ),
            step2_dataFetching=Step2DataFetching(
                toolsUsed=["get_historical_portfolio_data"],
                portfolio=[],
                fetchingNotes="Data fetching attempted but structured response parsing failed"
            ),
            step3_compositionAnalysis=Step3CompositionAnalysis(
                totalAmountUsd=0,
                topHoldings=[],
                topGainers=[],
                topLosers=[],
                compositionSummary="Unable to analyze composition"
            ),
            step4_performanceAnalysis=Step4PerformanceAnalysis(
                periodStartValue=0,
                periodEndValue=0,
                totalDeltaUSD=0,
                totalDeltaPercentage=0,
                tokensOrderedByPerformance=[],
                performanceSummary="Unable to analyze performance"
            ),
            step5_reportGeneration=Step5ReportGeneration(
                confidence="low",
                error="llm_error",
                keyTakeaways=["Analysis incomplete due to parsing error"],
                recommendations=[],
                limitations=["Structured response parsing failed", "Using fallback response"],
                summary=f"{content}\n\nThis is not financial advice."
            )
        )
    
    def print_analysis(self, result: Dict):
        """Pretty print analysis results."""
        print("\n" + "=" * 70)
        print("📊 PORTFOLIO ANALYSIS RESULTS")
        print("=" * 70)
        
        question = result.get("question", "Unknown")
        structured = result.get("response", {}).get("structuredResponse", {})
        
        print(f"\n🔬 Question: {question}\n")
        
        # Step 1: Request Parsing
        step1 = structured.get("step1_requestParsing", {})
        print("STEP 1: Request Parsing")
        print("-" * 70)
        print(f"Timeframe: {step1.get('timeframe', 'unknown')}")
        print(f"Reasoning: {step1.get('parsingReasoning', 'N/A')}")
        print()
        
        # Step 2: Data Fetching
        step2 = structured.get("step2_dataFetching", {})
        print("STEP 2: Data Fetching")
        print("-" * 70)
        print(f"Tools Used: {', '.join(step2.get('toolsUsed', []))}")
        print(f"Tokens Found: {len(step2.get('portfolio', []))}")
        print(f"Notes: {step2.get('fetchingNotes', 'N/A')}")
        print()
        
        # Step 3: Composition Analysis
        step3 = structured.get("step3_compositionAnalysis", {})
        print("STEP 3: Portfolio Composition")
        print("-" * 70)
        print(f"Total Value: ${step3.get('totalAmountUsd', 0):,.2f}")
        print(f"Top Holdings: {', '.join(step3.get('topHoldings', []))}")
        print(f"Summary: {step3.get('compositionSummary', 'N/A')}")
        print()
        
        # Step 4: Performance Analysis
        step4 = structured.get("step4_performanceAnalysis", {})
        print("STEP 4: Performance Analysis")
        print("-" * 70)
        print(f"Start Value: ${step4.get('periodStartValue', 0):,.2f}")
        print(f"End Value: ${step4.get('periodEndValue', 0):,.2f}")
        print(f"Change: ${step4.get('totalDeltaUSD', 0):,.2f} ({step4.get('totalDeltaPercentage', 0):.2f}%)")
        print(f"Summary: {step4.get('performanceSummary', 'N/A')}")
        print()
        
        # Step 5: Report Generation
        step5 = structured.get("step5_reportGeneration", {})
        print("STEP 5: Final Report")
        print("-" * 70)
        print(f"Confidence: {step5.get('confidence', 'unknown').upper()}")
        print(f"Error Status: {step5.get('error', 'unknown')}")
        print(f"\nKey Takeaways:")
        for i, takeaway in enumerate(step5.get('keyTakeaways', []), 1):
            print(f"  {i}. {takeaway}")
        print(f"\nRecommendations:")
        for i, rec in enumerate(step5.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
        print(f"\nSummary:")
        print(f"  {step5.get('summary', 'N/A')}")
        print("=" * 70 + "\n")


def main():
    """Main function to run the portfolio agent."""
    # Initialize the agent
    agent = PortfolioAgent(model_name="gpt-4", temperature=0.3)
    
    # Example usage
    questions = [
        "Review my portfolio",
        "Give me a daily report",
        "Analyze my portfolio and show which tokens are underperforming",
        "How has my portfolio changed in the last 7 days?",
        "What is my total profit/loss this month?",
    ]
    
    wallet_addresses = {
        "evm": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # Example address
        "solana": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # Example address
    }
    
    print("\n" + "🚀 PORTFOLIO AGENT" + "\n")
    
    # Process each question
    for i, question in enumerate(questions, 1):
        try:
            print(f"\n[{i}/{len(questions)}] Processing: {question}")
            result = agent.analyze(
                query=question,
                evm_wallet_address=wallet_addresses.get("evm"),
                solana_wallet_address=wallet_addresses.get("solana"),
                verbose=True
            )
            
            agent.print_analysis(result)
            
        except Exception as e:
            print(f"❌ Error processing question '{question}': {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
