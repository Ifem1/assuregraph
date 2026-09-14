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

Verified live deployment:

```text
AssureGraph address:      0x9136B931Da0E9FC6D57461d3B4896b8d36aA93AA
AssureGraph deploy tx:    0x16e7c094229a9c696f8c1b1a9a6be7a4d2ec2d4f11036b8084f254384e6bc2ab
AssuranceGate address:    0x7413d074aeD8A61cFdCd79184e199de2F2AF59d7
AssuranceGate deploy tx:  0x61311586ad8cba1eaef5e3f131e388df54592fe8317aa8430b5e02b5b069ff0c
Network:                  studionet
Chain ID:                 61999
```

### Final lifecycle evidence

```text
Case creation tx:         0x82cc689e94c644905b0aba626a82376145a9b738b8ddff5ef77ea686761b4bd2
Case seal tx:              0xe84d4adcbd54e76e8b130657d5fd7f79e9cbc4ede3159ccd0b6ecc5e0ae1e267
Auth assessment tx:       0x5a87a730af027b709558c72cebe97af971269c45786ca696667598f326851a36
Rollback assessment tx:   0x1a001b07618abbffd6ab2036d88871ff125596e9c23a73cde2a130c6c845a3cb
Runbook assessment tx:    0x19ef54eb3e73b8b466903322b5df367c8b84ee5bc72694269ee59f0a8702ef36
Snapshot refresh tx:      0xf12c9dc8b2e3b3c944b637fde70e5e2cc042476c924bddf486c5e8fea710c2fe
Allowed gate tx:          0x9c8e1ed7d26f6622fbcf59b7ff0ec16637658bf7e0bbc81ac70f4203085ae788
Rejected gate tx (wrong definition hash): 0x81e220bc3fe39aaa17d58c3a2d20526797267322205de5db47f409039e464573
Rejected gate tx (replay): 0xbed5dda4a9ad913607c9d62d8c20e6070d71579514bede7ad68f1bbf02a7fa39
Definition hash:          ebe71a1a6fe7e307a5b43a869bfd583ff8f4374ee081406a622a5d870b9958cf
Snapshot hash:            bd848eb352174bdf6b73e9a9acd63c1c09f6b08e6e7133aa3d1e21725858f055
```

Verified command: `gltest tests/integration -v -s --network studionet` — 1 passed.

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
