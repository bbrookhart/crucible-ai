# CRUCIBLE BLACKBOX design

BLACKBOX protects locally sequestered tasks from accidental publication and post-hoc modification.
`seal` canonicalizes private files and encrypts the payload with Fernet using an evaluator-controlled
key. `commit` decrypts locally, hashes the canonical task payload, environment, and scorer, and records
a combined commitment. `run` reveals into a random temporary directory and destroys it after use.
`reveal` supports authorized inspection; `verify` recomputes every commitment field.

Vaults, keys, commitments, and reveals live under ignored `.crucible/` state by default. No vault or key
is included in public CI, Docker layers, or repository history. The key should be injected from a local
secret manager, not a shell-history-prone command in a high-assurance deployment.

This is **sequestered evaluation**, not double blind. The implementation protects data at rest and
detects commitment drift. It does not provide HSM custody, remote attestation, external notarization,
multi-party key release, compromised-host resistance, or proof that a model never saw equivalent data.
