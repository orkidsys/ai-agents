# Frontend Developer Agent

Expert frontend developer specializing in modern web technologies, React/Vue/Angular frameworks, UI implementation, and performance optimization.

## Personality

You are **Frontend Developer**, an expert frontend developer who specializes in modern web technologies, UI frameworks, and performance optimization. You create responsive, accessible, and performant web applications with pixel-perfect design implementation and exceptional user experiences.

## How to use this agent

### Runnable Python agent

A LangChain-based agent that can **read**, **write**, and **list** files in a workspace and implement frontend tasks (components, styles, config) from natural language.

---

## Implemented agent (Python)

### Features

- **Tools**: `read_file`, `write_file`, `list_directory` — all paths relative to a workspace root
- **Model**: OpenAI chat model (e.g. GPT-4) with a frontend-expert system prompt
- **Output**: Final message content plus optional structured summary (task_summary, files_changed, explanation, next_steps)

### Installation

1. Create a virtual environment:

```bash
cd "frontend developer agent"
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Environment variables:

Create a `.env` file in this directory with:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Optional: `WORKSPACE_ROOT=/path/to/your/project` (defaults to current working directory when not set in code).

### Usage

**Basic:**

```python
from main import FrontendDeveloperAgent

agent = FrontendDeveloperAgent(
    model_name="gpt-4",
    temperature=0.3,
    workspace_root="/path/to/your/frontend/project",  # optional
)

result = agent.implement(
    "Add a React button component at src/components/Button.jsx that accepts label and onClick props.",
    verbose=True,
)
agent.print_result(result)
```

**Run the built-in example:**

```bash
python main.py
```

**Run example scripts:**

```bash
python example.py
```

Edit `example.py` to uncomment `example_custom_workspace()` or `example_implement_feature()`.

### API

- **`FrontendDeveloperAgent( model_name="gpt-4", temperature=0.3, workspace_root=None )`**  
  - `workspace_root`: base path for all file tools; default is `os.getcwd()`.

- **`agent.implement( request, verbose=False )`**  
  - Returns a dict: `question`, `response` (with `messages` and `content`), and optionally `structured_response` (a `FrontendTaskResponse` if parseable).

- **`agent.print_result( result )`**  
  - Pretty-prints the result.

### Project structure

```
frontend developer agent/
├── README.md         # This file
├── main.py           # FrontendDeveloperAgent and main()
├── tools.py          # read_file, write_file, list_directory tools
├── schemas.py        # FrontendTaskResponse, FileChange
├── example.py        # Usage examples
├── requirements.txt  # Python dependencies
├── .env              # OPENAI_API_KEY (create from .env.example if present)
└── .gitignore
```

### Requirements

- Python 3.10+
- OpenAI API key
- Dependencies: `langchain`, `langchain-openai`, `langchain-community`, `pydantic`, `python-dotenv`

---

## Expertise (reference)

| Area | Focus |
|------|--------|
| **Frameworks** | React, Vue, Angular — components, state management, routing |
| **Styling** | CSS3, Grid, Flexbox, custom properties, design systems |
| **Scripting** | JavaScript (ES6+), TypeScript |
| **UI/UX** | Pixel-perfect implementation, animations, responsive layouts |
| **Performance** | Bundle size, code splitting, lazy loading, Core Web Vitals |
| **Quality** | Accessibility (a11y), semantic HTML, cross-browser support |
