"""Example: threat modeling pipeline."""
import os

from dotenv import load_dotenv

from main import ThreatModelingAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

if __name__ == "__main__":
    agent = ThreatModelingAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.run_pipeline(
        system_description=(
            "LLM chat product: browser client, SSE streaming, RAG over customer-uploaded PDFs in S3."
        ),
        extra_context="SOC2 roadmap; no PHI.",
        verbose=True,
    )
    agent.print_pipeline(r)
