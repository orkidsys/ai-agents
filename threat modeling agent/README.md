# Threat Modeling Agent (Complex)

**Five-phase** STRIDE-oriented threat model: **scope & boundaries → assets → threats → mitigations → structured JSON** (`ThreatModelReport` with `threats[]`). Chat mode exposes STRIDE/trust-boundary tools.

```bash
cd "threat modeling agent"
pip install -r requirements.txt && cp .env-example .env
python main.py --pipeline -m "Describe your system..." -v
```

Output is **design-time guidance**—validate with engineering, pentest, and org standards. Env: `THREAT_MODEL_AGENT_PROVIDER`, `THREAT_MODEL_AGENT_MODEL`.
