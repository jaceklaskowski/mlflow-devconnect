"""A small, dependency-free eval harness: run an agent over a dataset, score it
with an LLM judge, and log the results to MLflow as a run.

(`mlflow.genai.evaluate()` is a nice convenience wrapper around this same idea,
but as of mlflow 3.1 it hard-requires the `databricks-agents` package. This
does the same job with nothing beyond MLflow itself -- inputs -> predict_fn ->
judge -> aggregate -> log.)
"""

import pandas as pd

import mlflow


def run_eval(predict_fn, dataset, judge, run_name=None):
    """Run predict_fn over dataset, score each row with judge, log to MLflow.

    Returns (results_df, pass_rate).
    """
    rows = []
    with mlflow.start_run(run_name=run_name):
        for example in dataset:
            inputs = example["inputs"]
            expectations = example.get("expectations", {})
            output = predict_fn(**inputs)
            feedback = judge(inputs=inputs, outputs=output, expectations=expectations)
            rows.append(
                {
                    **inputs,
                    "output": output,
                    "expected_eligible": expectations.get("eligible"),
                    "judge_verdict": feedback.value,
                    "judge_rationale": feedback.rationale,
                }
            )

        df = pd.DataFrame(rows)
        pass_rate = (df["judge_verdict"] == "yes").mean()

        mlflow.log_metric("pass_rate", pass_rate)
        mlflow.log_metric("num_examples", len(df))
        mlflow.log_table(df, artifact_file="eval_results.json")

    return df, pass_rate
