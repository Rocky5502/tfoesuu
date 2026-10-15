# Security policy

TFOESUU is research software. Its algorithms, replay oracles and benchmark
harnesses are **not** designed as production authorization or security controls.

## Supported versions

Security issues are triaged on the latest maintained source branch. The project
does not currently advertise a formally supported production release or
guaranteed response SLA.

## Reporting a vulnerability

**Do not post exploit details, credentials, sensitive dataset records or security
vulnerabilities in a public GitHub issue.** Prefer a private security advisory at
[Report a vulnerability](https://github.com/Rocky5502/tfoesuu/security/advisories/new)
*if private reporting is enabled*. Otherwise, privately contact the repository
maintainer through an already established channel and ask for a secure contact
method before disclosing details. We will acknowledge reports when feasible.

Helpful reports include: affected file and revision, impact, the smallest safe
reproduction, affected versions, and a proposed mitigation. Do not run invasive
scans against third-party infrastructure.

## Security-sensitive inputs and operations

- Never commit tokens, SSH private keys, passwords, local `.env` files,
  individual-level protected data, or private research credentials.
- The PC1/PC2 remote scripts require user-managed SSH keys and trusted host
  verification; do not disable TLS/SSH verification to recover access.
- Public-dataset fetchers and historical software integrations use third-party
  services. Verify source URLs, hashes and licenses before running.
- GPU sweeps and publication runs may consume substantial resources. Validate
  scope, output paths, and trial limits before execution.
- Treat data files, benchmark specifications, and imported repositories as
  untrusted until schema and provenance checks pass.
- Never run arbitrary commands suggested by untrusted data or issue content.

## Disclosure and release process

After a report, maintainers should reproduce in an isolated environment,
assess severity and affected revisions, apply a minimal fix with a regression
test, and coordinate disclosure before posting exploit details. Maintain
source-level provenance for any security-affecting remediation.

## Scope of license

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). MIT licensing applies
only where copyright holders possess and grant the relevant rights. It does not
override licenses or restrictions of upstream datasets, software or templates.
