# Consensus design

## What consensus decides

Consensus is used for exactly one question:

> Does the fetched public source materially establish, materially contradict, or fail to resolve this frozen leaf criterion?

The decision vocabulary is deliberately bounded:

- `PASS`
- `FAIL`
- `AMBIGUOUS`
- `UNAVAILABLE`

## Leader path

The leader:

1. fetches the configured HTTPS evidence URL;
2. sends the source plus frozen case/claim data to an LLM;
3. obtains a bounded verdict, reason and evidence excerpt;
4. enforces local grounding rules before returning the candidate.

A `PASS` or `FAIL` without a verbatim excerpt contained in the fetched source is downgraded to `AMBIGUOUS` before consensus.

## Validator path

The validator does not validate JSON shape alone.

It independently:

1. fetches the same URL;
2. performs the same bounded semantic evaluation;
3. requires the independent decisive verdict to match the leader's verdict;
4. for `PASS` or `FAIL`, requires the leader's evidence excerpt to exist in the validator's independently fetched source.

If the source changed between observations in a way that prevents convergence, consensus can fail rather than writing a false stable answer.

The validator also requires the leader's decisive excerpt to exactly match the
validator's own grounded excerpt. A leader cannot quote an irrelevant sentence
that merely happens to be present on a page whose independent assessment passes.

## What consensus does not decide

Consensus does not decide:

- graph topology;
- thresholds;
- parent/child relationships;
- whether an edge creates a cycle;
- freshness expiry;
- definition hashes;
- snapshot hashes;
- whether a consumer action hash was already used;
- the final root status once leaf verdicts are known.

Those are deterministic protocol rules.

## Why not ask one LLM whether the root is safe?

Because that collapses policy, evidence and composition into one opaque subjective output.

AssureGraph instead makes the safety argument inspectable:

```text
root NOT_ASSURED
because auth FAIL
while recovery ASSURED
```

or:

```text
root STALE
because authentication evidence expired
```

The protocol can explain the path without asking another model.
