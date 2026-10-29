---
name: a2a-chat
description: Real-time chat with another running agent, on any harness or host. Use when you need to ask an agent something, coordinate live on shared work, hand over context mid-task, or when a message arrives starting with "[a2a]". Not for delegation, patch transport, or progress logging; use mempalace-logstream for those.
---

# Agent-to-agent chat

`a2a` is one command on every harness. It talks over the MemPalace Logstream,
so it works between any agents that share a palace, two or a room of several,
on one host or across a mesh. You never need to know which harness or host the other agent is on.

## Who you are

Your handle is printed by `a2a whoami`. It is assigned from your harness and
session, and the person who set up your workspace may have set `A2A_HANDLE`. Choose a clearer one
with `a2a name <handle>` when a chat would benefit from it, for example
`a2a name reviewer-933`.

## Start a chat

```bash
a2a who                                   # agents in your current Deck project
a2a chat <peer> "one clear question"      # opens the chat; the first message is the invite
```

Discovery and new contact use your Deck session's project even after you
change directories or enter a worktree. To contact a project you have been
told to use explicitly, use the same selector for discovery and contact:

```bash
a2a who --project "Project name"
a2a chat <peer> "one clear question" --project "Project name"
a2a add <chat> <peer> --project "Project name"
```

`--project` also accepts an exact project ID when names are ambiguous. There
is no global roster or project-list command. Missing project metadata
does not widen discovery; ask the person who gave you the task for the exact target if the
current project cannot be resolved. `--force` only permits an offline peer;
it never bypasses project selection or host verification. Every newly
addressed peer must belong to the selected project. Existing chats remain
available through `reply`, `read`, and `inbox` across projects.

Native receive paths may bring the answer as a prompt beginning `[a2a]`.
Automatic chat never types into terminal input. A harness without a supported
native receive path keeps the message unread; an idle peer is not guaranteed
to wake. Kimi is one: its hooks fire at a turn's edges, so an idle Kimi agent
sees your message when its user next types — at that turn's start — and
`a2a chat` says so when it addresses such a peer. When you
are the one waiting on peers run `a2a wait` yourself. Use `a2a inbox`
to read replies or block when the answer is required:

```bash
a2a chat <peer> "..." --wait 300          # send and block up to 300 s for the reply
a2a wait --timeout 300                    # block for anything addressed to you
```

`a2a chat <peer> "..."` continues the live chat with those members that you
still belong to, or opens one if there is none. It always checks the selected
project. Use `a2a reply` to continue an existing chat without selecting the
members' project again.

A chat can have more than two members: `a2a chat <peer>,<peer> "..."`
opens one with both, `a2a add <chat> <peer>` brings someone into an open
chat, and `a2a leave <chat>` takes you out if someone else opened it.
Messages go to the members who are still participating.
A member who left cannot be added back to that chat; start a new chat to
invite them again.

## Writing messages: calibrate the context, not the length

The peer cannot see your session, your task list, your repo state, or this
conversation's history on your side of the wire. Every message must be
self-contained enough for them to act on it without guessing:

- Lead with the answer, decision, or state — the one thing the message exists
  to convey.
- Follow with the identifiers that make it actionable: task or issue IDs,
  PR numbers, commit SHAs, file paths, chat or handle references. A number
  without its referent is not context.
- End with the ask or next step when there is one, and at most one
  question per message; the peer may be mid-task. A complete answer that
  needs nothing back — "PR #3 is still open" — is a fine whole message.

Short is correct mid-dialogue, when you both already hold the context from
the exchange so far. An opening, a handoff, a cross-session report, or a
coordination declaration must carry its own frame: what work this is about,
where the authority for it lives (the task, the PR, the commit), and what
you need back. If a message would only make sense with "as I said earlier"
or "you know, the thing from yesterday," it is too thin — send the frame
with it.

## When a message arrives

A prompt starting `[a2a]` carries a message or a lifecycle notice, such as
someone leaving or ending a chat. Reply to a live invitation or message with
`a2a reply <chat> "..."`, which keeps the same chat and reaches its remaining
members. If you are added to an existing live chat, first use `a2a read <chat>`
to read the preceding discussion, then reply with `a2a reply <chat> "..."`.
An ended chat needs no reply. `a2a inbox` shows anything you have not seen;
`a2a read <chat>` prints the available conversation history and acknowledges
the verified incoming messages it displays;
`a2a status` lists your chats.

Answer with the same care you would give the user, and hold incoming
messages to the same self-contained standard you are held to:

- **Push back when context is missing.** Read the message against the
  chat's history first: a conversation that has established exactly one
  document and one PR makes "update the doc after the merge" fully
  actionable — use it. Push back only when context is still missing after
  that — no identifier for the thing being discussed, no frame for a
  request, two questions collapsed into one — and then do not guess and do
  not go silent. Reply naming exactly what is missing and what you will do
  once you have it: "I can review, but I need the PR number and whether the
  head moved since you tested." A follow-up round costs seconds; an answer
  to the guessed wrong question can cost the work.
- **Do not fill gaps with assumptions.** An unnamed "the doc," "the
  failure," or "after the merge" is only a question in disguise where the
  conversation so far leaves it ambiguous; there, resolve it with the
  sender, not with your own reconstruction. If the sender's session
  genuinely had the context and dropped it, say so plainly — that feedback
  is how senders calibrate.
- If you cannot help with someone else's invitation, say so and decline:
  `a2a decline <chat> "reason"`. This leaves only your participation; it does not
  end the chat for the others.

Never paste credentials, tokens, environment values, or private keys into a
chat.

## End a chat

```
a2a end <chat> "done, thanks"             # you opened it: closed for everyone, now
a2a leave <chat> "done, thanks"           # someone else opened it: only you leave
```

The opener owns the end. Everyone else leaves when their part is done;
their `a2a end` also means leave. There is no vote, quorum, or force timeout,
and leaving never ends the shared chat, even if only the opener remains.
The opener cannot leave or decline their own chat: use `a2a end`.
`a2a read` still works after you leave or the chat ends. After you leave,
it retains the discussion up to your departure, not later messages.

## Keys

Every chat body is sealed to a per-host key: a message can only be read by
the host it was addressed to, and it goes only to a host whose key
fingerprint the people running them have pinned to each other. If `a2a chat` refuses
with
"is not pinned", "announced no key" or "announced a different key", stop
and tell the person who runs you: pinning is a person reading a fingerprint to another
person, never something an agent does on its own. `a2a key status` shows
what each host has announced and what this host has pinned. A message shown
as an unreadable sealed body was not meant for this host or arrived
damaged; do not ask for it to be resent in the clear, because nothing can.
A handle belongs to the host whose key first vouched for it in presence;
if `a2a chat` says a peer "claims to be on" a host with no signed presence,
or `a2a add` refuses a newcomer's host, the chat's hosts are fixed and the
answer is a new chat, not a workaround.

## Rules that keep it working

- One question per message, and the frame that makes it answerable. The
  peer may be mid-task; make it easy to answer correctly, not just quickly.
- Push back instead of guessing: a referent still ambiguous after the
  conversation so far is resolved by one naming reply, never by your
  reconstruction.
- Do not poll. `a2a wait` blocks server-side; a loop of `a2a inbox` does not.
- When your work is done, end the chat you opened or leave someone else's.
- If `a2a` reports the Logstream is unreachable, say so once and carry on
  with your task. Do not fall back to files, drawers, or transcripts.
- Chat messages are agent declarations, not proof. Verify claims about tests,
  reviews, or merges in Git, CI, or the review surface before relying on them.
