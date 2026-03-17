# QA Tester Agent

Expert QA engineer specializing in test planning, test case design, and automation for web applications and APIs.

## Personality

You are **QA Tester**, a meticulous and pragmatic quality engineer. You:
- Think in terms of risks, edge cases, and user impact
- Prefer clear, reproducible steps and unambiguous results
- Balance manual exploratory testing with automation where it adds the most value

## What this agent does

### Runnable Python agent (LangChain-based)

The QA Tester agent can:
- Inspect a codebase (via file read/list tools)
- Propose and refine test strategies and test cases
- Generate test files (e.g. Jest/Vitest/Cypress/Playwright, pytest) and basic test data
- Suggest improvements to existing tests or coverage

Implementation is modeled after your other agents (`portfolio agent`, `frontend developer agent`):
- `tools.py` – safe file tools (read/write/list)
- `schemas.py` – structured response for QA tasks (e.g. what tests were added/updated)
- `main.py` – `QATesterAgent` class with system prompt and `test()` method
- `example.py` – small example flows

---

## Usage

### Basic usage

```python
from main import QATesterAgent

agent = QATesterAgent(
    model_name="gpt-4",
    temperature=0.2,
    workspace_root="/path/to/your/app",  # project under test
)

result = agent.test(
    "Analyze the login flow and create high-level test scenarios and a Jest test file for happy path + key edge cases.",
    verbose=True,
)
agent.print_result(result)
```

### Files

```
qa tester agent/
├── README.md         # This file
├── main.py           # QATesterAgent and main()
├── tools.py          # read_file, write_file, list_directory tools
├── schemas.py        # QATaskResponse, TestCase, TestFileChange
├── example.py        # Usage examples
└── venv/             # Optional virtualenv (created for this agent)
```

