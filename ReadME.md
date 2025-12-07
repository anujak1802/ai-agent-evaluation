### 🧠 AI Agent Evaluation Platform 
A full end-to-end evaluation framework for benchmarking AI agents across multiple models, prompts, and
tasks---complete with: • FastAPI backend • PostgreSQL database •
Background evaluation worker • Real-time dashboard UI • Chart.js
visualizations (latency, score) • Multi-agent + multi-testcase
evaluation runs • Auto-refreshing frontend This system lets you run
structured evaluations across agents, compare performance, visualize
results, and track metrics like latency, cost, and accuracy scoring.

## 🚀 Features

-  ✅ 1. Agents Agents represent AI models you want to
benchmark. Each agent has: • name • model (e.g., GPT-4o, GPT-4o-mini) •
config (temperature, max_tokens, etc.) • created_at API POST /agents/ →
create agentGET /agents/ → list all agents

- ✅ 2. Testcases Testcases define the evaluation prompts. Each testcase
includes: • name • prompt • (optional) expected answer • (optional) meta
for evaluating correctness API POST /testcases/ → create testcaseGET
/testcases/ → list testcases

- ✅ 3. Evaluation Runs An evaluation run pairs multiple agents with
multiple testcases. Example: Evaluate Agent 1 and Agent 2 on testcases
1, 2, and 3. The platform automatically: • creates a new run • marks
status: pending → running → complete • triggers worker jobs • produces
per-agent-per-testcase results API POST /evals/
```
{ \"agent_ids\": \[1, 2\], \"testcase_ids\": \[1, 2, 3\], \"run_name\":
\"math-eval-benchmark-1\" } GET /evals/ → List runs
```
- ✅ 4. Evaluation Worker A background worker performs the actual
evaluation: For every (agent × testcase) pair: 1 Calls the LLM (OpenAI
or local) 2 Records response text 3 Computes: ◦ score ◦ latency_ms ◦
cost_usd 4 Writes results into database 5 Marks run as complete

- ✅ 5. Results Every model/testcase output is stored as a row: • run_id •
agent_id • testcase_id • response • score • latency_ms • cost_usd API
POST /results/ → worker uses to store outputGET /results/{run_id} →
dashboard uses to fetch chart data

### 📊 Dashboard UI Accessible at: 👉 /dashboard The dashboard displays:
Agents Table • ID • Name • Model • Created Evaluation Runs • Run name •
Status (badges: pending / running / completed) • Agent ID • Click to
view results Run Details Shows detailed per-testcase results: • Response
• Score • Latency (ms) • Cost Charts Powered by Chart.js: Score Bar
Chart Visualizes model accuracy across testcases. Latency Line Chart
Shows model speed across prompts. Automatically updates as results come
in.


🧪 Example Workflow 
 - 1️⃣ Create Agents

```
 curl -X POST http://localhost:8000/agents/ \\ -H \"Content-Type:
application/json\" \\ -d \'{ \"name\": \"math-agent-4o-mini\",
\"model\": \"gpt-4o-mini\", \"config\": {\"temperature\": 0.0} }\' 
```
- 2️⃣ Create Testcases
```
curl -X POST http://localhost:8000/testcases/ \\ -H \"Content-Type:
application/json\" \\ -d \'{ \"name\": \"addition\", \"prompt\": \"What
is 2+2?\" }\' 
```
- 3️⃣ Start Evaluation Run
```
curl -X POST http://localhost:8000/evals/ \\ -H \"Content-Type:
application/json\" \\ -d \'{ \"agent_ids\": \[1, 2\], \"testcase_ids\":
\[1, 2, 3\], \"run_name\": \"math-eval-benchmark-1\" }\'
```
-  4️⃣ Worker Computes Results Automatically or manually:
```
curl -X POST http://localhost:8000/results/ \\ -H \"Content-Type:
application/json\" \\ -d \'{ \"run_id\": 1, \"agent_id\": 1,
\"testcase_id\": 1, \"response\": \"4\", \"score\": 1.0, \"latency_ms\":
220, \"cost_usd\": 0.00015 }\'
```
### 🖥️ Run Locally (Docker)
```
docker compose up 
```
-- build Services: • api-1 → FastAPI backend • db-1 →
PostgreSQL • worker-1 → evaluation worker • dashboard → served from
/static/dashboard.html

📁 Project Structure
```
app/ 
├── api/ 
│ ├── routes_agents.py 
│ ├── routes_evals.py 
│ ├──routes_results.py 
│ └── routes_testcases.py 
├── db/ 
│ ├── models.py 
│ └── session.py 
├── workers/ 
│ └── eval_worker.py 
├── static/ 
│ └──
dashboard.html 
└── main.py
```

### 💡 Roadmap Ideas 
• ✓ Add multi-run comparison charts • ✓ Add cost trend
chart • ✓ Add filters (model, date, run name) • 🔲 Add chart exporting
(PNG/PDF) • 🔲 Add authentication • 🔲 Add distributed worker queue
(Celery, Redis) • 🔲 Add real expected-answer scoring (string
similarity, embeddings, etc.)

🙌 Contributing Issues and PRs are welcome!If you need help extending
the system, just ask.

If you want, I can also generate: ✅ A pretty Markdown version with
logos & emojis✅ A developer setup README✅ A docs site (mkdocs)Just
tell me!

You said: README.md that I can directly paste

ChatGPT said: Here is a clean, ready-to-paste README.md---no
placeholders, no explanations needed.Copy/paste it directly into your
repo.
