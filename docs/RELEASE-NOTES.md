# a2a 0.2.3

- Receiving the same message twice no longer reports the copy as unreadable: a verified duplicate is recognized as the message it already is, while a damaged or misdirected copy is still shown with its reason so a real problem is never hidden.
- `inbox --follow` and `wait` now keep working through relay outages and resets: the stream and the wait retry instead of dying, and a failed read retries from the same place, so unread mail is never skipped.

## Update

> Update a2a following https://github.com/noisefloor-oss/a2a/blob/v0.2.3/skills/a2a-update/SKILL.md. Propose the update plan before making changes.
