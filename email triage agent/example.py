"""
Example run for Email Triage Agent.
"""
import os

from dotenv import load_dotenv

from main import EmailTriageAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def example_openai() -> None:
    agent = EmailTriageAgent(provider="openai", model_name="gpt-4o-mini")
    email = (
        "Subject: Bug in checkout\n\n"
        "Hi team, customers cannot complete checkout on iOS. This started after the last deploy. "
        "Please investigate ASAP."
    )
    r = agent.chat(message=f"Triage and draft a reply:\n{email}", verbose=True)
    agent.print_result(r)


if __name__ == "__main__":
    example_openai()
