"""The regression gate: OrderBot must get refund-eligibility questions right.

Run it against the buggy agent (default) to watch it fail:
    pytest test_agent_quality.py -v

Run it against the fixed agent to watch it pass:
    ORDERBOT_FIXED=1 pytest test_agent_quality.py -v
"""

import os

import mlflow

from orderbot.agent import build_agent
from orderbot.eval_dataset import EVAL_DATASET
from orderbot.judge import refund_policy_correctness

mlflow.set_experiment("orderbot-quality-gate")
mlflow.anthropic.autolog()


def test_refund_policy_answers_are_correct():
    fixed = os.environ.get("ORDERBOT_FIXED") == "1"
    agent = build_agent(fixed=fixed)

    with mlflow.start_run(run_name="fixed" if fixed else "buggy"):
        results = mlflow.genai.evaluate(
            data=EVAL_DATASET,
            predict_fn=agent,
            scorers=[refund_policy_correctness],
        )

    assert results.passed, results.reason
