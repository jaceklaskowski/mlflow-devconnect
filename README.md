# OrderBot &mdash; eval-driven development demo

A tiny Claude-powered customer-support agent ("OrderBot") with a real, reproducible
bug, wired up to demonstrate the full MLflow loop: **trace -> find a failure ->
turn it into an eval -> score with an LLM judge -> gate it in pytest.**

## Just Demo

The demo is `just demo` away.

```sh
just demo
Demo state reset.
1. In one terminal: just ui
2. In another:      just test-buggy   (RED)
3. Then:            just test-fixed   (GREEN)
```

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

Start MLflow UI.

```sh
# Review traces and eval results
just ui
```

```sh
# Buggy agent (default) -- RED
just test-buggy
```

```sh
# Fixed agent -- GREEN
just test-fixed
```

## Project layout

- `orderbot/tools.py` -- fake order DB + the two tools (`lookup_order`,
  `check_refund_eligibility`), each wrapped in `@mlflow.trace`.
- `orderbot/agent.py` -- the tool-calling loop, in buggy and fixed flavors
  (`build_agent(fixed=True/False)`).
- `orderbot/eval_dataset.py` -- 5 questions covering the trap case plus sanity
  checks (already-expired order, not-yet-delivered, cancelled).
- `orderbot/judge.py` -- a hand-rolled LLM-judge scorer using
  `mlflow.genai.scorers.scorer`. No managed judge service required -- just
  Claude, a rubric, and a `Feedback` object.
- `test_agent_quality.py` -- the pytest gate. Runs the agent + judge over the
  dataset with `mlflow.genai.evaluate()` (MLflow's own eval loop -- predict,
  score, aggregate, log, all linked back to per-row traces in the run) and
  asserts on the returned `result.passed`.
