# General Assistant Agent

A small LangChain **general-purpose assistant** with **multiple LLM backends** (OpenAI, Anthropic, Google Gemini, Vertex AI) and lightweight tools: **current time** (IANA timezones) and **safe arithmetic**.

## Installation

```bash
cd "general assistant agent"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-example .env
# Add keys for the provider you use
```

## Usage (Python)

```python
from main import GeneralAssistantAgent

agent = GeneralAssistantAgent(provider="openai", model_name="gpt-4o-mini")
result = agent.chat(message="What time is it in Europe/Berlin?", verbose=True)
agent.print_result(result)
```

## CLI

```bash
python main.py -m "What is 2 ** 10? Use the calculator."
python main.py --provider anthropic -m "Hello."
python main.py   # demo with no args
```

## Project layout

```
general assistant agent/
├── main.py
├── llm_factory.py
├── tools.py
├── schemas.py
├── example.py
├── requirements.txt
├── .env-example
└── README.md
```

## License

MIT (same spirit as other agents in this repo).
