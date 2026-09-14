# Threat model

## Malicious leader

A leader may attempt to fabricate `PASS`, `FAIL`, or supporting evidence.

Mitigation:

- validators re-fetch and re-evaluate independently;
- decisive verdict must match independently;
- decisive evidence must be verbatim text present in the validator's source observation.

## Prompt injection in evidence

Public pages are untrusted data and may contain instructions directed at models.

Mitigation:

- the assessment prompt explicitly treats all case fields and source content as data;
- obvious instruction-like caller criteria are rejected before sealing;
- the model is asked only for one bounded classification task;
- no tool action, money movement or additional browsing is available from source instructions.

## Source substitution after sealing

An assessor may try to prove a claim using a more favourable unrelated site.

Mitigation:

- each leaf freezes an HTTPS source prefix before sealing;
- later evidence must stay inside that prefix and on the same host.

AssureGraph does not prove that the configured source was the correct authority; that remains a declared assurance-case assumption.

## Circular argument

A case owner may attempt to create `A -> B -> A`.

Mitigation:

- graph edges may only point to earlier claim IDs;
- cycles are structurally impossible.

## Hidden orphan claim

A definition may contain claims that are not actually connected to the advertised root.

Mitigation:

- sealing requires every claim to be reachable from the root.

## Stale evidence replay

A consumer may rely forever on an old successful assessment.

Mitigation:

- every leaf has a frozen freshness window;
- a passing assessment automatically becomes `STALE` for current support after expiry;
- `is_assured` evaluates current time, not the last stored snapshot.

## Definition substitution

A consumer may accidentally rely on a different graph with the same case ID assumption.

Mitigation:

- sealed cases expose a canonical definition hash;
- consumer contracts pass the exact expected hash into `is_assured`.

## Replay at the consumer

The same assurance may be used repeatedly for an operation intended to occur once.

Mitigation in the included `AssuranceGate` example:

- every action uses a 32-byte action hash;
- consumed action hashes cannot execute twice.

## Storage spam

Leaf reassessment is permissionless, so users can create assessment history.

Mitigation:

- transactions incur network cost;
- only the latest assessment pointer affects current assurance;
- historical records remain append-only for auditability.

A production deployment that needs stronger anti-spam economics can wrap assessment access without changing the primitive's consensus model.
