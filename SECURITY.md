# Security policy

## Reporting a vulnerability

**Do not open a public issue.** Use GitHub private vulnerability reporting on this repository, or
email `security@litmus64.com`.

Include: version (`lx --version`), platform, sandbox tier in use, and a reproducer if you have one.
If the finding involves untrusted-code execution or sandbox escape, say so in the subject — it is
routed first.

## Response SLA

| Stage | Target |
|---|---|
| Acknowledgement | 48 hours |
| Triage and severity assessment | 5 business days |
| Fix or documented mitigation, critical | 14 days |
| Fix or documented mitigation, high | 30 days |
| Public advisory + credit | with the fix, or 90 days, whichever is first |

We publish an advisory even when the fix is small, and we credit reporters by name unless asked not
to.

## Scope

**In scope, highest priority:** sandbox escape from an untrusted diff · prompt injection that changes
a verdict · receipt forgery or signature bypass · secret leakage into a receipt, artifact, log, or
span · plugin escaping its declared capability allowlist.

**In scope:** denial of wallet · cache poisoning · ledger poisoning via crafted history · dependency
vulnerabilities we ship.

**Out of scope:** findings that require an already-compromised CI runner or an already-malicious
maintainer · self-inflicted misconfiguration where the tool warned · missing hardening with no
demonstrated impact (report it as an issue instead, it is welcome).

## Our own posture

SLSA 3 builds, signed artifacts, pinned and vendored dependencies, `cargo-audit`/OSV daily,
reproducible builds, a sandbox-escape suite and an injection corpus in CI, and a committed Litmus64
receipt for every Litmus64 pull request. See [`THREATS.md`](THREATS.md).
