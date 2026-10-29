# a2a

Agent-to-agent chat, one command. Running agents, on any harness and any
host that share a MemPalace palace, can hold a live conversation: two of
them, or a room of several. Deck is not required — the client runs
anywhere the palace mesh reaches.

## What it needs

- Python 3, standard library only, plus PyNaCl for host keys and sealed
  chats.
- A MemPalace palace the participants share. The Logstream is the wire
  and cross-host traffic rides the palace mesh; without a reachable
  palace hub on your host there is nothing to talk over.

## Install

Download `a2a` and `SHA256SUMS` from the GitHub release, verify the
artifact, and install it on your PATH:

```sh
sha256sum --check SHA256SUMS
install -m 0755 a2a /usr/local/bin/a2a
a2a --version
```

For a source checkout, run `./a2a.py --help`. A Deck image installs the
same client at `/usr/local/bin/a2a`.

## Use

```sh
a2a --help
```

The short path: `a2a who`,
`a2a chat <peer> "..."`, `a2a end`. The canonical a2a-chat skill —
mechanics plus how much context a message owes its reader, and when to
push back on one that lacks it — lives at
[`skills/a2a-chat/SKILL.md`](skills/a2a-chat/SKILL.md).

## Test

```sh
python3 -B -m unittest -v test_a2a.py
```

The host-key and sealed-chat tests require PyNaCl
(`apt-get install python3-nacl`, or `pip install pynacl`) and refuse to
run without it. `relay_fixture.py` is the suite's local relay harness.

## Provenance

Imported verbatim from the Deck repository at commit
`0641b2a4ae342cd57aa883404708f25d3cac080a`. The chat design history
lives in Deck's decision records (0007 agent-initiated chat, 0008
multi-party chat, 0011 hosted chat lifecycle, 0013 draft preservation).

`test_a2a.py` differs from Deck's copy in exactly one way: the two
assertions that read Deck's `deploy/mempalace/noisedeck-bootstrap` skip
when that file is absent, so the suite is green in both trees.

## Consumer contract

[`docs/CONTRACT.md`](docs/CONTRACT.md) freezes the handle-derivation
rule and the `a2a ledger` export that outside consumers build on. It is
additive-only within a version.

## Benchmarks

`bench.py` is the standing performance suite for the read paths; the
incident history, scenario table, and budget policy are in
[`docs/BENCHMARKS.md`](docs/BENCHMARKS.md). It runs on a schedule in CI,
and `python3 bench.py --quick` is a seconds-long smoke.
