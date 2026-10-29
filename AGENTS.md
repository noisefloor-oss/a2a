# a2a — working agreement

Single-file Python CLI (`a2a.py`, installed as `a2a`): live agent-to-agent
chat over a shared MemPalace palace — two agents or a room of several, on
any harness and any host the palace mesh reaches. Python 3 standard library
only, plus PyNaCl for host keys and sealed chats. Ground truth, in order:
[`docs/CONTRACT.md`](docs/CONTRACT.md) (the frozen consumer contract),
[`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) (the budget policy), then the
commit history. The chat design history lives in Deck's decision records
(0007 agent-initiated chat, 0008 multi-party chat, 0011 hosted chat
lifecycle, 0013 draft preservation).

## Hard rules

- **One file, standard library.** Everything ships in `a2a.py`. PyNaCl is
  the only third-party dependency: without it the sealed-chat tests skip
  and the CLI refuses key and sealed operations — that refusal is load-
  bearing, never work around it. No new dependency without amending this
  agreement.
- **The consumer contract is frozen.** The handle-derivation rule and the
  `a2a ledger` exports in `docs/CONTRACT.md` are additive-only within a
  version; outside consumers build on them. Breaking changes require a new
  contract version, never a silent edit.
- **One deliberate divergence from Deck's copy.** `test_a2a.py` differs
  from Deck's tree in exactly one way: the two assertions that read Deck's
  `deploy/mempalace/noisedeck-bootstrap` skip when that file is absent.
  Keep the suite green in both trees and keep that the only difference.
- **Read-path performance has standing budgets.** Before landing a change
  that touches the read paths, run `python3 bench.py --quick` (seconds).
  The full `bench.py` run belongs to the scheduled CI job, not per-PR
  timing assertions; incident history and budgets live in
  [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md).

## Workflow

- The full lifecycle — tasks, branches, pull requests, cross-model review,
  merge, and worktree hygiene — is owned by [`SDLC.md`](SDLC.md). Read it
  before changing task state or creating, reviewing, or merging a branch.
  PR titles are Conventional Commits with a scope from the fixed set
  defined there, and every PR merges only with a current-head
  `noise-review[bot]` APPROVE.
- CI runs the suite on every push to `main` and on pull requests, plus the
  `sdlc` gates (PR title, attribution scan, secret scan, tree hygiene) and
  the `review-gate`. The benchmark suite runs on the weekly schedule and on
  demand, uploading `benchmarks.json` as an artifact.
- Full local gate before handing off:

  ```sh
  python3 -B -m unittest -v test_a2a.py
  python3 -B bench.py --quick
  ```

  Both need PyNaCl for the sealed paths (`apt-get install python3-nacl`,
  or `pip install pynacl`). `relay_fixture.py` is the suite's local relay
  harness, exercised by the suite itself — do not run it standalone.

<!-- NOISEDECK_ASSETS_START -->
## Files for the person

Files meant for the person you work with, such as screenshots, exports and reports, go in `.deck/assets/`. Deck shows them in the Assets panel.
<!-- NOISEDECK_ASSETS_END -->
