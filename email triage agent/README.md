# Email Triage Agent

A LangChain agent that triages incoming emails, suggests a priority, drafts a professional response, and proposes next actions.

## Installation

```bash
cd "email triage agent"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-example .env
```

## Usage (Python)

```python
from main import EmailTriageAgent

agent = EmailTriageAgent(provider="openai", model_name="gpt-4o-mini")
result = agent.chat(
    message="Triage: Subject: Invoice mismatch. We need corrected totals by EOW.",
    verbose=True,
)
agent.print_result(result)
```

## CLI

```bash
python main.py -m "Subject: Outage. Service is down for EU users."
python main.py
```

## Project layout

```
email triage agent/
├── main.py
├── llm_factory.py
├── tools.py
├── schemas.py
├── example.py
├── requirements.txt
├── .env-example
└── README.md
```
