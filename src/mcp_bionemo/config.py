"""Backend selection for the BioNeMo MCP server.

By default the server runs against a deterministic in-process SIMULATOR, so it works with no GPU,
no key and no network. Set BIONEMO_BACKEND=live (and an NGC/NVIDIA key, or BIONEMO_BASE_URL for a
self-hosted NIM) to call the real BioNeMo NIMs.
"""

from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv

from .bionemo import BioNeMo, BioNeMoSettings, NIMBioNeMo, SimulatedBioNeMo

load_dotenv(find_dotenv(usecwd=True))


def backend() -> BioNeMo:
    mode = os.getenv("BIONEMO_BACKEND", "simulated").strip().lower()
    if mode in {"live", "nim", "real"}:
        return NIMBioNeMo(BioNeMoSettings())
    seed = int(os.getenv("BIONEMO_SIM_SEED", "0"))
    return SimulatedBioNeMo(seed=seed)


def backend_name() -> str:
    return "live" if os.getenv("BIONEMO_BACKEND", "simulated").strip().lower() in {"live", "nim", "real"} else "simulated"
