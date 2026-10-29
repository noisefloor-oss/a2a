---
name: a2a-update
description: Install or update the standalone a2a client from a tagged GitHub release. Use when asked to install, upgrade, verify, or pin a2a, including safely replacing an existing binary without changing Deck's bundled version pin.
---

# Install or update a2a

Propose an update plan before changing any files. Identify the current version, target tag, installation path, permissions, checksum, and rollback path. Do not download or replace anything until the plan is clear.

## Protect Deck's pin

A standalone update never changes Deck's bundled a2a version. Deck pins its own reviewed artifact and moves that pin only through a Deck release. Do not edit Deck configuration, Dockerfile arguments, or release pins to make a standalone update appear consistent. Install the standalone binary in a separate user-owned location when Deck is present.

## Install

1. Choose an exact release tag and read its notes. Do not follow a moving branch or `latest` URL.
2. Download `a2a` and `SHA256SUMS` from that tag.
3. Verify the bytes before execution:

   ```sh
   sha256sum --check SHA256SUMS
   ```

4. Install with mode `0755`, preserving a backup of any replaced binary. Prefer a user-owned path such as `$HOME/.local/bin/a2a` and ensure its directory is on `PATH`.
5. Verify `a2a --version` reports the selected version and `a2a --help` runs outside the download directory.
6. Confirm the intended MemPalace palace is reachable before starting chats. PyNaCl is required for host keys and sealed chats; do not bypass its absence.

## Rollback

If checksum verification, version reporting, help, or the palace check fails, restore the backup binary and stop. Do not leave a partially installed or unverified a2a on `PATH`.
