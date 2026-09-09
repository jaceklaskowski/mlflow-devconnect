# Speaking at DevConnect Warsaw

Title: Evaluation-driven development for AI agents, with MLflow

## Abstract

Most agent development still runs on vibes: tweak a prompt, try a few inputs, hope it's better. Evaluation-driven development replaces that with a loop you can actually run in CI.

This talk walks through the loop end-to-end with MLflow: instrument an agent with tracing, find a real failure in the trace tree, turn that failure into an eval dataset, score it with LLM judges, and gate the whole thing in pytest so quality regressions fail the build.
Live demos on a small agent, plus a quick look at what changes when you move from a laptop to a self-hosted server to a managed deployment.

You'll leave knowing how to turn your production traces into an agent regression suite.

## Requirements

* Speaking at DevConnect Warsaw on Sep 15
* 20 mins including Q&A
* Much more technical (not a sales pitch)
* Live demos from real-world workloads
* the focus is on informing people so they can make the right choices
* customer stories, common misconceptions and something that feels more like a practitioner event rather than a vendor one.
* litmus test is "would someone who liked the sound of this feature go away and try it and have a 90% success rate".

## Others

* Holly suggested reviewing Jules' deck [mlflow\_oss\_eval\_deck\_L200.pdf](https://mail.google.com/mail/?ik=51097000f6&attid=0.1&permmsgid=msg-f:1873944259437415904&view=att&disp=inline) for options.
* Lizzie confirmed updating your talk details on the website and sent updated marketing asset [\_DevConnect Warsaw I Marketing Materials (1).pdf](https://mail.google.com/mail/?ik=51097000f6&attid=0.1&permmsgid=msg-f:1875165817941137832&view=att&disp=inline).
