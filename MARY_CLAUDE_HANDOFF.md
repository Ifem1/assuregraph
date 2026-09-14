# Mary → Claude handoff

Mary will unzip this repository herself, open/add the unzipped `assuregraph` folder in Claude, and paste the instruction below.

---

You are taking over a substantially implemented GenLayer Intelligent Contract repository named **AssureGraph**.

Do not return only a plan, checklist, commentary or mockup. Inspect the entire unzipped repository first, then finish it to a review-ready state in the existing folder and push the completed work to:

`https://github.com/Ifem1/assuregraph`

The remote repository is currently intended to receive this codebase. Preserve the product architecture unless an actual GenLayer runtime/test failure proves a change is necessary.

## PRODUCT BOUNDARY

AssureGraph is a **standalone reusable Intelligent Contract primitive**, not a full application.

There must be **no frontend**.

The primitive models a formal assurance/safety case as an immutable DAG:

- semantic evidence lives only at leaf claims;
- leaf verdicts are `PASS`, `FAIL`, `AMBIGUOUS`, or `UNAVAILABLE`;
- decisive `PASS`/`FAIL` evidence must remain grounded in the independently fetched source;
- `ALL`, `ANY`, and `THRESHOLD` composition is deterministic;
- passing leaf evidence expires under a frozen freshness window;
- expired evidence becomes `STALE` for current support without rewriting historical assessments;
- consumers pin the sealed `definition_hash`;
- `AssuranceGate` proves another Intelligent Contract can enforce current AssureGraph assurance and reject replay.

Do not collapse the design into a generic “AI decides whether the system is safe” contract. The root status must remain deterministic from consensus-backed leaves.

## NON-NEGOTIABLE NETWORK

Use **stable Studionet only**:

- network alias: `studionet`
- chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`

Do not change the network target.

Before every live deploy/write workflow, verify the effective network information and confirm chain ID 61999.

## REQUIRED WORK

1. Read `README.md`, `SUBMISSION.md`, `DEPLOYMENT.md`, every file under `docs/`, both contracts, all tests and scripts before editing.
2. Run `python scripts/preflight.py` immediately.
3. Install the repository's pinned test tooling and run all Direct Mode tests.
4. Fix actual failures completely. Do not weaken tests merely to make them green.
5. Review the AssureGraph contract for current stable GenLayer SDK/runtime compatibility, storage safety, validator independence, URL/source-prefix safety, graph invariants, threshold semantics, timestamp/freshness handling, event behavior and consumer compatibility.
6. Keep the current stable py-genlayer dependency unless stable Studionet itself proves it must change. Never migrate the project to another Studio environment just to make tooling easier.
7. Ensure the leader/validator design remains substantive: validators must independently re-fetch/re-evaluate the source and decisive evidence must be grounded in the validator's own observation.
8. Preserve the rule that the LLM only judges leaf evidence. It must never decide the root assurance result.
9. Preserve the append-only assessment history and deterministic freshness behavior.
10. Preserve the source namespace frozen before sealing. Do not allow a post-seal assessor to substitute an unrelated source.
11. Review `AssuranceGate` and make sure it performs a real typed IC-to-IC read of `is_assured(case_id, expected_definition_hash)` and blocks replayed `action_hash` values.
12. Add any missing adversarial Direct Mode tests you believe a reviewer would reasonably expect, especially around forged leader results, stale evidence, threshold edge cases, graph reachability, source substitution, malformed model output and definition-hash mismatch.
13. Do not invent deployment proof, contract addresses, transaction hashes, passing test counts or CI results.

## GITHUB + IMMUTABLE FIXTURES

The repository target is `Ifem1/assuregraph`.

After the first real commit containing `fixtures/` is pushed:

1. obtain that full 40-character commit SHA;
2. run `python scripts/pin_fixture_commit.py <FULL_COMMIT_SHA>`;
3. confirm the live integration test now fetches immutable raw GitHub URLs pinned to that commit;
4. commit and push the pin.

Do not leave `FIXTURE_COMMIT_PLACEHOLDER` in the final submission.

## LIVE STUDIONET PROOF

After Direct Mode is green, run the live integration lifecycle on **studionet**.

The final live proof must demonstrate at least:

- AssureGraph deploys on chain 61999;
- the example assurance DAG is created and sealed;
- a non-empty 64-hex definition hash exists;
- real public leaf evidence reaches consensus;
- the root becomes `ASSURED` only because the deterministic graph rules are satisfied;
- `refresh_case` creates a snapshot hash;
- AssuranceGate is deployed with the finalized AssureGraph address;
- the correctly pinned gate action succeeds;
- wrong-definition-hash execution is rejected;
- action replay is rejected.

If live tests expose fee-estimation requirements in the currently installed stable tooling, use the supported stable Studionet fee-estimation path. Do not change networks as a workaround.

## FINAL DOCUMENTATION

Update `DEPLOYMENT.md` only with evidence you actually produced:

- finalized AssureGraph address;
- finalized AssureGraph deploy transaction;
- finalized AssuranceGate address;
- finalized AssuranceGate deploy transaction;
- case creation/seal transactions;
- leaf assessment transactions;
- snapshot transaction;
- allowed gate transaction;
- rejected gate evidence;
- final definition hash;
- final snapshot hash;
- exact test commands and real test results.

If stable tooling makes any originally documented command inaccurate, correct the documentation to the command that actually worked.

## FINAL GATES

Before final push:

- `python scripts/preflight.py --final` must pass;
- Python compilation must pass;
- all Direct Mode tests must pass;
- the live Studionet lifecycle must pass;
- no secrets, private keys, `.env`, virtual environments, caches, build artefacts or unrelated files may be tracked;
- there must be no frontend;
- confirm every network reference remains stable Studionet / chain 61999;
- inspect `git diff`, `git status`, tracked files and the final GitHub repository after push.

Do not claim completion until all applicable checks actually pass and the remote repository contains the final committed code.

At the end, report exactly what changed, the real test results, live contract addresses/transaction evidence, final commit SHA, and any limitation that genuinely remains.
