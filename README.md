# agentic-qa-mcp

### Agentic QA Workflows — Jira/Playwright → Multi-Agent DB→API→Excel

**Two proof-of-concept implementations of Agentic AI applied to QA Engineering — evolving from a single Jira-driven browser-testing agent pair to a full sequential, multi-agent validation workflow.**

Built hands-on as part of an ongoing exploration into Agentic QA: how far AI agents can go beyond "generating test scripts" and actually *participate* in the QA process — retrieving data, understanding contracts, executing validations, and making decisions based on each other's results. Everything here uses real, production-grade, publicly available tools (Microsoft AutoGen, MCP, NVIDIA-hosted models) — no custom platform, nothing mocked.

---

![Architecture diagram: two agent pipelines — Jira to BugAnalyst to AutomationAgent to Playwright, and MySQL to DatabaseAgent to APIAgent to ExcelAgent](assets/architecture.svg)

---

## 🧠 In plain English — what does this actually do?

Imagine two coworkers on your QA team:

1. **A Bug Analyst** who opens Jira every morning, reads the last few bugs filed against the app, spots the pattern in what keeps breaking, and writes up a step-by-step manual test plan to catch it early next time.
2. **An Automation Engineer** who takes that plan and turns it into an actual browser test — clicking through the app, filling forms, taking screenshots, and reporting pass/fail.

This project replaces both of those humans with **AI agents** that do the same job, end-to-end, without a person in the loop. One agent talks to Jira. The other agent drives a real Chrome browser. They talk to *each other* — the analyst hands off its findings, the automation agent executes them — and the framework captures screenshots and logs as proof of what happened.

A second, more advanced workflow in the same project chains **three** agents together: one pulls a test user from a MySQL database, a second uses that data to call a real REST API (register + login), and a third logs the verified result into an Excel report — a fully automated, database-driven regression check.

You don't need to be technical to get the headline: **this is software that tests other software, by reasoning about real bug data instead of following a fixed script.**

---

## 🏗️ How it works (for technical reviewers)

