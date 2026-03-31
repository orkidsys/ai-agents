# ADR Pipeline Agent (Complex)

**Five sequential LLM phases** for a serious **Architecture Decision Record**:

1. **Context** — problem, drivers, constraints  
2. **Options** — realistic alternatives with pros/cons  
3. **Evaluation** — explicit criteria and comparison  
4. **Decision narrative** — recommendation + consequences  
5. **Structured synthesis** — `ADRReport` JSON for tools and PRs  

Also includes a small **chat** mode with ADR template tools.

```bash
cd "adr pipeline agent"
pip install -r requirements.txt && cp .env-example .env
python main.py --pipeline -m "Your decision context..." -v
python main.py --pipeline -m "..." --constraints ./constraints.txt
```

Env: `ADR_PIPELINE_AGENT_PROVIDER`, `ADR_PIPELINE_AGENT_MODEL`.
