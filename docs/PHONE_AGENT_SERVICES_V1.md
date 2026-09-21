# Phone Agent Services V1

## Services being prepared

### 1. Command service
Only explicit human commands enter the authoritative command path.

### 2. Brain service
Provider-neutral reasoning backend. The application does not hard-code a model provider.

### 3. Memory service
Local structured JSONL records with project scope, source, confidence, timestamp, and SHA-256 content hash.

### 4. Knowledge service
Provider-neutral web/external knowledge interface. Search results are evidence and must retain source provenance.

### 5. GitHub service
Repository read/write adapter using a runtime credential. Default architecture is least privilege; write operations must be explicitly authorized.

### 6. Python service
Controlled Python execution interface. Current implementation is NOT a complete sandbox.

### 7. Simulation service
Adapter for the independent Simulation Matrix. The Matrix remains an executor, not the scientific decision-maker.

### 8. Forensic verification service
Planned service for leakage, circularity, provenance, reproducibility, identifiability, null/control validity, and adversarial checks.

## Required before real deployment

- Android build verification
- secure secret storage
- scoped GitHub credentials
- actual model backend
- real knowledge/search provider
- sandboxed Python execution
- Simulation Matrix transport
- adversarial regression tests
- crash recovery
- encrypted local state
- signed release build

No service is described as operational until it has been executed and verified.
