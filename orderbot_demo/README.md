# OrderBot -- eval-driven development demo

A tiny Claude-powered customer-support agent ("OrderBot") with a real, reproducible
bug, wired up to demonstrate the full MLflow loop: **trace -> find a failure ->
turn it into an eval -> score with an LLM judge -> gate it in pytest.**

The demo is `just demo` away.

## The bug, in one sentence

OrderBot's refund policy has an exception -- flash-sale ("promo") orders get a
10-day refund window instead of the standard 30 days -- and that rule lives only
inside the `check_refund_eligibility` tool. The buggy version of the agent isn't
given that tool, so it falls back on the standard policy and wrongly approves a
refund that should have been denied. The fixed version is told to always call the
tool. Same model, same question, different (correct) answer.

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/).

```sh
cd orderbot_demo
export ANTHROPIC_API_KEY=...    # required -- used by both the agent and the judge
```

## Run it

```sh
# Buggy agent (default) -- RED
uv run pytest test_agent_quality.py -v

# Fixed agent -- GREEN
ORDERBOT_FIXED=1 uv run pytest test_agent_quality.py -v

# Look at the traces + eval results
uv run mlflow ui
```

`./reset_demo.sh` wipes local MLflow state (`mlruns/`, `.pytest_cache/`) for a
clean rehearsal.

## Project layout

- `pyproject.toml` / `uv.lock` -- the uv-managed dependency set (runtime deps +
  a `dev` group for `pytest`).
- `orderbot/tools.py` -- fake order DB + the two tools (`lookup_order`,
  `check_refund_eligibility`), each wrapped in `@mlflow.trace`.
- `orderbot/agent.py` -- the tool-calling loop, in buggy and fixed flavors
  (`build_agent(fixed=True/False)`).
- `orderbot/eval_dataset.py` -- 5 questions covering the trap case plus sanity
  checks (already-expired order, not-yet-delivered, cancelled).
- `orderbot/judge.py` -- a hand-rolled LLM-judge scorer using
  `mlflow.genai.scorers.scorer`.
- `orderbot/evaluate.py` -- a small dependency-free eval harness that runs the
  agent + judge over the dataset and logs the results as an MLflow run.
- `test_agent_quality.py` -- the pytest gate.

Note: `mlflow.genai.evaluate()` is the "official" convenience wrapper for this
same loop, but as of mlflow 3.1 it hard-requires the `databricks-agents` package
(which, worse, pins an old mlflow version and will silently downgrade your
environment if installed). `orderbot/evaluate.py` does the same job -- predict,
judge, aggregate, log -- with nothing beyond MLflow itself, which is both safer
for a live demo and a better illustration of what's actually happening under
the hood.
