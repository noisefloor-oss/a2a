# a2a software development lifecycle

This document owns a2a's task, branch, pull-request, review, merge, and
worktree procedures. It follows Deck's lifecycle (`/workspace/deck/SDLC.md`)
so that an agent moving between the projects changes nothing but the
repository name. The repository `AGENTS.md` keeps the always-on floor and
routes lifecycle work here. Read that file first, then this one completely,
before changing task state or creating, reviewing, rebasing, merging, or
cleaning up branches and pull requests.

## Workflow

Work a task from `noise tasks next` or an explicitly assigned ID. Claim with
a stable owner (use your a2a handle), create the task-bound worktree through
the engine's run and `worktree provision` flow, and keep the fencing token
and revision private. Never create a second worktree by hand for a task. A
stale revision or claim conflict requires a fresh read, never an implicit
retry. Mark `in-progress` when you start and `done` only when verified
working, not merely written.

Branch, push, and open a PR as each unit of work completes; nothing finished
stays local-only. An agent may merge its own PR only after the review gate
below passes.

### Pull requests (the atomic unit)

- One idea per PR. If the title needs "and," it is two PRs. Refactors and
  behavior changes go in separate PRs.
- Commits within a PR are checkpoints; they get squashed on merge. Mainline
  is linear via squash-merge: never a merge commit, never rebase `main`.
- A PR must be green at merge time and carry a gate verdict (below).
- Read a PR with a three-dot diff (`gh pr diff <n>`, or `main...branch`),
  never two tips.

### Stacked PRs

Use `gh stack` exactly as Deck's `SDLC.md` describes, including the
checkout-free path for task-bound worktrees and the hazards it lists. Stack
only work that genuinely depends on the work below it.

### Cross-model review (the merge gate)

- Every PR is reviewed by an agent running a **different model** than the
  implementer. A fresh session of the same model does not count.
- The reviewer checks correctness against the floor in `AGENTS.md`, the
  standing requirements in `.noise/review-focus.md`, and test coverage, then
  posts the verdict as a formal review under `noise-review[bot]`.
  `.noise/review.env` on the default branch declares that identity; it is
  read from the pull request's base ref. Treat changes to either file like
  CODEOWNERS changes.
- A verdict not posted under `noise-review[bot]` does not satisfy the gate.
  Never `gh pr review` under user auth.
- Merge only with: `noise-review[bot]` APPROVE **at the exact head**, the
  required checks green, branch up to date with `main`, every thread
  resolved. Then `gh pr merge --squash`. A rebase or amended commit
  invalidates the approval; disarm an armed `--auto` before rebasing.
- A review's `commit_id` does not establish which commit was read. A changed
  head needs a fresh gate decision; Deck's bounded review-reuse procedure
  applies here unchanged.
- The maintainer may review or merge anything directly at any time.

### Driving the reviewer

One command per round:

```sh
set -a; . /workspace/review/.env; set +a
/workspace/review/bin/noise-review dispatch --pr <N> \
  --repo noisefloor-app/a2a \
  --reviewer-cmd 'codex exec --model gpt-6-astra \
      -c model_reasoning_effort="high" \
      --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -' \
  --reviewer-model gpt-6-astra \
  --focus "<what this round changed, plus what to verify>"
```

The primary reviewer is Codex on `gpt-6-astra` at high effort; the secondary
is Claude on Sonnet 5.5 (`claude-sonnet-5-5`, `--effort high`). Use the
secondary when the primary is unavailable or when the implementer used the
primary model. **`--repo` is not optional**: the shared `.env` names the
review tool's own repository. `dispatch` injects `.noise/review-focus.md`
from the base ref ahead of `--focus`, so `--focus` carries only the
per-round steer. Exit codes: `0` approved, `2` changes requested, `3` no
verdict, `4` commented, `1` operational error. Sanity-check every verdict
against the real diff; an ungrounded one is discarded and re-run. Persist no
review scratch.

### PR titles and messages

- The PR title becomes the squash-commit message: Conventional Commits with
  a required scope from `chat`, `keys`, `ledger`, `relay`, `cli`, `bench`,
  `docs`, `ci`, `sdlc`, `tasks`. Example: `feat(keys): pin host keys by
  fingerprint at first sight`.
- The title names the single thing changed. The body states the why when not
  obvious and names the task ID.
- No AI attribution, `Co-Authored-By:` trailers, or tool watermarks. The
  `attribution-scan` job fails a PR whose title, body, or commit messages
  carry a line beginning `Co-Authored-By:`, `Generated with`, `Generated
  by`, or `Assisted by`. It recognizes those shapes; the rule is wider
  than the scan.
- Project setup owns the repository-local Git identity; agents never touch
  `user.name`, `user.email`, or `user.useConfigOnly`.

### History immutability

Force-push is allowed on your own unmerged PR branch. Never force-push
`main`; correct mistakes with a new PR.

### Workspace hygiene

Keep the primary checkout on `main` between units of work. Let the engine's
claim, run, and `worktree provision` saga create task-bound branches and
worktrees. Delete a merged PR's local branch and worktree the same day;
squash-merged branches are invisible to `git branch --merged`, so cross-check
`gh pr list --state merged`. Never leave review scratch, stashes, or a stale
`.git/index.lock` behind.

## Branch rules

`main` carries the same ruleset as Deck: no deletion, no force-push, linear
history, pull requests only with squash as the sole merge method, and the
required status checks — `test`, `pr-title`, `attribution-scan`,
`secret-scan`, `tree-hygiene`, `review-gate` — strict and up to date with
`main`. Repository settings: squash only, `PR_TITLE`/`PR_BODY`, delete
branch on merge, auto-merge allowed.

## Continuous integration

The `CI` workflow runs the unittest suite on every push to `main` and on
pull requests; the `Benchmarks` workflow runs the full suite on the weekly
schedule and on demand and uploads `benchmarks.json` — timing assertions
belong there, on a quiet scheduled runner, never per pull request. The
`sdlc` workflow carries the PR-title, attribution, secret, and tree-hygiene
gates; the `review-gate` workflow enforces the current-head
`noise-review[bot]` approval. Like the sibling noise repositories, all
workflows run on the org's persistent self-hosted Linux ARM64 runners (the
repository is private, so GitHub-hosted runner jobs fail instantly on
billing), which is why every pull-request job rejects external fork
sources before any step runs.
