# Council protocol — how the rounds run

The chair (the main session) runs the rounds. Teammates obey their round.

## Round 0 — shared evidence pass (chair, before any teammate is dispatched)

Teammates each running their own repo-wide `grep` sweeps is the largest single
cost in a council run, and it is also a *quality* problem: five specialists
each grep up a slightly different picture and then argue about different
objects.

Before Round A the chair builds one **evidence pack** for the scope — a cheap
retrieval pass (the `Explore` agent, or a Haiku/Sonnet subagent) enumerating
the relevant ledger IDs (`docs/quality/features.json`), UI controls
(`docs/quality/ui-controls.json`), spec sections, and — once code exists —
files, endpoints, contract entries, migrations, routes and admin surfaces.
Every teammate reads the pack, and greps only to chase something the pack
missed — saying so when they do.

Retrieval is not judgement. Never pay a reviewer's rate for enumeration.

## Effort per round (the chair sets this)

| Round | Effort | Why |
|---|---|---|
| 0 — evidence | `low` / `medium` | Enumeration, not judgement. |
| A — blind review | `high` | Open-ended investigation — the round that earns the money. `xhigh` only for a genuinely novel scope. |
| B — cross-examination | `medium` | A bounded response to text you have been handed, in a fixed four-part shape. |
| C — rebuttal | `medium` | Same — a bounded response to a named challenge. |
| D — ruling | `high` | Where ambiguous judgement concentrates. |

`effort` is a field on an agent's own definition file — there is no
per-invocation override — so every seat pins `effort: high` sized for Round A.
The table is guidance for the chair's own passes and for deciding whether a
scope justifies editing a seat up to `xhigh`.

## Round A — blind review

Each teammate investigates **independently**, without seeing any other
teammate's conclusions. Evidence from the repositories and ledgers, not
assumptions.

Output, in the shared finding format, grouped as:

```
BLOCKERS
REQUIRED
SHOULD
EXPERIMENT
NOT WORTH DOING   ← things in scope you deliberately decline to recommend, with why
```

The `NOT WORTH DOING` section is mandatory. A review that recommends everything
it noticed has done no prioritisation.

Close Round A with a **Position summary**: at most five lines stating what you
believe and what would change your mind.

## Round B — cross-examination

You now receive the other teammates' Round A output. You MUST produce all four:

1. **CHALLENGE** — attack at least one substantive recommendation from another
   teammate. Name the teammate, the finding, and the evidence that undermines it.
2. **OVER-ENGINEERED** — name exactly one proposal (yours included, if honest)
   that costs more than the failure it prevents.
3. **MISSED** — one risk or requirement, inside your expertise, that everyone
   else overlooked.
4. **DEFENCE** — answer every challenge aimed at you, with evidence.

Do not soften a challenge to keep the peace. Consensus is not the goal;
arguments that survive scrutiny are the goal.

## Round C — rebuttal and revision

```
RETRACTED: <finding> — <who disproved it and how>
REVISED:   <finding> — <old position> → <new position> — <what changed it>
HELD:      <finding> — <the challenge> — <why it does not land>
```

Changing your mind under good evidence is a **successful outcome**. Holding a
position you cannot defend is the failure.

## Round D — ruling (chair only)

The chair does NOT majority-vote. For every disputed item:

```
DECISION:            ACCEPT | MODIFY | EXPERIMENT | DEFER | REJECT | BLOCK RELEASE
WHY:
DISSENTING VIEW:     (name the teammate; never delete a losing argument)
AFFECTED REPOS:
REQUIREMENT IDS:     (existing VZ-… IDs touched, or new IDs to add to the ledger)
USER IMPACT:
OPERATOR IMPACT:
BUSINESS VALUE:
TECHNICAL COST/RISK:
ACCEPTANCE CRITERIA:
TEST PLAN:
```

Then one prioritised backlog:

```
P0 — release blockers
P1 — required for coherent product behaviour
P2 — high-value improvements
P3 — experiments and future opportunities
DECLINED — considered and rejected, with the reason (an owner decision if it reduces charter scope)
```

A ruling never reduces charter scope on its own. Anything that would drop an
accepted parity or integration obligation goes to `docs/OPEN_QUESTIONS.md` for
the owner.

## The chair seat

Run the chair as an **Opus session with `/advisor fable`**, not as a Fable
session. Fable steers panel selection and the Round D ruling; Opus runs the
rounds. Never add "show your reasoning" / "explain your thinking" wording to
this protocol or to a teammate prompt — it reroutes the advisor seat.

## Implementation rules (only after the owner asks for implementation)

- No code is modified during council review. Review teammates are read-only.
- When implementation is requested, assign **one repo to one implementer**.
- Two agents in one checkout need separate git worktrees.
- Each implementer obeys `AGENTS.md`: one acceptance item and one focused PR
  per session, tests that challenge the implementation, exact evidence, and
  READY_FOR_REVIEW — never self-merge, never claim VERIFIED without
  independent verification.
