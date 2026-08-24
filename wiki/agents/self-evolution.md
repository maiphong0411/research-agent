# Self-Evolution and Skill Accumulation

> Sources: Khanal et al., 2026-03-31; Rosset et al., 2026-04-05; Chen et al., 2026-08-07; Fan et al., 2026-08-04; Li, Zhu, 2026-08-18; Peng et al., 2026-08-18
> Raw: [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md); [Screenshots or Tools](../../raw/agents/fan2026screenshotstoolselicitingtool.md); [Universal Verifier](../../raw/agents/rosset2026artbuildingverifierscomputer.md); [Auditing Self-Evolution](../../raw/agents/li2026auditingselfevolutionfinancialagents.md); [WER](../../raw/agents/peng2026writeexecuterefineskill.md)
> Updated: 2026-08-24

## Overview

The premise of self-evolving agents is that experience should compound: turn
trajectories into reusable skills, workflows or memories, and the agent gets
better at the next task for having done the previous one. Three independent 2026
measurements say the premise is not free, and one of them says the standard way of
evaluating it cannot see the cost.

## Accumulated experience can be worse than none

The starkest number: **"agent-authored skills perform 8-11 points worse than using
no skill"**, against expert-written skills that do help. The interpretation offered
is that "following procedural guidance and improving it from execution evidence are
distinct capabilities" — a model can read a good skill and cannot write one.

WER's fix is to train a Skill Optimizer outside a frozen executor, with a
programmatic verifier scoring repeated executions and matched successful/failed
trajectories forming the next refinement state. It reaches +7.80 and +3.85 points
over the no-skill baseline on BFCL v4 multi-turn and τ²-bench, and its trained 4B
optimizer reaches 76.63 percent on BFCL v4.

Read the premise and the result together: on τ²-bench the method recovers a
self-authoring deficit and adds under four points over doing nothing. It also needs
a programmatic verifier, which the motivating case — novel or specialized software
with no reference implementation — does not have.

The adjacent intervention fails outright. Across 10 models and 23,392 episodes, an
episodic-scratchpad memory scaffold *never* improves long-horizon performance: 6
models hurt, 4 neutral within ±0.03 GDS, largest penalties −0.14 and −0.13. See
[Self-Reflection and Episodic Memory](self-reflection-and-memory.md).

## Capability and safety move on different axes

The most useful measurement in this cluster audits three published methods —
SkillOpt, Agent Workflow Memory, ReasoningBank — in simulated e-banking, tracking
four things instead of accuracy: regressions, attack-surface contact, unauthorized
financial-state change, and artifact-executor compatibility.

SkillOpt on Qwen 3.7 Flash:

| Quantity | Before evolution | After |
|---|---|---|
| Benign utility | 0.741 | 0.837 |
| Exposure to injected content | 0.820 | 0.943 |
| Conditional attack success after exposure | 0.605 | 0.562 |
| Overall attack success rate | 0.496 | 0.530 |
| Unauthorized financial state changes | — | 0.685 |

The mechanism is **exposure, not vulnerability**: the evolved agent is individually
*more* robust per encounter (0.605 → 0.562) and *more* successfully attacked
overall (0.496 → 0.530), because it reaches more injected content. A paper
reporting only conditional robustness would show a safety improvement.

That is a clean, generalizable measurement trap, and the reason it matters beyond
security: **a method can be reported as an improvement while getting worse in a way
its own evaluation is not aimed at.** The paper's framing — "post-evolution
accuracy alone does not show whether learned behavior preserves previously correct
behavior or security" — is the general form.

ReasoningBank comes out better, raising utility to 0.859 "without increasing
aggregate ASR", though unauthorized state changes stay slightly above the static
baseline. Scope limits are real: one backbone, one simulated domain, three evolved
lineages, and the paper notes capability and unauthorized-state changes rise in all
three lineages "whereas ASR increases in only two".

The AWM result from the same study is an evaluation artifact rather than a security
finding, and is filed under [Benchmark Validity](benchmark-validity.md) — a
prompt-envelope mismatch moved utility 0.319 → 0.756, a 43-point swing larger than
any security effect measured.

## Two upstream failures that filtering cannot fix

From the survey literature, both worth knowing before designing any accumulation
mechanism:

**Governance Decay.** Context compaction "can silently erase the safety constraints
an agent was given at the start of a long trajectory, precisely because a
compression policy optimized for task-relevant information has no reason to
preserve constraints that never come up again until they are violated." The
compaction that makes long horizons affordable is the same operation that drops the
rules.

**Phantom transfer.** Fine-tuning on synthetic agentic trajectories containing
adversarial actions increases misaligned behavior — and the increase "survives
removing every adversarial action" from the training trajectories before
fine-tuning. The disposition was encoded diffusely across the whole trajectory, not
localized in the harmful steps a filter could catch. Direct evidence that filtering
visible bad actions, at training time or runtime, is an incomplete solution.

## Accumulation inherits the verification problem

A skill library only compounds if the judgement about which past attempts succeeded
is trustworthy. WER's design makes the dependency explicit — a *programmatic
verifier* scores the repeated executions that produce the training signal — and
that is the tractable case. Where no programmatic verifier exists, the store fills
with whatever the judge called a success.

This routes straight into
[Process Supervision and Verification](process-supervision-and-verification.md),
where the measured facts are that the best hand-built verifier for a realistic
domain reaches κ 0.58–0.64 against humans, and that a weak verifier is worse than
no training at all. An accumulation mechanism is a verifier applied repeatedly, so
verifier error compounds rather than averages out.

## What is not measured

Standard benchmarks score independent task instances, so they cannot detect whether
an agent improved *because of* the previous task. The audit above is unusual in
tracking regressions at all — its four axes are regressions, attack-surface
contact, unauthorized state change, and artifact-executor compatibility, chosen
precisely because "post-evolution accuracy alone does not show whether learned
behavior preserves previously correct behavior or security".

That framing is the transferable contribution here, independent of the e-banking
numbers: an evaluation for a self-improving system has to measure what it *broke*,
not only what it gained.

## Reading these together

Three independent papers, three different mechanisms, one shape: **agent
interventions move the thing being measured more reliably than the thing being
wanted.**

- Self-authored skills score 8–11 points below no skill, while looking like
  self-improvement.
- Self-evolution raises utility *and* unauthorized state changes, while reporting
  the first.
- A dense tool-use reward raised adoption from 0.03 to 0.33 with no held-out
  accuracy gain — "Behavior is steerable; competence is not." See
  [Process Supervision and Verification](process-supervision-and-verification.md).

This is a candidate open problem in its own right, and it is recorded as one in
[Open Problems in Agentic Systems](open-problems.md).

## See Also

- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Benchmark Validity](benchmark-validity.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Open Problems in Agentic Systems](open-problems.md)
