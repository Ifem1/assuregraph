# Build status at handoff

## Completed in the generated repository

- AssureGraph primitive implemented.
- AssuranceGate consumer implemented.
- Stable Studionet configuration fixed to chain ID 61999 / `https://studio.genlayer.com/api`.
- Direct Mode test suite authored.
- Live Studionet lifecycle test authored.
- Immutable fixture-pinning helper authored.
- Reviewer documentation, architecture, consensus and threat-model documentation authored.
- Static repository preflight implemented.
- Python sources compile successfully with `py_compile`.
- `python scripts/preflight.py` passes.
- Repository contains no frontend.

## Not claimed as completed

Direct Mode execution and live Studionet deployment were not run in the generation environment because that environment could not resolve external package hosts while installing the pinned GenLayer test tooling. The failure occurred during dependency download, before the project tests ran.

The handoff agent must therefore install the dependencies in its normal networked environment, run all Direct Mode tests, fix any runtime incompatibility rather than hiding it, then run the stable Studionet lifecycle and record only real finalized deployment evidence.

No deployment address, transaction hash or passing test count has been fabricated.
