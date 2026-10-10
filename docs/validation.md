# Validation evidence — 9 October 2026

`pip install -e ".[dev]"` succeeded in a fresh virtual environment for this repository, independently of the other projects. Tests ran on Python 3.12.14 / Darwin arm64 CPU. Other Python versions in CI have not been executed locally here.

| Check | Result |
|---|---|
| Offline test suite | 11 passed |
| Ruff lint | Passed |
| Ruff formatting | Passed |
| Mocked/simulated integration | Tested within the scope below |
| Live NVIDIA hosted endpoint | Not executed |
| Self-hosted GPU endpoint | Not executed |
| Clinical/scientific domain validation | Not completed |

## Tested scope

Typed tool simulation, real stdio client discovery/call, stable seeds, explicit binder chain selection, request payloads, mocked HTTP failures and async parsing.

The GitHub workflows have been added or retained, but their remote execution has not been verified after these changes. Unit tests establish behavior on fixtures; they do not establish semantic or clinical correctness.

## Opt-in live contract test

Requires access and a real target fixture containing `pdb`, `contigs`, optional `hotspot_res`, and the expected generated `binder_chain`:

```bash
RUN_LIVE_NVIDIA=1 BIONEMO_TARGET_JSON=target.json pytest -q tests/test_live_contract.py
```

Set `NGC_API_KEY` or `NVIDIA_API_KEY`, and optionally `BIONEMO_BASE_URL`. Install the relevant live extra first (`.[bio]` for ai-scientist, `.[live]` for mcp-bionemo). The manual workflow requires `NVIDIA_API_KEY` and `BIONEMO_TARGET_JSON` secrets in the `nvidia-integration` environment. It exercises RFdiffusion and ProteinMPNN response contracts, not all scientific endpoints or biological validity.

The request changes follow the [RFdiffusion request schema](https://docs.api.nvidia.com/nim/reference/ipd-rfdiffusion-infer) and [ProteinMPNN chain-selection schema](https://docs.nvidia.com/nim/bionemo/proteinmpnn/latest/endpoints.html), checked 9 October 2026. Runtime behavior remains unverified.
