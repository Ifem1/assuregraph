# AssureGraph

**Composable, consensus-backed assurance cases for GenLayer.**

AssureGraph is a standalone reusable Intelligent Contract primitive. It turns a formal assurance argument into immutable on-chain structure, uses GenLayer consensus only where semantic judgement is genuinely required at evidence leaves, and derives the root assurance result deterministically through an `ALL` / `ANY` / `THRESHOLD` claim DAG.

There is **no frontend**. That is deliberate. AssureGraph is intended for the Intelligent Contracts category, not the Projects category.

## The problem

Most semantic contracts answer one question and store one verdict. High-assurance systems need something different:

> A release, service, protocol or autonomous agent is considered ready only when a structured set of claims is currently supported by evidence, with explicit composition rules and freshness.

A safety argument might look like:

```text
Release assurance                          ALL
├── Authentication control                LEAF
└── Recovery assurance                    THRESHOLD 2/2
    ├── Rollback readiness                LEAF
    └── Incident-runbook readiness        LEAF
```

The hard part is not merely judging each leaf. The protocol must also preserve the argument structure, prevent circular reasoning, pin the exact definition consumers rely on, preserve historical assessments, model stale evidence honestly and ensure the final root decision is not itself an LLM opinion.

AssureGraph does that.

## Why GenLayer

A normal smart contract can deterministically evaluate a Boolean DAG, but it cannot safely determine whether a public document materially establishes a natural-language safety claim.

A normal LLM service can make that judgement, but one operator controls the model, prompt, source fetch and output.

AssureGraph separates the two jobs:

```text
public evidence
      │
      ▼
GenLayer leader + independent validators
      │
      ▼
PASS / FAIL / AMBIGUOUS / UNAVAILABLE
      │
      ▼
deterministic evidence freshness
      │
      ▼
immutable ALL / ANY / THRESHOLD graph
      │
      ▼
ASSURED / NOT_ASSURED / INCOMPLETE / STALE
```

GenLayer consensus is used only for the semantic leaf decision. The graph rules, thresholds, freshness, reachability, hashing and consumer gate are deterministic.

## Contract set

### `contracts/assuregraph.py`

The reusable primitive.

It provides:

- immutable assurance-case definitions after sealing;
- leaf claims with frozen evidence criteria and source namespaces;
- `ALL`, `ANY` and `THRESHOLD` composition nodes;
- an acyclic-by-construction claim graph;
- permissionless public evidence reassessment;
- independent validator re-fetch and re-classification;
- source-grounded verbatim evidence for decisive `PASS` and `FAIL` outcomes;
- append-only assessment history;
- freshness windows and automatic `STALE` derivation;
- deterministic root assurance computation;
- definition hashes for downstream pinning;
- evidence-state snapshot hashes for auditability;
- a minimal `is_assured(case_id, expected_definition_hash)` composability surface.

### `contracts/assurance_gate.py`

A deliberately small consumer contract proving that AssureGraph is not merely documentary.

`AssuranceGate.execute(...)` succeeds only if:

1. AssureGraph currently reports the pinned case as `ASSURED`;
2. the caller supplies the exact sealed definition hash; and
3. the action hash has not already been consumed.

A stale, failed, incomplete or definition-mismatched case cannot authorize the protected action.

## State model

### Assurance case

```text
DRAFT ──seal_case()──> SEALED
```

After sealing, the argument topology and leaf policies cannot change.

The definition hash commits to:

- title and purpose;
- root claim;
- every claim;
- claim type;
- statement;
- leaf criterion;
- frozen source prefix;
- freshness window;
- threshold;
- every child edge.

### Claim types

`LEAF`
: A semantic proposition assessed from public HTTPS evidence.

`ALL`
: Every child must currently be `ASSURED`.

`ANY`
: At least one child must currently be `ASSURED`.

`THRESHOLD(k)`
: At least `k` children must currently be `ASSURED`.

The LLM cannot alter these rules.

### Leaf verdicts

`PASS`
: The source materially establishes the frozen criterion. A verbatim source excerpt is mandatory.

`FAIL`
: The source materially contradicts or disproves the frozen criterion. A verbatim source excerpt is mandatory.

`AMBIGUOUS`
: The source is readable but cannot safely establish either decisive outcome.

`UNAVAILABLE`
: The source could not be read.

### Derived statuses

`ASSURED`
: The claim currently satisfies its deterministic composition rule.

`NOT_ASSURED`
: The current decisive evidence/graph state proves the rule is not satisfied.

`INCOMPLETE`
: More or clearer evidence is required.

`STALE`
: Previously passing evidence has exceeded the leaf's frozen freshness window and can no longer support assurance.

Staleness does not rewrite history. The old assessment remains `PASS`; it simply stops being current support for the root claim.

## Acyclic graph invariant

AssureGraph makes cycles impossible by construction: an edge can only point from a newer composite claim to an earlier claim.

```text
claim 1  leaf
claim 2  leaf
claim 3  threshold -> [1, 2]
claim 4  leaf
claim 5  all       -> [3, 4]
```

Because every edge moves toward a lower claim ID, a claim can never eventually depend on itself.

At sealing, the contract additionally requires every claim to be reachable from the selected root. Orphan arguments cannot silently exist outside the committed assurance case.

## Consensus design

