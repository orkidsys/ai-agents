# Technical Documentation Agent

A LangChain agent that turns rough notes into structured technical docs: README sections, API reference snippets, runbooks, changelogs, and ADR-style write-ups. It includes small tools for outlines and changelog formatting.

## Installation

```bash
cd "technical documentation agent"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-example .env
```

## Usage (Python)

```python
from main import TechnicalDocumentationAgent

agent = TechnicalDocumentationAgent(provider="openai", model_name="gpt-4o-mini")
result = agent.chat(
    message="Write a minimal runbook for Redis failover: check health, promote replica, verify.",
    verbose=True,
)
agent.print_result(result)
```

## CLI

```bash
python main.py -m "ADR: we chose PostgreSQL over Mongo for transactional reports."
python main.py
```

## Project layout

```
technical documentation agent/
├── main.py
├── llm_factory.py
├── tools.py
├── schemas.py
├── example.py
├── requirements.txt
├── .env-example
└── README.md
```
