"""A tiny regression suite for OrderBot's refund-eligibility answers.

Each row is a real question a customer might ask, plus the ground-truth
eligibility decision computed straight from the policy (see tools.py).

Ground truth is nested under "ground_truth" rather than passed as top-level
expectation keys: mlflow.genai.evaluate() logs every top-level expectations
key as its own assessment, and EvaluationResult.passed/.reason treat any of
those as a pass/fail signal -- which would misread our raw `eligible`/`reason`
fields as failing assertions.
"""

EVAL_DATASET = [
    {
        "inputs": {"question": "Can I get a refund for order A1001?"},
        "expectations": {
            "ground_truth": {
                "eligible": False,
                "reason": "Delivered 40 days ago -- past the 30-day window.",
            }
        },
    },
    {
        "inputs": {"question": "I'd like to return order A1002, is that possible?"},
        "expectations": {
            "ground_truth": {
                "eligible": False,
                "reason": (
                    "It was a flash-sale (promo) purchase, which only gets a 10-day refund "
                    "window -- and it was delivered 20 days ago, so it's past that window "
                    "even though it would still be within the standard 30-day window."
                ),
            }
        },
    },
    {
        "inputs": {"question": "What's the refund status for order A1003?"},
        "expectations": {
            "ground_truth": {
                "eligible": True,
                "reason": "Delivered 2 days ago -- well within the window.",
            }
        },
    },
    {
        "inputs": {"question": "Order A1004 hasn't arrived yet, can I still get a refund?"},
        "expectations": {
            "ground_truth": {
                "eligible": False,
                "reason": "Not delivered yet, so the refund window hasn't started.",
            }
        },
    },
    {
        "inputs": {"question": "Can I be refunded for order A1005?"},
        "expectations": {
            "ground_truth": {
                "eligible": False,
                "reason": "Order was cancelled -- there's nothing to refund.",
            }
        },
    },
]