This is built on the **[AutoGen AgentChat](https://microsoft.github.io/autogen/)** framework (Microsoft's open-source multi-agent orchestration library) combined with the **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** — the emerging open standard that lets an LLM safely call external tools (Jira, a browser, a database, a spreadsheet) through a consistent interface.

### Scenario 1 — Bug-Driven Smoke Test Generation (`scenario1.py`)
*POC #1 — the original Jira + Playwright Agentic QA experiment.*


```
Jira (via MCP)  →  BugAnalyst Agent  →  handoff  →  AutomationAgent  →  Playwright (via MCP)  →  Screenshots
```

| Agent | Tooling (MCP server) | Responsibility |
|---|---|---|
| **BugAnalyst** | [`mcp-atlassian`](https://github.com/sooperset/mcp-atlassian) | Pulls the 5 most recent bugs from a Jira project, detects recurring failure patterns, and drafts a precise, step-by-step smoke-test scenario (exact URLs, actions, expected results). |
| **AutomationAgent** | [`@playwright/mcp`](https://github.com/microsoft/playwright-mcp) | Converts that plan into live browser actions using Microsoft's official Playwright MCP server, executes it against the real application in a headed browser, waits on the actual UI state (not fixed sleeps), and captures screenshots as evidence. |

The two agents run inside a `RoundRobinGroupChat` and hand off control using a plain-text signal (`"HANDOFF TO AUTOMATION"`), so each agent does exactly one job and stops — this keeps the run deterministic and auditable instead of an open-ended chat loop.

### Scenario 2 — Database-to-API Regression Pipeline (`framework/scenario2.py`)
*POC #2 — the next evolution: a sequential, multi-agent User Registration Validation workflow.*


```
MySQL (via MCP)  →  DatabaseAgent  →  APIAgent (REST + filesystem MCP)  →  ExcelAgent (via MCP)  →  Report
```

| Agent | Tooling (MCP server) | Responsibility |
|---|---|---|
| **DatabaseAgent** | [`mysql_mcp_server`](https://github.com/designcomputer/mysql_mcp_server) | Pulls a real user record from MySQL and prepares a unique, test-ready registration payload. |
| **APIAgent** | [`dkmaker-mcp-rest-api`](https://github.com/dkmaker/mcp-rest-api) + filesystem MCP | Reads an existing Postman collection to learn the real API contract, builds a compliant request body from the database data, executes registration + login calls, and reports the real response status. |
| **ExcelAgent** | [`@negokaz/excel-mcp-server`](https://github.com/negokaz/excel-mcp-server) | Only writes a result row to a live Excel workbook once the API step reports a **genuine** success — not just "attempted." |

The `framework/agentFactory.py` and `framework/mcp_config.py` modules exist so every new agent/workflow reuses the same MCP wiring instead of hand-rolling server config each time — this is the difference between a one-off script and a reusable framework.

### Why this is a real framework, not a demo hack

- **No mocked tools.** Every integration (Jira, Playwright, MySQL, REST, Excel, filesystem) is a real, community/vendor-maintained MCP server — the same ones a production team would install.
- **Deterministic handoffs.** Agents use explicit termination phrases and role boundaries so behavior is repeatable and reviewable, not an unbounded chat.
- **Evidence-first.** The automation agent is explicitly instructed to wait for real UI state changes and capture screenshots, so every run leaves an an audit trail (`/evidence` folder has samples of the actual output: screenshots, DOM snapshots, and console logs from a live run).
- **Model-agnostic.** Points at any OpenAI-compatible endpoint (this build used NVIDIA's hosted model catalog) — swap `BASE_URL`/`MODEL_NAME` for OpenAI, Azure, or a local model with no code changes.

---

## 📂 Repository structure

```
agentic-qa-mcp/
├── scenario1.py              # Jira bugs → AI-generated smoke test → executed in Playwright
├── framework/
│   ├── scenario2.py           # MySQL → API registration/login → Excel reporting pipeline
│   ├── agentFactory.py        # Reusable factory for building MCP-backed agents
│   └── mcp_config.py          # Centralized MCP server configuration (MySQL, REST, Excel, filesystem)
├── evidence/                  # Sample artifacts captured from a real automated run
│   ├── 01_automation_evidence_cart.png  # Screenshot captured by the AutomationAgent mid-flow
│   ├── sample_page_snapshot.yml         # Accessibility-tree snapshot Playwright MCP uses to "see" the page
│   └── sample_console.log               # Captured browser console output during the run
└── requirements.txt           # Full dependency list (AutoGen, MCP SDK, Playwright, etc.)
```

> Local virtual environment, IDE metadata, OS files, and the full raw run-log archive were removed before publishing — this repo contains only the source code and a representative sample of run evidence.

---

## ⚙️ Running it yourself

1. `pip install -r requirements.txt` (Python 3.11+ recommended; project was built against 3.14)
2. Install the MCP servers the agents call at runtime — these are fetched on demand via `npx`/`uvx`, so no separate install step is required beyond having Node.js and `uv` available.
3. Set real credentials for whichever scenario you run:
   - **Scenario 1:** an LLM API key, plus `JIRA_URL` / `JIRA_USERNAME` / `JIRA_API_TOKEN` for your Jira instance.
   - **Scenario 2:** an LLM API key, plus MySQL connection details in `framework/mcp_config.py`.
4. Run: `python scenario1.py` or `python -m framework.scenario2`

All secrets in this repo are placeholders (`<API_KEY>`, `<JIRA_API_TOKEN>`, etc.) — nothing sensitive is committed. Point them at your own Jira project, database, and target application to reproduce the workflow end-to-end.

---

## 🚀 Where this goes next

This was built as a working proof-of-concept, and the roadmap below is exactly what I'd tackle to take it from "personal project" to "CI-grade tooling":

- **CI integration** — trigger `scenario1.py` on a schedule or on new Jira bug labels, and publish the screenshot/log evidence as a pipeline artifact automatically.
- **Structured reporting** — replace console output with a proper Allure/HTML report generated from each agent's transcript.
- **Guardrails & cost control** — add max-turn and token-budget limits per agent so a stuck agent can't loop indefinitely against a paid LLM endpoint.
- **Multi-project Jira support** — parameterize `JIRA_PROJECTS_FILTER` so the same BugAnalyst can triage several products.
- **Assertion layer** — have the AutomationAgent emit structured pass/fail results (not just prose) so results can feed a dashboard instead of only a chat transcript.
- **Secrets management** — move all credentials to environment variables / a secrets manager (e.g., Vault, AWS Secrets Manager) instead of source placeholders.

---

## 👤 About this project

This is part of an ongoing Agentic AI journey in QA Engineering. It started with a Jira + Playwright agent pair (POC #1) exploring whether agents could turn real bug data into executed browser tests. This repo's second workflow (POC #2) pushes further — a sequential multi-agent pipeline where a Database Agent, API Testing Agent, and Excel Agent pass context to one another, validate real outcomes, and only persist results once the required criteria are actually satisfied.

The goal isn't "AI generating test scripts." It's AI agents that can genuinely participate in the QA process — retrieving data, understanding API contracts, executing validations, making decisions from prior results, and stopping only when the workflow's real success criteria are met.

Next steps: more autonomous QA agents, stronger validation/decision logic, and reusable MCP-based capabilities that operate across different layers of the testing stack.

Feedback, questions, and forks are welcome.

**License:** [MIT](LICENSE) — free to use, modify, and build on.

---

<sub>Suggested GitHub topics: `ai-agents` `autogen` `mcp` `model-context-protocol` `test-automation` `sdet` `playwright` `qa-engineering` `llm-agents`</sub>
