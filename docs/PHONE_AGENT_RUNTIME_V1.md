# Phone Agent Runtime V1

The Android app is the host. GitHub is infrastructure and evidence, not command authority.

## Runtime pipeline

HUMAN COMMAND
-> AUTHORITY GATE
-> INTENT/TOOL ROUTING
-> READ-ONLY EVIDENCE COLLECTION
-> MODEL REASONING (when configured)
-> SCIENTIFIC GUARD
-> VERIFICATION
-> EVIDENCE LEDGER
-> RESPONSE

## Capabilities implemented in source

- explicit human command gateway
- encrypted GitHub credential storage on Android
- GitHub repository/file/tree/commit/workflow read services
- provider-neutral knowledge/search interface
- provider-neutral LLM backend interface
- project-agnostic memory and provenance records
- independent Simulation Matrix request boundary
- scientific guard preventing model output from becoming scientific authority
- explicit confirmation for repository writes

## Important status

Source implementation is not execution evidence. No capability is marked operational until Android build/tests or a controlled runtime test verifies it.

## Required before release

1. Build the APK with GitHub Actions.
2. Run unit/integration tests.
3. Verify Chaquopy Python packaging.
4. Verify Android Keystore storage.
5. Configure a real model backend.
6. Configure a real knowledge/search provider.
7. Harden Python execution into a real sandbox or disable untrusted execution.
8. Connect the Simulation Matrix through a tested transport.
9. Add encrypted local persistent memory.
10. Run adversarial authority/security tests.
11. Sign the release APK.
