"""OrderBot: a tiny tool-calling customer-support agent, in two versions.

`build_agent(fixed=False)` is the buggy version shipped first: it only has the
`lookup_order` tool, so it has to eyeball refund eligibility itself from raw
dates. It quietly assumes "30 days since purchase", which is wrong for orders
whose delivery was delayed.

`build_agent(fixed=True)` gives it the `check_refund_eligibility` tool and an
explicit instruction to always defer to it. Same model, same questions,
correct answers.
"""

import anthropic
import mlflow

from orderbot.tools import TODAY, TOOL_IMPLS, TOOL_SPECS

MODEL = "claude-sonnet-5"
MAX_TURNS = 4

_TODAY_LINE = f"Today's date is {TODAY.strftime('%Y-%m-%d')}. Always give a definitive answer -- never phrase eligibility as \"if today's date is before X\"."

BUGGY_SYSTEM_PROMPT = f"""You are OrderBot, a customer support assistant for an online store.

{_TODAY_LINE}

Use the lookup_order tool to find order details and answer the customer's question,
including refund eligibility under our standard 30-day return policy (delivery date
plus 30 days). Be concise and friendly.
"""

FIXED_SYSTEM_PROMPT = f"""You are OrderBot, a customer support assistant for an online store.

{_TODAY_LINE}

You have two tools:
- lookup_order: order status, item, purchase date, delivery date.
- check_refund_eligibility: the authoritative refund decision for an order. It accounts
  for special cases (like flash-sale pricing) that aren't visible from lookup_order alone.

Never compute refund eligibility yourself -- ALWAYS call check_refund_eligibility before
telling a customer whether they can get a refund, and base your answer on its result.

Be concise and friendly.
"""


def build_agent(fixed: bool = False):
    """Return a predict_fn(question: str) -> str, suitable for mlflow.genai.evaluate."""
    system_prompt = FIXED_SYSTEM_PROMPT if fixed else BUGGY_SYSTEM_PROMPT
    tool_names = ["lookup_order", "check_refund_eligibility"] if fixed else ["lookup_order"]
    tools = [TOOL_SPECS[name] for name in tool_names]

    client = anthropic.Anthropic()

    @mlflow.trace(name="orderbot_turn", span_type="AGENT")
    def predict_fn(question: str) -> str:
        messages = [{"role": "user", "content": question}]

        for _ in range(MAX_TURNS):
            response = client.messages.create(
                model=MODEL,
                max_tokens=500,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                return "".join(
                    block.text for block in response.content if block.type == "text"
                ).strip()

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                impl = TOOL_IMPLS[block.name]
                result = impl(**block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )
            messages.append({"role": "user", "content": tool_results})

        return "Sorry, I couldn't resolve this in time -- let me get a human to help."

    return predict_fn
