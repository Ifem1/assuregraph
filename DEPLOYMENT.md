# Deployment — stable Studionet

AssureGraph is targeted at the stable hosted GenLayer Studio environment only.

```text
Network alias: studionet
RPC:           https://studio.genlayer.com/api
Chain ID:      61999
Currency:      GEN
```

Do not change the project to a different Studio environment during this handoff.

## 1. Install tooling

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Run local/static checks

```bash
python scripts/preflight.py
pytest tests/direct -q
```

Fix every failure before live deployment.

## 3. Push the first commit before live evidence testing

The integration test intentionally reads immutable public evidence from this repository.

After the first push to `Ifem1/assuregraph`, get the commit SHA that contains the files under `fixtures/`.

Then run:

```bash
python scripts/pin_fixture_commit.py <FULL_COMMIT_SHA>
```

Commit that change.

This changes the integration evidence URLs from a placeholder to:

```text
https://raw.githubusercontent.com/Ifem1/assuregraph/<FULL_COMMIT_SHA>/fixtures/...
```

so every validator sees immutable bytes.

## 4. Verify the network before signing

```bash
genlayer network set studionet
genlayer network info
```

The effective chain must be **61999** and the RPC must be `https://studio.genlayer.com/api`.

If those values do not match, stop and correct the network configuration before funding or signing.

## 5. Run the live lifecycle test

```bash
gltest tests/integration -v -s --network studionet
```

The lifecycle must prove:

- AssureGraph deploys;
- the assurance definition seals;
- three public leaf assessments reach semantic consensus;
- the deterministic root becomes `ASSURED`;
- the snapshot hash is produced;
- AssuranceGate deploys with the primitive address;
- a correctly hash-pinned action succeeds;
- a wrong-definition-hash action is refused.

## 6. Canonical deployments

Deploy canonical instances only after tests are green.

Primitive:

```bash
genlayer network set studionet
genlayer deploy --contract contracts/assuregraph.py
```

Consumer deployment requires the finalized AssureGraph address as its constructor argument. Use Studio or the CLI/SDK path supported by the installed stable tooling.

Do not fabricate addresses in the documentation. Record only finalized live values.

### Finalized deployment evidence

Fill this section after deployment:

```text
AssureGraph address:      <FINALIZED_ADDRESS>
AssureGraph deploy tx:    <FINALIZED_TX_HASH>
AssuranceGate address:    <FINALIZED_ADDRESS>
AssuranceGate deploy tx:  <FINALIZED_TX_HASH>
Network:                  studionet
Chain ID:                 61999
```

### Final lifecycle evidence

```text
Case creation tx:         <FINALIZED_TX_HASH>
Case seal tx:             <FINALIZED_TX_HASH>
Auth assessment tx:       <FINALIZED_TX_HASH>
Rollback assessment tx:   <FINALIZED_TX_HASH>
Runbook assessment tx:    <FINALIZED_TX_HASH>
Snapshot refresh tx:      <FINALIZED_TX_HASH>
Allowed gate tx:          <FINALIZED_TX_HASH>
Rejected gate tx:         <FINALIZED_TX_HASH>
Definition hash:          <64_HEX>
Snapshot hash:            <64_HEX>
```

## 7. Final preflight

```bash
python scripts/preflight.py --final
```

Final mode rejects:

- an unpinned fixture commit;
- missing deployment evidence placeholders;
- accidental network-target drift;
- Python syntax errors;
- frontend directories.
