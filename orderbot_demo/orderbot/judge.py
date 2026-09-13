"""A hand-rolled LLM judge, wired in as a custom mlflow.genai scorer.

No managed judge service required -- just Claude, a rubric, and a Feedback object.
"""

import anthropic
from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer

JUDGE_MODEL = "claude-haiku-4-5"

_client = anthropic.Anthropic()

PROMPT_TEMPLATE = """You are grading a customer support agent's reply about refund eligibility.

Customer question:
{question}

Ground truth: eligible={eligible}. Reason: {reason}

Agent's reply:
{output}

Does the agent's reply reach the SAME eligibility decision (yes/no) as the ground truth,
for a reason consistent with the ground truth reason? Answer on the first line with exactly
one word, "pass" or "fail". On the second line, give a one-sentence rationale.
"""


@scorer
def refund_policy_correctness(inputs, outputs, expectations) -> Feedback:
    prompt = PROMPT_TEMPLATE.format(
        question=inputs["question"],
        eligible=expectations["eligible"],
        reason=expectations["reason"],
        output=outputs,
    )
    response = _client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=100,
        # anthropic 1.x dropped `temperature` from the typed create() signature;
        # pass it through extra_body so the judge stays deterministic.
        extra_body={"temperature": 0},
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    lines = text.splitlines()
    verdict = lines[0].strip().lower() if lines else ""
    rationale = " ".join(lines[1:]).strip() or text

    passed = verdict.startswith("pass")
    return Feedback(value="yes" if passed else "no", rationale=rationale)
