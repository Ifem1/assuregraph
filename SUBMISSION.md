# AssureGraph — Intelligent Contract submission

## Category

Standalone reusable GenLayer Intelligent Contract.

**No frontend.** The repository intentionally contains only the primitive, a minimal consumer, tests, fixtures and reviewer documentation.

## One-sentence description

AssureGraph is a formal assurance-case primitive where GenLayer validators independently verify public evidence at leaf claims while the root `ASSURED / NOT_ASSURED / INCOMPLETE / STALE` state is derived deterministically through an immutable `ALL / ANY / THRESHOLD` argument DAG.

## Why this is not a thin LLM wrapper

The LLM cannot decide whether the whole system is safe.

Consensus is restricted to a bounded evidence question at each leaf. The contract itself owns:

- DAG construction;
- cycle prevention;
- root reachability;
- immutable definition hashing;
- exact source namespace pinning;
- assessment history;
- freshness expiry;
- `ALL`, `ANY` and threshold logic;
- current assurance derivation;
- snapshot hashing;
- downstream hash-pinned consumption.

## Consensus logic

For each leaf assessment, the leader fetches the public source and proposes `PASS`, `FAIL`, `AMBIGUOUS` or `UNAVAILABLE`.

A validator independently fetches and re-evaluates the source. It requires the decisive verdict to match. For `PASS` and `FAIL`, it also requires the leader's verbatim evidence excerpt to exist in the validator's independently fetched page.

Leader-output-only schema validation is not used as consensus.

## Reusability

Any consumer contract can pin one sealed assurance policy through:

```python
is_assured(case_id, expected_definition_hash)
```

The included `AssuranceGate` proves the intended integration boundary and prevents replay of one-time action hashes.

## Meaningful use cases

- protocol-upgrade readiness;
- autonomous-agent deployment safety;
- operational readiness;
- infrastructure release gates;
- compliance-control assurance;
- model release checks;
- high-risk treasury or governance prerequisites.

## Important trust boundaries

AssureGraph proves what a configured public source materially establishes under a frozen criterion. It does not claim that a source is legally authoritative, that hidden evidence does not exist, or that a root claim represents universal truth.

## Target network

Stable Studionet only:

```text
RPC: https://studio.genlayer.com/api
Chain ID: 61999
Alias: studionet
```

## Final live evidence required before submission

The zip intentionally contains no invented deployment addresses or transaction hashes.

Before submission, the repository owner should:

1. push the initial repository;
2. pin the public fixture commit in the live integration test;
3. run Direct Mode tests;
4. run the live lifecycle with `--network studionet`;
5. deploy canonical `AssureGraph` and `AssuranceGate` instances;
6. record finalized contract addresses and transaction hashes in `DEPLOYMENT.md`;
7. run `python scripts/preflight.py --final`;
8. push the final evidence commit.
