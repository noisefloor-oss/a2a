Use MemPalace Logstream for the review lifecycle: publish content-free
`review.claimed`, `review.tests-started`, `review.tests-completed`, and
`review.completed` events with stable project, agent, correlation, branch, and
base-commit fields. No prompts, diffs, findings, paths, terminal output, or
verdict text goes in Logstream, and no `.review` or `.reviews` scratch copies
are created. Logstream events are coordination declarations only; GitHub
remains the authoritative verdict.

Review for code quality, not only correctness: flag non-idiomatic code for
the language and codebase, and AI slop — chain-of-thought or prompt residue
leaking into comments, redundant narration of what the code obviously does,
and dead or speculative scaffolding the change does not need.

Hold every change to the floor in `AGENTS.md`, each a 🔴 blocking finding
if crossed:

- `a2a.py` stays the single module, standard library plus PyNaCl only. A
  new third-party import or a new source file is blocking unless the
  working agreement itself is amended in the same change.
- The consumer contract (`docs/CONTRACT.md`) is additive-only within a
  version. Any change to handle derivation or the `a2a ledger` export
  shapes that is not strictly additive is blocking.
- The no-PyNaCl refusal path must keep refusing: key operations and sealed
  chat exit with the explanatory error, never fail open and never succeed
  unsealed. A change that weakens that refusal is blocking.
- `test_a2a.py` differs from Deck's copy in exactly one way (the two
  bootstrap assertions skip when Deck's `deploy/mempalace/` tree is
  absent). Any new divergence is blocking unless it removes the last one.
- Read-path changes must respect the standing budgets in
  `docs/BENCHMARKS.md`; a change that lands a budget regression without
  recording the incident is blocking.
- No AI attribution anywhere (title, body, commit messages), and no
  secret-shaped content in the tree; both are also machine-scanned, so a
  slipped shape means the gate is broken, not merely the change.

Findings use the verdict format: `✅ VERDICT: APPROVE` or
`❌ VERDICT: REQUEST_CHANGES`, with 🔴 [blocking], 🟡 [nit], 🟢 [resolved],
🔵 [info] markers.
