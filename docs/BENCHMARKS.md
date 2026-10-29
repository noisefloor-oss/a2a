# a2a performance benchmarks

`bench.py` is the standing suite for the client's read paths and its
relay-facing behavior. It exists because every performance fix in the
client's history was found reactively, in production:

- Deck PR #1254: a cold `inbox --peek` folded ~20 s against a relay whose
  presence room had grown past 17,000 events; the 5-second subprocess
  budget killed it, the output was parsed as empty, and **no mail was
  delivered** while the roster showed the agent alive and idle.
- Deck PR #1257: one `inbox --peek` issued 95 list calls (17.3 s) because
  reads re-paged whole rooms and bypassed both caches; reads are now
  incremental, so cost no longer grows with the palace.
- Deck PR #1170: a presence pass that takes longer than the host cache's
  validity (3.3 s over 13,800 events against a 2-second cache) left every
  reader repeating the whole pass.
- Deck PR #1193: the courier's own heartbeat (~288 `courier.scan` writes
  per host-day) was the largest single contributor to that presence-room
  growth.
- The 2026-09-29 MemPalace upgrade evaluation measured by hand, on a
  38,959-drawer snapshot, that a search behind a slow read costs 1435 ms
  on MemPalace 3.8.0 versus 574 ms on 3.10.0, and that listing order
  semantics changed between the two.

## What runs

| Scenario | What it pins |
| --- | --- |
| `presence-cold@N`, `ledger-cold@N`, `index@N` (N = 1k, 5k, 20k) | cold read cost at palace scales past today's ~17k-event rooms |
| `presence-warm@N` | the incremental reread: a second read must issue a handful of pages, not the room again (PR #1257's class) |
| `presence-cold@[3.8-refuses-order]` | a relay that rejects `order=asc` (MemPalace 3.8.0's shape) still reads within budget via the fallback |
| `presence-cold@[3.10-ignores-order]` | a relay that accepts `order=asc` and lists newest-first anyway is **refused loudly**, never folded |
| `courier-idle-scan` | an idle courier scan writes at most one heartbeat (PR #1193's class) |
| `budget-refusal` | a stalled read **raises**; it never resolves to an empty ledger (PR #1254's class) |

Two metrics: wall time and the number of list pages a read issues. Page
count is deterministic — budgets for it are tight. Time budgets carry
headroom (a breach means an order-of-magnitude regression, not scheduler
noise) and were set from measured baselines:

| Scenario | Baseline (measured on this repo's CI runner class) | Budget |
| --- | --- | --- |
| `presence-cold@1000` / `@5000` / `@20000` | 0.008 s / 0.08 s / 0.56 s | 4 / 12 / 45 s |
| `ledger-cold@1000` | 0.028 s | 4 s |
| `index@1000` | 0.024 s | 4 s |

(Baselines are from the suite's first full CI run — the self-hosted Linux
ARM64 runner, run 40255515074, 2026-10-26, all 16 scenarios passing;
`--json` emits each run's own measurements for every scheduled run.)

## Running

```sh
python3 bench.py --quick   # smoke sizes, seconds
python3 bench.py           # full suite; exit 1 on any breach
python3 bench.py --json    # machine-readable results
```

CI runs the full suite on a schedule (`schedule` + `workflow_dispatch`
in `.github/workflows/benchmarks.yaml`), not per pull request — timing
assertions belong on a quiet runner, and the deterministic page-count
assertions run in the normal test suite's territory.

## The MemPalace version axis in a lab

The suite emulates the two relay behaviors that differed across
MemPalace 3.8.0 and 3.10.0 (listing-order support). Measuring a real
palace version pair is a lab exercise: point `A2A_MCP_URL` at each
version's relay over the same seeded snapshot, run `bench.py --json`,
and compare. The upgrade evaluation's hand measurements are the
template; this suite makes the client-side half repeatable.
