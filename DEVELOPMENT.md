# Development model

- Source is available under the [MIT license](LICENSE).
- This repository is the standalone home of `a2a`. It was imported verbatim
  from the Deck repository at commit
  `0641b2a4ae342cd57aa883404708f25d3cac080a`; the chat design history lives
  in Deck's decision records (0007, 0008, 0011, 0013).
- **Issues are open** and are the supported inbound channel for bug reports
  and feedback. Filing an issue creates no commitment to a fix, a timeline,
  or a response SLA — but reports are read and genuinely useful.
- For security reports, see [SECURITY.md](SECURITY.md) — please do not open
  a public issue for a vulnerability.

## AI assistance

This software is developed with heavy, deliberate use of autonomous coding
agents, operating under machine-enforced test and benchmark gates. A human
(Doug Doan) directs the work, owns every release decision, and is
responsible for what ships.

## Status

This project is **experimental**: interfaces, file formats, and behavior
may change between releases without a deprecation cycle. The only
compatibility commitment is the explicitly versioned consumer contract in
[docs/CONTRACT.md](docs/CONTRACT.md), which is additive-only within a
version.