For `assess_leaf(claim_id, evidence_url)`:

1. deterministic code checks that the case is sealed;
2. deterministic code checks that the target is a leaf;
3. deterministic code validates HTTPS/public-host shape;
4. deterministic code requires the URL to stay inside the leaf's source namespace frozen before sealing;
5. the leader fetches the source and classifies it against the frozen claim criterion;
6. an independent validator fetches the source itself and performs the same semantic task;
7. the validator requires the same decisive verdict;
8. for `PASS` or `FAIL`, the leader's evidence excerpt must also exist verbatim in the validator's independently fetched source;
9. only the accepted consensus result becomes the new current assessment.

The validator never accepts a leader merely because its JSON has the right shape.

## Deterministic composition rules

### ALL

```text
any NOT_ASSURED -> NOT_ASSURED
else any STALE  -> STALE
else incomplete -> INCOMPLETE
else            -> ASSURED
```

### ANY

```text
any ASSURED          -> ASSURED
all NOT_ASSURED      -> NOT_ASSURED
else any STALE       -> STALE
else                 -> INCOMPLETE
```

### THRESHOLD(k)

```text
assured >= k                         -> ASSURED
assured + stale + incomplete < k     -> NOT_ASSURED
else stale exists                    -> STALE
else                                 -> INCOMPLETE
```

That last rule is important. AssureGraph does not label a threshold `NOT_ASSURED` merely because it has not yet collected enough evidence. It only does so when the currently unresolved children could no longer bring the threshold to `k`.

## Source policy

Every leaf freezes an HTTPS source prefix before sealing, for example:

```text
https://security.example.org/releases/
```

Later evidence must remain under that namespace and on the same exact host.

This prevents an assessor from defining a claim against one source policy and then opportunistically proving it with an unrelated website after the case is sealed.

AssureGraph does **not** claim that the configured source is authoritative in the real world. Source authority is a declared input/trust assumption of the assurance case. The contract proves what the configured public source currently establishes under the frozen criterion.

## Freshness

A passing leaf stores an expiry time:

```text
expires_at = observed_at + freshness_seconds
```

After expiry:

```text
PASS history remains PASS
current leaf support becomes STALE
root assurance is recomputed deterministically
```

A fresh reassessment can restore assurance without deleting or changing the previous assessment.

## Example lifecycle

```text
1. create_case()
2. add_leaf(authentication)
3. add_leaf(rollback)
4. add_leaf(runbook)
5. add_threshold(recovery, 2)
6. add_child(recovery, rollback)
7. add_child(recovery, runbook)
8. add_all(root)
9. add_child(root, authentication)
10. add_child(root, recovery)
11. set_root(root)
12. seal_case()
13. assess_leaf(authentication, ...)
14. assess_leaf(rollback, ...)
15. assess_leaf(runbook, ...)
16. get_case_status() -> ASSURED
17. AssuranceGate.execute(...) -> succeeds
18. evidence ages beyond frozen window
19. get_case_status() -> STALE
20. another gated execution -> refused
21. fresh reassessment -> ASSURED again
```

## Why this is reusable

AssureGraph does not know what a "release" is. The same primitive can represent:

- protocol-upgrade readiness;
- autonomous-agent safety cases;
- infrastructure release gates;
- compliance-control assurance;
- operational-readiness arguments;
- safety certifications;
- model-deployment readiness;
- treasury-action prerequisites;
- high-risk workflow prerequisites.

Consumers only need the stable view:

```python
is_assured(case_id, expected_definition_hash)
```

They do not need to replicate the consensus prompts, graph rules or freshness logic.

## Network target

This repository is intentionally configured for **stable GenLayer Studionet**:

```text
RPC:      https://studio.genlayer.com/api
Chain ID: 61999
Network:  studionet
```

The repository does not use a development-preview network alias.

## Tests

### Direct Mode

```bash
python -m pip install -r requirements-test.txt
pytest tests/direct -q
```

The suite covers definition immutability, graph reachability, acyclicity, frozen source namespaces, validator independence, grounded evidence, threshold composition, failure propagation, staleness, reassessment and snapshot hashes.

### Live Studionet

The integration lifecycle is intentionally written for stable Studionet:

```bash
gltest tests/integration -v -s --network studionet
```

Before that run, pin `tests/integration/test_studionet_lifecycle.py` to the immutable commit containing the public evidence fixtures. See `DEPLOYMENT.md`.

## Repository structure

```text
contracts/
  assuregraph.py
  assurance_gate.py
fixtures/
  auth_pass.txt
  rollback_pass.txt
  runbook_pass.txt
  auth_fail.txt
tests/
  direct/
  integration/
docs/
  ARCHITECTURE.md
  CONSENSUS.md
  THREAT_MODEL.md
  DEMO.md
scripts/
  preflight.py
  pin_fixture_commit.py
README.md
SUBMISSION.md
DEPLOYMENT.md
```

## Non-goals

AssureGraph does not claim to:

- prove metaphysical truth;
- decide whether a source is legally authoritative;
- discover hidden/private evidence;
- replace formal verification;
- turn a subjective root statement directly into an LLM verdict;
- make legal, regulatory or safety guarantees outside the encoded argument;
- provide a frontend or full product flow.

It is an assurance-argument primitive: consensus-backed leaf evidence plus deterministic, inspectable composition.
