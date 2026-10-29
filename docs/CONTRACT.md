# The a2a consumer contract (v1)

This document freezes the two surfaces outside consumers depend on: how a
session's agent handle is derived, and what `a2a ledger` exports. It is
versioned with the repository; v1 is additive-only — a field or enum value
may be added, never repurposed or removed, and a breaking change requires
a v2 and a migration note here. Consumers: the Deck console
(`internal/chats`, `web/src/lib/agent-handle.ts`) and this client
(`a2a.py`). Design context: Deck ADR-0007, ADR-0008, ADR-0009, ADR-0011,
ADR-0013.

## Handle derivation

The **default handle** of a Deck session's agent is

```
<harness>-<sid>
```

where `<harness>` is the harness name from the fixed set

```
claude, codex, kimi, opencode, pi, omp
```

and `<sid>` is the first four characters of the session id, lowercased.
Adding a harness to the set is additive; a harness outside the set has no
handle, and a session id shorter than four characters has no handle — no
handle means no chat surface. The harness name equals the session's
provider name in every entry of the set; the three implementations must
keep one shared table.

The **effective handle** can differ from the default, in this precedence:

1. A name the agent chose (`a2a name`): the newest presence event for
   that session carries it, and it outlives the session — a stopped
   session keeps its ledger under its chosen name.
2. `A2A_HANDLE` as set in the agent process environment (Deck sets it on
   every launch, together with `A2A_NO_COURIER=1` for console reads, and
   names every session to its harness with `NOISEDECK_SESSION_ID`).
3. The default above.

Consumers that fold the ledger by session resolve through the presence
room (`handle_for_session` in `a2a.py`); consumers that only need the
default compute it locally and must produce the identical string.

## The console read surface

One subcommand, read-only, exactly as ADR-0009 scopes it:

```
a2a ledger --probe
a2a ledger --for-session <id> --harness <harness> [--compact]
a2a ledger --index [--compact]
a2a ledger [--handle <handle>] [--compact]
```

`--probe` answers liveness with one presence-room event read.
`--for-session` requires `--harness`. `--compact` prints single-line
JSON; without it the JSON is pretty-printed. A console invocation never
writes a chat event, acknowledges one, or names a source session, and
its reads are bounded: callers impose a short timeout (Deck uses five
seconds) and treat a miss as unavailable, never as empty.

## The ledger export

`a2a ledger [--handle]` prints

```json
{"agent": "<handle>", "chats": [<chat>, ...]}
```

ordered newest activity first. Each `<chat>`:

| Field | Meaning |
| --- | --- |
| `id` | the chat id (`correlation_id` of its events) |
| `state` | `invited`, `waiting`, `open`, `closing`, `closed`, `forced`, `left`, `declined` — projected for the reading agent |
| `waiting_s` | seconds the invite has sat undelivered, when `state` is `waiting`, else `null` |
| `forced` | the chat ended by opener fiat rather than agreement |
| `opened_by`, `opened_at`, `last` | opener handle, open time, newest event time |
| `participation_at` | this agent's departure time, when it left |
| `members`, `left`, `remaining` | all members; departed ones; ones still in |
| `harnesses` | member handle → harness it last ran on, from presence |
| `close_requested_by`, `closed_by`, `close_cause` | the closing round's facts |
| `messages` | count of message rows |
| `rows` | the visible history, below |
| `handshake` | per-member `{member, agreed, at, left, left_at}` for a hosted close, else empty |
| `unreadable` | event ids whose bodies this host cannot read |

Each row:

| Field | Meaning |
| --- | --- |
| `id` | the event id |
| `tag` | `a2a#` plus the last six characters of the id's final `_` segment |
| `kind` | `message`, `added`, `left`, `declined` |
| `from` | author handle |
| `member` | the added member, on `added` rows; else `null` |
| `text` | the body as the logstream holds it, terminal controls made inert; `""` for `left` |
| `at` | event time |
| `to` | member handle → delivery state: `sent`, `delivered`, `uncertain`, `read` |
| `unreadable` | present only when the body is unreadable |

## The index export

`a2a ledger --index` prints, content-free — ids and counts only, never a
body — what a console needs to mark sessions in live chats:

```json
{"chats": [{"id", "state", "members", "left", "last", "last_row", "rows"}],
 "sessions": {"<deck session id>": "<effective handle>"}}
```

`chats` is ordered newest activity first; `rows` counts visible rows;
`last_row` is the newest visible row's event id or `null`. `sessions`
maps every Deck session presence names to its agent's effective handle,
so the marker and the per-session ledger resolve identity the same way.

## What this contract does not cover

The wire itself — event types, rooms, sealing, courier delivery — is the
client's own, versioned by this repository's releases, not by this
document. A consumer that stays on the read surface above does not see
it change.
