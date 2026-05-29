# AGENTS.md

This repo is centered on personal workstation bootstrap and maintenance scripts, especially `./ubuntu-setup.sh`, plus a grab bag of standalone CLI utilities.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry.
- Re-read the current script before every edit, trust file state not memory, and validate immediately after each change.
- Preserve existing CLI shape unless the user asks to redesign it: flags, environment variables, prompts, exit behavior, and default side effects are part of the interface.
- Prefer focused validation such as `bash -n`, `shellcheck` if available, or a narrow `--help`/dry-run style check over broad execution of install scripts.
- Do not run destructive scripts or commands without explicit user intent. Treat scripts such as `clean-home.sh` as high-risk and preserve their confirmation barriers.
- For shell scripts, keep the current style and existing helper abstractions instead of inlining one-off logic.
- For German prose or user-facing text, use standard German orthography with umlauts and `ß` unless the user explicitly asks for ASCII.

## Setup Scripts

- `./ubuntu-setup.sh` is the main integration surface in this repo. Prefer editing existing helper functions and feature-specific installers over adding ad hoc logic in `main`.
- Keep setup actions idempotent where the script already aims for that: command-existence checks, guarded config edits, backup-before-reconfigure behavior, and safe re-runs should not regress.
- Preserve the current split between general setup and Lena-specific opt-ins such as `--lenas-setup` and related `UBUNTU_SETUP_*` flags unless the user explicitly asks to redesign that boundary.
- When touching download-and-run flows, keep checksum verification before execution. Do not weaken integrity checks or silently replace them with trust-on-first-use behavior.
- When touching Podman-managed services, follow the existing safety pattern: require Podman 5, refuse to replace unrelated same-name containers, keep persistent state under the calling user's home directory, and prefer loopback-only port bindings unless the user explicitly asks to expose services.
- When changing GNOME, Git, VS Code, or shell reconfiguration steps, preserve explicit backup or append-only behavior unless the user asked for a reset.
- If a change affects CLI flags or execution flow in `ubuntu-setup.sh`, validate at minimum with `bash -n ./ubuntu-setup.sh` and `./ubuntu-setup.sh --help`.

## Standalone Utilities

- Keep standalone scripts single-purpose and lightweight. Avoid introducing large framework dependencies when standard shell or small scripting-library solutions are enough.
- Preserve safety prompts and obviousness for scripts with destructive or privacy-related behavior.
- For converters, scrapers, and text-processing utilities, prefer deterministic input/output behavior over cleverness.
- If a utility already has a narrow platform assumption baked in, do not silently broaden or change that assumption without the user's request.
