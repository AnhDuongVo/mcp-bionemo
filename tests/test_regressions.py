import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from mcp_bionemo.bionemo import BioNeMoSettings, NIMBioNeMo


@pytest.mark.parametrize("seed", [0, 42])
def test_request_payload_preserves_seed_and_chains(monkeypatch, seed):
    client = NIMBioNeMo(BioNeMoSettings(base_url="http://localhost:8000"))
    captured = []
    monkeypatch.setattr(client, "_post", lambda tool, body: captured.append((tool, body)) or {})
    client.rfdiffusion("pdb", "A1-20/0 50-70", random_seed=seed)
    client.proteinmpnn("pdb", input_pdb_chains=["B"])
    assert captured[0][1]["random_seed"] == seed
    assert captured[1][1]["input_pdb_chains"] == ["B"]


def test_async_missing_request_id_fails(monkeypatch):
    client = NIMBioNeMo(BioNeMoSettings(base_url="http://localhost:8000"))
    client._requests = SimpleNamespace(post=lambda *a, **kw: SimpleNamespace(status_code=202, headers={}))
    with pytest.raises(ValueError, match="nvcf-reqid"):
        client.rfdiffusion("pdb", "contigs")


def test_http_error_is_propagated():
    client = NIMBioNeMo(BioNeMoSettings(base_url="http://localhost:8000"))

    def fail():
        raise RuntimeError("HTTP 401")

    client._requests = SimpleNamespace(post=lambda *a, **kw: SimpleNamespace(status_code=401, raise_for_status=fail))
    with pytest.raises(RuntimeError, match="401"):
        client.rfdiffusion("pdb", "contigs")


def test_simulation_stable_across_processes():
    code = "import json; from mcp_bionemo.bionemo import SimulatedBioNeMo; print(json.dumps(SimulatedBioNeMo().proteinmpnn('pdb')))"
    outputs = [
        subprocess.check_output([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": seed})
        for seed in ["1", "2"]
    ]
    assert outputs[0] == outputs[1]


def test_successful_async_response_parsing():
    client = NIMBioNeMo(BioNeMoSettings(base_url="http://localhost:8000"))
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return SimpleNamespace(status_code=200, raise_for_status=lambda: None, json=lambda: {"output_pdb": "ATOM"})

    client._requests = SimpleNamespace(
        post=lambda *a, **kw: SimpleNamespace(status_code=202, headers={"nvcf-reqid": "request-id"}), get=get
    )
    assert client.rfdiffusion("pdb", "contigs")["output_pdb"] == "ATOM"
    assert calls == ["http://localhost:8000/v1/status/request-id"]
