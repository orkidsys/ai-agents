"""Example: full ADR pipeline."""
import os

from dotenv import load_dotenv

from main import ADRPipelineAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

if __name__ == "__main__":
    agent = ADRPipelineAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.run_pipeline(
        brief="Adopt OpenTelemetry vs vendor APM only for tracing.",
        extra_constraints="Kubernetes, Java + Node services.",
        verbose=True,
    )
    agent.print_pipeline(r)
