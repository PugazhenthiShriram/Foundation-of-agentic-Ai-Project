# AdvisorAI

AdvisorAI is a mini-project implementing a multi-agent academic advising workflow with Agentic RAG concepts, deterministic academic validation, reflection/self-correction, and human approval.

## Architecture

Profile Agent → Retrieval Agent → Planning Agent → Validator → Human Advisor

## Features

- Student transcript lookup
- Degree requirement checking
- Prerequisite graph validation
- Schedule conflict checking
- Catalog retrieval
- Planning loop
- Validator/reflection loop capped at 3 iterations
- Streamlit advisor dashboard
- Evaluation test set

## Run

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The supplied mock data is self-contained. An LLM provider can be added later to turn the retrieval and planning nodes into tool-calling LLM agents.

## Important demo behavior

The system deliberately uses deterministic prerequisite and schedule functions rather than allowing an LLM to invent academic rules. This follows the project specification's hallucination-mitigation design.

## Evaluation

Run:

```bash
python evaluation/evaluate.py
```

For the full academic evaluation, extend the harness with No-RAG, Basic-RAG, and Agentic-RAG configurations and compare prerequisite accuracy, validator pass rate, citation correctness, latency, and token usage.
