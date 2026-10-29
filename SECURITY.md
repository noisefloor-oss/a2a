# Security policy

## Reporting a vulnerability

Please report vulnerabilities privately by email to the maintainer:
**doug@noisefloor.app**. Do not open a public issue for a security problem.
(GitHub Security Advisories under this repository's Security tab is an
accepted route as well wherever it is available; this repository is
currently private, where GitHub does not offer it, so email is the
reliable channel.)

Reports are read by the maintainer. This is an experimental, solo-maintained
project: there is no response-time SLA and no bug bounty, but genuine
vulnerabilities are taken seriously and fixes are prioritized over feature
work.

## Scope

`a2a` carries agent identity in PyNaCl host keys, seals every chat body to
the participating hosts, and uses the MemPalace logstream over the palace
mesh as its transport. Reports about breaking sealed-chat confidentiality
or integrity, forging or colliding a host identity or handle, crossing a
chat's membership boundary (reading or posting as a non-participant), or
corrupting the `a2a ledger` export are exactly what this policy is for.

The tool assumes the local host and the shared palace hub are trusted
infrastructure. Reports that require an already-compromised host or palace
hub are still welcome but may be classified as hardening suggestions
rather than vulnerabilities.

## Supported versions

Only the latest tagged release is supported. There are no security backports
to earlier releases.
