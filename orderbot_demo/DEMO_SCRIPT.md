# Live demo script -- ~6 minutes, terminal + browser side by side

## Before you go live

1. `./reset_demo.sh` (clean slate, so run counts/trace counts in the UI aren't confusing)
1. Open a terminal tab and run `uv run mlflow ui`. Leave it running.
1. Open `http://127.0.0.1:5000` and go to the `orderbot-quality-gate` experiment
1. Open another terminal tab for `uv run pytest`
1. Font size big. Close Slack/notifications. Confirm `ANTHROPIC_API_KEY` is set in both shells.

Backup: a screen recording of a full successful run (red -> green), in case
conference wifi kills the live Anthropic calls. Cue it up muted in another tab.

---

## 1. Hook: run the gate, watch it fail (~90s)

Say: "OrderBot is a small support agent. It's got a pytest test that gates its
refund-eligibility answers. Let's just run it."

```sh
uv run pytest test_agent_quality.py -v
```

While it runs (~25s): "Five questions, an LLM judge scoring each answer against
ground truth, an assertion at the end."

It fails. Point at the pass rate (`refund_policy_correctness/mean`, usually
~40-60%) and the printed failure list -- don't read the whole diff, just land
on order **A1002**: agent said "you're eligible", judge says wrong.

## 2. Why: look at the trace (~90s)

Switch to browser, open the `buggy` run inside `orderbot-quality-gate`, open its
Traces tab, click the `orderbot_turn` trace for A1002.

Say: "One call to `lookup_order`. That's it. No eligibility check ever happened
-- because the buggy agent doesn't even have that tool. It fell back on the
generic 30-day policy and missed the flash-sale exception, which only lives
inside `check_refund_eligibility`."

This is the "found a real failure in the trace tree" beat from the abstract --
linger here, it's the visual payoff.

## 3. The fix, and rerun green (~90s)

Switch to terminal. Say: "The fix isn't a prompt tweak, it's giving the agent
the tool it needs and telling it to trust it, not guess." (Optionally flip open
`orderbot/agent.py` for 5 seconds to show `FIXED_SYSTEM_PROMPT`.)

```sh
ORDERBOT_FIXED=1 uv run pytest test_agent_quality.py -v
```

Green, 100%.

## 4. Compare, in the UI (~60s)

Back to browser: the experiment's runs table now shows `buggy` (red) and
`fixed` (100%) side by side -- select both, hit Compare if there's time. Open
the `fixed` run's A1002 trace: now there are two tool calls, and the second one
carries the real answer.

Say: "This is the loop end to end: a trace surfaces a real bug, the bug becomes
a permanent regression test, and it runs on every PR from now on -- no one gets
to re-introduce this one."

## 5. Land it (~30s)

"Production traces are the best eval dataset you'll ever have, because they're
real. You don't need a big eval framework to start -- inputs, a judge, an
assert. Ours is about 40 lines."

---

## If the API is down / wifi dies

Skip straight to the pre-recorded video, or narrate over the code: open
`orderbot/tools.py` and `orderbot/judge.py`, point at the promo-window logic
and the judge prompt, and walk through what the trace *would* show. The story
survives without live calls; it's just less fun.

## Timing budget check

Hook 1:30 + Why 1:30 + Fix 1:30 + Compare 1:00 + Land 0:30 = **6:00**, leaving
~10 min for the rest of the talk and ~4 min buffer/Q&A inside a 20-min slot.
