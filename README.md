# AI Agents (Overview)

This repository contains multiple AI-powered agents, each focused on a specific task or domain.

## Advanced multi-phase agents

These agents run **sequential specialist LLM phases** (with context passed forward) and end in a **structured JSON** synthesis step when the model complies.

### Adversarial Review Agent (Advanced)
**Analyst → Red Team → Blue Team → Chair:** neutral decomposition, stress test, mitigations, and a consolidated `AdversarialReviewReport`. Optional **chat** mode exposes rubric tools. See `adversarial review agent/README.md` (`python main.py --deep`).

### Incident Response Agent (Advanced)
**Triage → Technical → Comms → Synthesis:** stabilization-oriented steps, engineering actions, internal/external drafts, and a consolidated `IncidentResponseReport`. Optional **chat** mode for playbooks. See `incident response agent/README.md` (`python main.py --run`).

### Complex multi-phase agents (5 LLM steps + JSON)

These add **longer orchestration** (five specialist passes plus a final structured artifact):

| Agent | Phases | CLI | Output schema |
|--------|--------|-----|----------------|
| **ADR Pipeline** | Context → Options → Evaluation → Decision narrative → JSON | `adr pipeline agent/` — `python main.py --pipeline` | `ADRReport` |
| **Threat Modeling** | Scope → Assets → STRIDE → Mitigations → JSON | `threat modeling agent/` — `python main.py --pipeline` | `ThreatModelReport` |
| **GTM Launch** | ICP → Positioning → Channels → Timeline → JSON | `gtm launch agent/` — `python main.py --pipeline` | `GTMLaunchReport` |

Each folder has a **chat** mode with reference tools and the same multi-provider `llm_factory` pattern as other agents.

## Research Agent
Built with LangChain to perform multi-source research and synthesize results into structured summaries with sources.

## Portfolio Analysis Agent
Analyzes cryptocurrency portfolios across EVM and Solana wallets using schema-guided reasoning to produce structured performance and composition reports.

## Hyperliquid BTC Scalping Agent
Scalps BTC perpetuals on Hyperliquid with openai-based decisioning, using multiple strategies, technical indicators, and built-in risk management.

## LinkedIn Activity Agent
Helps professionals grow their LinkedIn presence by generating posts, comments, and content strategy ideas using schema-guided reasoning.

## Twitter / X Viral Post Agent
Drafts high-retention **X (Twitter)** posts with strong hooks, alternates, optional thread outlines, and posting tips—plus tools for **280-character** checks and viral **format** patterns (multi-provider LLM).

## QA Tester Agent
Assists with test planning, test-case design, and automation guidance for web apps and APIs, focusing on risks and edge cases.

## Bug Report Agent
Turns informal bug descriptions into structured reports (title, repro steps, expected vs actual, environment, severity hints, labels) with optional JSON output—aligned with how engineering teams triage issues.

## Wallet Poisoning Agent
Educates users about Web3 wallet/address poisoning scams and helps verify destination addresses to reduce the risk of sending funds to lookalikes.

## Smart Contract Auditing Agent
Runs an intensive, multi-agent smart contract audit (Security, Logic, Gas, Compliance) to produce severity-sorted findings and recommendations.

## Frontend Developer Agent
Implements frontend changes from natural language by reading/writing/listing files in your workspace and generating practical UI code updates.

## Voice Creation Agent
Generates speech audio from text with support for different person personas (voice profiles), including default and custom voices.

## Web Scraping Agent
Fetches and analyzes web pages via LangChain tools, with **multiple LLM backends** (OpenAI, Anthropic/Claude, Google Gemini, Vertex AI)—not locked to a single vendor.

## General Assistant Agent
A general-purpose conversational assistant with the same **multi-provider LLM** setup, plus small tools for **current time** (IANA timezones) and **safe arithmetic**—a simple base you can extend with more tools.

## Customer Support Agent
Drafts empathetic, action-oriented customer support replies, classifies issues for routing (billing, shipping, account, product quality), and can generate a structured refund-intake checklist.

## Meeting Notes Agent
Turns raw meeting notes into concise summaries with decisions, action items, and risk highlights to make follow-through easier.

## Email Triage Agent
Classifies inbound emails, estimates urgency, drafts a professional reply, and suggests concrete next actions (with optional structured JSON output).

## Technical Documentation Agent
Turns rough notes into structured technical writing (README, API docs, runbooks, changelogs, ADRs) with outline and changelog helper tools and optional structured JSON output.

## Interview Prep Agent
Helps candidates practice behavioral (STAR), technical, and high-level design interview prompts with sample talking points, drills, and delivery tips—without inventing the user’s experience.

## Sales Outreach Agent
Drafts concise outbound **email** and **LinkedIn-style** messages with hooks, CTA, follow-up ideas, and “verify before send” prompts—plus light funnel-stage and length tools (multi-provider LLM).

## Travel Planner Agent
Produces **day-by-day trip outlines** from dates, pace, budget band, and interests; includes constraint and jet-lag reminders. Does not book or verify live hours, prices, or visas (users confirm with official sources).

## Study Coach Agent
Converts notes or topics into **flashcards**, **practice questions**, and study scheduling hints using active-recall / time-box tools (multi-provider LLM).

## Move Contract Validator Agent
Validates **Move** modules (Aptos / Sui aware) using **four specialist agents**—security, logic, gas/storage, and standards/compliance—and merges their findings into a single structured report with overall risk and recommendations.

