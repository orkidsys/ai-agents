# Interview Prep Agent

A LangChain agent for interview practice: behavioral answers (STAR), technical discussion framing, light system-design coaching, and follow-up drills—with optional structured JSON output.

## Installation

```bash
cd "interview prep agent"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-example .env
```

## Usage (Python)

```python
from main import InterviewPrepAgent

agent = InterviewPrepAgent(provider="openai", model_name="gpt-4o-mini")
result = agent.chat(
    message="Staff engineer loop. How do I answer: Tell me about a project that failed?",
    verbose=True,
)
agent.print_result(result)
```

## CLI

```bash
python main.py -m "Practice: explain idempotency in APIs with examples."
python main.py
```

## Project layout

```
interview prep agent/
├── main.py
├── llm_factory.py
├── tools.py
├── schemas.py
├── example.py
├── requirements.txt
├── .env-example
└── README.md
```
