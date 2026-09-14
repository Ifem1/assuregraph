# Architecture

## Design principle

AssureGraph deliberately minimizes the surface on which nondeterminism can affect state.

Semantic judgement is restricted to **leaf evidence assessment**. Once a leaf verdict has reached consensus, all higher-order reasoning is deterministic graph evaluation.

This avoids the weaker architecture:

```text
LLM reads everything -> LLM decides whether system is safe
```

and replaces it with:

```text
independent semantic leaf verdicts
            +
immutable argument topology
            +
deterministic composition
            =
current assurance status
```

## Storage

### `AssuranceCase`

Owns definition metadata, root claim, immutable definition hash and the latest optional snapshot.

### `Claim`

Represents either:

- a semantic evidence leaf; or
- an `ALL`, `ANY`, or `THRESHOLD` composition node.

Nested dynamic arrays are intentionally avoided in stored dataclasses. Claim membership and graph edges use indexed `TreeMap` relations instead.

### `Assessment`

Append-only record of a consensus decision over one leaf and one public evidence URL.

The leaf stores only a pointer to its current assessment. Reassessment changes that pointer but never deletes the earlier receipt.

## Graph construction

Claims receive monotonically increasing IDs.

`add_child(parent, child)` requires:

```text
child_id < parent_id
```

Every directed edge therefore moves toward a smaller ID. Cycles are impossible.

This is simpler and safer than accepting arbitrary edges and attempting cycle detection after the fact.

At sealing, the contract verifies:

- the root exists;
- the root is composite;
- every composite has children;
- every threshold is satisfiable by its own child count;
- every claim is reachable from the selected root.

## Definition hash

The canonical JSON definition includes every semantically relevant field and child list. It is serialized with sorted keys and compact separators before Keccak hashing.

A consumer pins this hash when it decides to trust a particular assurance policy.

If a different case definition is created later, it necessarily has a different hash.

## Current versus historical truth

An assessment can remain historically `PASS` while no longer supporting assurance because its freshness window has elapsed.

AssureGraph separates:

```text
historical verdict: PASS
current support:     STALE
```

That distinction prevents history rewriting while still making assurance time-sensitive.

## Snapshots

`refresh_case(case_id)` persists:

- current derived root status;
- refresh time;
- snapshot hash over the definition and current leaf evidence pointers/statuses.

Consumers do not need snapshots for safety — `is_assured` computes current status — but snapshots make demos, audits and external indexing easier.

## Consumer boundary

`AssuranceGate` demonstrates the smallest useful consumer.

It does not inspect the argument graph itself. It asks the primitive:

```python
is_assured(case_id, expected_definition_hash)
```

and consumes a one-time action hash only when the answer is true.
