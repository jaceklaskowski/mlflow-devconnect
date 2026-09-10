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
from orderbot.evaluate import run_eval
from orderbot.judge import refund_policy_correctness

PASS_RATE_THRESHOLD = 1.0

mlflow.set_experiment("orderbot-quality-gate")
mlflow.anthropic.autolog()


def test_refund_policy_answers_are_correct():
    fixed = os.environ.get("ORDERBOT_FIXED") == "1"
    agent = build_agent(fixed=fixed)

    df, pass_rate = run_eval(
        predict_fn=agent,
        dataset=EVAL_DATASET,
        judge=refund_policy_correctness,
        run_name="fixed" if fixed else "buggy",
    )

    failures = df[df["judge_verdict"] != "yes"]
    assert pass_rate >= PASS_RATE_THRESHOLD, (
        f"refund policy pass rate {pass_rate:.0%} is below {PASS_RATE_THRESHOLD:.0%}\n"
        f"{failures[['question', 'output', 'judge_rationale']].to_string()}"
    )
