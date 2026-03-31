"""Example: GTM pipeline."""
import os

from dotenv import load_dotenv

from main import GTMLaunchAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

if __name__ == "__main__":
    agent = GTMLaunchAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.run_pipeline(
        product_brief="Developer tool: managed test environments from pull requests.",
        extra_context="Competitors: ephemeral env vendors. Differentiator: lower cost via sleep/wake.",
        verbose=True,
    )
    agent.print_pipeline(r)
