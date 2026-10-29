#!/usr/bin/env python3
"""Standing performance benchmarks for the a2a client and its relay path.

Every latency fix in the client's history was found reactively in
production (issue records in docs/BENCHMARKS.md): reads whose cost grew
with the palace, caches invalidated by their own pass duration, and a
fold killed by its subprocess budget and parsed as empty delivery. This
module is the suite that catches those classes before they ship.

Each scenario seeds the in-memory relay the test suite uses (imported
from test_a2a, including its MemPalace relay-version profiles) and
measures the client's real fold functions. Two metrics matter: wall
time, and the number of list pages a read issues — page count is
deterministic, so it is asserted tightly in CI while time budgets carry
headroom. Run: python3 bench.py [--quick] [--json]. Exit is nonzero when
any budget is breached or any correctness assertion fails.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import a2a  # noqa: E402
import test_a2a  # noqa: E402

PAGE_MAX = 500

# Time budgets carry headroom over measured baselines (docs/BENCHMARKS.md):
# a breach means an order-of-magnitude regression, not scheduler noise.
WALL_BUDGETS = {1_000: 4.0, 5_000: 12.0, 20_000: 45.0}
QUICK = False
RESULTS: list[dict] = []


def record(name: str, events: int, wall: float, pages: int,
           budget_wall: float | None, budget_pages: int | None, note: str = "") -> None:
    ok = True
    if budget_wall is not None and wall > budget_wall:
        ok = False
    if budget_pages is not None and pages > budget_pages:
        ok = False
    RESULTS.append({"scenario": name, "events": events, "seconds": round(wall, 3),
                    "pages": pages, "budget_seconds": budget_wall, "budget_pages": budget_pages,
                    "ok": ok, "note": note})
    if not ok:
        print(f"FAIL {name}: {wall:.3f}s > {budget_wall}s or {pages} pages > {budget_pages}", file=sys.stderr)


def pages_budget(events: int) -> int:
    # A cold read walks the room once: ceil(N/PAGE_MAX) pages, plus room for
    # the smaller filtered lists the fold also issues.
    return math.ceil(events / PAGE_MAX) + 40


@contextmanager
def bench_relay(profile: str = "3.10"):
    """The suite's harness, minus unittest: in-memory relay, private state,
    hostA, no courier. profile picks the relay's listing semantics."""
    refuses = profile == "3.8-refuses-order"
    ignores = profile == "3.10-ignores-order"
    ls = test_a2a.FakeLogstream(refuses_order=refuses, ignores_order=ignores)
    tmp = tempfile.TemporaryDirectory()
    patches = [
        mock.patch.object(a2a, "_rpc", side_effect=lambda tool, args, timeout=30.0: ls.call(tool, args)),
        mock.patch.object(a2a, "_ORDER_REFUSED", False, create=True),
        mock.patch.object(a2a, "STATE_DIR", Path(tmp.name)),
        mock.patch.object(a2a, "KEY_DIR", Path(tmp.name) / "host"),
        mock.patch.object(a2a.socket, "gethostname", return_value="hostA"),
        mock.patch.dict(__import__("os").environ, {"A2A_NO_COURIER": "1", "A2A_TMUX_SOCKETS": "/s"}),
    ]
    try:
        for p in patches:
            p.start()
        a2a.key_init()
        a2a._PUBLIC_KEYS_CACHE.update(at=0.0, keys={})
        a2a._LEGACY_IDS_CACHE.update(loaded=False)
        a2a._HOSTS_CACHE.update(at=0.0, key=None, hosts={}, auth={}, projects={}, project_names={})
        reset_folds()
        yield ls
    finally:
        for p in reversed(patches):
            p.stop()
        tmp.cleanup()


def reset_folds() -> None:
    a2a._PRESENCE_STATE_MEMO.update(derived=None, at=0.0)
    a2a._EVENTS_SNAPSHOT = None


def seed(ls, presence: int, chats: int, chat_events: int) -> None:
    """Well-formed events written straight to the store: seeding measures
    nothing, so it skips sealing; fold cost is what the read path pays."""
    n = 0

    def ev(**kw):
        nonlocal n
        n += 1
        e = {"id": f"evt_{n:06d}", "seq": n,
             "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(n // 1000)),
             "type": kw.get("type", "agent.online"), "stream": kw.get("stream", "a2a"),
             "room": kw.get("room", "presence"), "from_agent": kw.get("from_agent", "claude-0001"),
             "to_agent": None, "correlation_id": None, "status": "ready",
             "body": "", "metadata": kw.get("metadata", {})}
        ls.events.append(e)
        return e

    for i in range(presence):
        ev(from_agent=f"agent-{i % 97:04d}", metadata={"handle": f"agent-{i % 97:04d}", "host": "hostA", "harness": "claude"})
    for c in range(chats):
        cid = f"chat-bench-{c:04d}"
        ev(type="chat.invite", room="chat", from_agent="claude-0001", correlation_id=cid,
           to_agent="*", body=f"invite {c}")
        for m in range(chat_events):
            ev(type="chat.message", room="chat", from_agent=f"agent-{m % 97:04d}",
               correlation_id=cid, to_agent="*", body=f"message {c}/{m}")


