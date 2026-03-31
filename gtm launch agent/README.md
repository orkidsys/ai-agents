# GTM Launch Agent (Complex)

**Five-phase** go-to-market planning: **ICP & pain → positioning & pillars → channel tactics → phased timeline → consolidated JSON** (`GTMLaunchReport`). Chat mode includes channel and readiness frameworks.

```bash
cd "gtm launch agent"
pip install -r requirements.txt && cp .env-example .env
python main.py --pipeline -m "Product, audience, constraints..." -v
```

Env: `GTM_LAUNCH_AGENT_PROVIDER`, `GTM_LAUNCH_AGENT_MODEL`. Outputs are planning drafts—validate with finance, legal, and real channel data.
