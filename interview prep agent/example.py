"""
Example run for Interview Prep Agent.
"""
import os

from dotenv import load_dotenv

from main import InterviewPrepAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def example_openai() -> None:
    agent = InterviewPrepAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.chat(
        message=(
            "Senior frontend role. Help me answer: "
            "Describe a time you improved performance in a web app."
        ),
        verbose=True,
    )
    agent.print_result(r)


if __name__ == "__main__":
    example_openai()
