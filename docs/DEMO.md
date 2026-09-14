# Demo script

The strongest demo is a contract-only Studio lifecycle. No frontend is required.

## Scene 1 — immutable safety argument

Deploy `AssureGraph` on stable Studionet and create:

```text
Release assurance                    ALL
├── Authentication control           LEAF
└── Recovery assurance               THRESHOLD 2/2
    ├── Rollback readiness           LEAF
    └── Incident readiness           LEAF
```

Seal it and show the 64-character definition hash.

Explain that from this point the argument topology, criteria, freshness windows and source policies are immutable.

## Scene 2 — consensus at leaves

Assess the three public fixture URLs.

For each assessment show:

- `PASS`;
- the verbatim evidence excerpt;
- the assessment ID;
- the leaf's current-assessment pointer.

Then show:

```text
get_case_status(1) -> ASSURED
```

The important point is that no LLM directly decided the root status.

## Scene 3 — real composability

Deploy `AssuranceGate` with the AssureGraph contract address.

Call:

```text
execute(case_id, definition_hash, action_hash)
```

and show success.

Then call with the wrong definition hash and show deterministic refusal.

## Scene 4 — freshness

For local/direct-mode demonstration, advance time beyond the leaf freshness window.

Show:

```text
historical assessment -> still PASS
current root status    -> STALE
is_assured(...)        -> false
```

Then perform fresh assessments and show the root returns to `ASSURED`.

## Reviewer takeaway

The primitive should be explained in one line:

> GenLayer judges bounded evidence leaves; AssureGraph deterministically composes those leaves into an immutable, freshness-aware assurance argument that other Intelligent Contracts can enforce.
