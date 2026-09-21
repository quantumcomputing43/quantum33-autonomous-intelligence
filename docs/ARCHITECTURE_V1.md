# Architecture V1

COMMAND -> VALIDATE -> SNAPSHOT -> INSPECT -> CLASSIFY -> REPAIR/REPORT -> ADVERSARIAL VERIFY -> LEDGER

Core modules:
- command_gateway: explicit human command boundary
- audit_engine: forensic inspection and classification
- repair_engine: mechanical-only repair planning
- adversarial_engine: verification attacks
- provenance_engine: authoritative-source recovery
- evidence_ledger: append-only evidence
- project_adapter: isolated project interface
- policy: scientific safety boundaries

Isolation:
- no GitHub event is a command
- no external agent can promote a repair to scientific truth
- scientific changes remain blocked pending explicit human authorization