def measure(ls, fn) -> tuple[float, int]:
    before = len(ls.listings)
    reset_folds()
    start = time.perf_counter()
    fn()
    wall = time.perf_counter() - start
    return wall, len(ls.listings) - before


def scenario_folds(n: int) -> None:
    chat_events_each = 8
    with bench_relay() as ls:
        seed(ls, presence=n, chats=max(n // 40, 1), chat_events=chat_events_each)
        total = n + (n // 40) * (1 + chat_events_each)
        wall, pages = measure(ls, lambda: a2a.handle_for_session("74300000-1111", "claude"))
        record(f"presence-cold@{n}", total, wall, pages, WALL_BUDGETS[n], pages_budget(n))
        before = len(ls.listings)
        start = time.perf_counter()
        a2a.handle_for_session("74300000-2222", "claude")
        record(f"presence-warm@{n}", total, time.perf_counter() - start,
               len(ls.listings) - before, WALL_BUDGETS[n], 40)
        wall, pages = measure(ls, lambda: a2a.ledger("agent-0001"))
        record(f"ledger-cold@{n}", total, wall, pages, WALL_BUDGETS[n], pages_budget(n))
        wall, pages = measure(ls, lambda: a2a.ledger_index())
        record(f"index@{n}", total, wall, pages, WALL_BUDGETS[n], pages_budget(n))


def scenario_relay_profiles(n: int = 1_000) -> None:
    with bench_relay("3.8-refuses-order") as ls:
        seed(ls, presence=n, chats=n // 40, chat_events=4)
        wall, pages = measure(ls, lambda: a2a.handle_for_session("74300000-1111", "claude"))
        record(f"presence-cold@{n}[3.8-refuses-order]", n, wall, pages, WALL_BUDGETS[n], pages_budget(n),
               note="a relay that rejects order=asc still reads within budget via the fallback")
    # A relay that accepts order=asc and lists newest-first anyway is lying
    # about append order; the client refuses the read rather than fold a
    # reordered stream (the guard is the contract, not a performance bug).
    with bench_relay("3.10-ignores-order") as ls:
        seed(ls, presence=n, chats=n // 40, chat_events=4)
        refused = False
        try:
            reset_folds()
            a2a.handle_for_session("74300000-1111", "claude")
        except a2a.LogstreamError:
            refused = True
        RESULTS.append({"scenario": f"presence-cold@{n}[3.10-ignores-order]", "events": n,
                        "seconds": 0.0, "pages": 0, "budget_seconds": None, "budget_pages": None,
                        "ok": refused,
                        "note": "a lying relay is refused loudly, never folded"})


def scenario_courier_idle() -> None:
    with bench_relay() as ls:
        seed(ls, presence=200, chats=5, chat_events=4)
        state: dict = {}
        a2a.prime_cursor(state)
        before_appends = sum(1 for e in ls.events if e["type"].startswith("courier."))
        before = len(ls.listings)
        start = time.perf_counter()
        with mock.patch.object(a2a, "deliver", return_value="none"):
            a2a.courier_once(state, "hostA", verbose=False)
        appends = sum(1 for e in ls.events if e["type"].startswith("courier.")) - before_appends
        record("courier-idle-scan", len(ls.events), time.perf_counter() - start,
               len(ls.listings) - before, 8.0, 60,
               note=f"heartbeats written={appends}; an idle scan writes at most one")


def scenario_budget_refusal() -> None:
    """The class that once delivered no mail: a fold that crosses its read
    budget must fail loudly, never resolve to an empty ledger."""
    with bench_relay() as ls:
        seed(ls, presence=500, chats=10, chat_events=4)

        def stall(tool, args, timeout=30.0):
            if tool == "mempalace_event_list" and args.get("room") == "chat":
                raise a2a.LogstreamError("timed out", code=-32099)
            return ls.call(tool, args)

        with mock.patch.object(a2a, "_rpc", side_effect=stall):
            reset_folds()
            failed_loudly = False
            try:
                a2a.ledger("agent-0001")
            except Exception:
                failed_loudly = True
            RESULTS.append({"scenario": "budget-refusal", "events": len(ls.events),
                            "seconds": 0.0, "pages": 0, "budget_seconds": None, "budget_pages": None,
                            "ok": failed_loudly,
                            "note": "a stalled chat read raises; it never returns an empty ledger"})


def main() -> int:
    global QUICK
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="smoke sizes only")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()
    QUICK = args.quick
    sizes = [1_000] if QUICK else [1_000, 5_000, 20_000]
    for n in sizes:
        scenario_folds(n)
    if not QUICK:
        scenario_relay_profiles()
        scenario_courier_idle()
    scenario_budget_refusal()
    if args.as_json:
        print(json.dumps(RESULTS, indent=2))
    else:
        print(f"{'scenario':44} {'events':>7} {'seconds':>8} {'pages':>6}  ok")
        for r in RESULTS:
            print(f"{r['scenario']:44} {r['events']:>7} {r['seconds']:>8.3f} {r['pages']:>6}  {'PASS' if r['ok'] else 'FAIL'}")
    return 1 if any(not r["ok"] for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
