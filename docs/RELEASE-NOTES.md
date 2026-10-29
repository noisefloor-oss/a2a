# a2a 0.1.0

Initial public release.

- Run live agent-to-agent chats on supported harnesses without installing Deck.
- Share conversations across hosts through the MemPalace palace mesh.
- Protect host identity and sealed chats with PyNaCl host keys.
- Read chat state through the additive-only v1 ledger consumer contract.
- Revalidate cached Codex ownership against process identity to prevent PID-reuse confusion.

## Update

Read the [a2a update skill](https://github.com/noisefloor-oss/a2a/blob/v0.1.0/skills/a2a-update/SKILL.md) and ask your agent to propose an update plan first. Keep Deck's bundled a2a version pin unchanged outside a Deck release.

Download `a2a` and `SHA256SUMS` from the v0.1.0 release, then run:

```sh
sha256sum --check SHA256SUMS
install -m 0755 a2a /usr/local/bin/a2a
a2a --version
```
