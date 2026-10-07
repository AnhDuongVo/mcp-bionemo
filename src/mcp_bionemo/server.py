"""A Model Context Protocol (MCP) server for NVIDIA BioNeMo biology NIMs.

Background
----------
BioNeMo's biology models are available as NeMo Agent Toolkit agent skills and as HTTP NIM endpoints, but
not as an MCP server, so an MCP client (Claude Desktop, Cursor, an IDE agent, NeMo Agent Toolkit's own MCP
client) cannot discover or call RFdiffusion, ProteinMPNN or Boltz-2 as tools. This server wraps the NIM
endpoints in typed MCP tools with a schema the client can read.

It runs against a deterministic simulator by default, so it is safe to install and explore with no key.
Set BIONEMO_BACKEND=live to route the same tools to the real NIMs.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from .config import backend, backend_name

mcp = MCPServer("bionemo", version="0.1.0")


def _bio():
    return backend()


@mcp.tool()
def info() -> dict[str, Any]:
    """Return which backend is active (simulated or live) and the tools this server exposes."""
    return {
        "backend": backend_name(),
        "tools": ["design_backbone", "design_sequences", "fold_complex", "design_binder"],
        "note": "Set BIONEMO_BACKEND=live with an NGC/NVIDIA key (or BIONEMO_BASE_URL for a local NIM) to call real models.",
    }


@mcp.tool()
def design_backbone(input_pdb: str, contigs: str, hotspot_res: list[str] | None = None) -> dict[str, Any]:
    """Design a protein backbone with RFdiffusion.

    Args:
        input_pdb: the target structure as PDB text (the scaffold/target to design against).
        contigs: RFdiffusion contig string describing what to generate, e.g. "A1-100/0 50-60".
        hotspot_res: optional target residues the binder should contact, e.g. ["A59", "A83"].

    Returns a dict with `output_pdb` (the generated backbone as PDB text).
    """
    return _bio().rfdiffusion(input_pdb=input_pdb, contigs=contigs, hotspot_res=hotspot_res)


@mcp.tool()
def design_sequences(input_pdb: str, num_sequences: int = 8) -> dict[str, Any]:
    """Design amino-acid sequences that fold to a given backbone with ProteinMPNN.

    Args:
        input_pdb: the backbone (PDB text) to design sequences for.
        num_sequences: how many candidate sequences to return.

    Returns a dict with `mfasta` (FASTA of designs) and `scores` (lower is better).
    """
    return _bio().proteinmpnn(input_pdb=input_pdb, num_seq_per_target=num_sequences)


@mcp.tool()
def fold_complex(
    protein_sequences: list[str],
    ligand_smiles: list[str] | None = None,
    predict_affinity: bool = False,
) -> dict[str, Any]:
    """Co-fold one or more protein chains (optionally with small-molecule ligands) using Boltz-2.

    Args:
        protein_sequences: one amino-acid sequence per protein chain. Give the binder AND the target
            together to score the complex; a binder folded alone does not measure binding.
        ligand_smiles: optional list of SMILES strings for small-molecule ligands.
        predict_affinity: if true and a ligand is given, also return a binding-affinity estimate.

    Returns a dict with `structures`, `confidence_scores`, and (optionally) `affinities`.
    """
    polymers = [{"id": chr(ord("A") + i), "molecule_type": "protein", "sequence": s} for i, s in enumerate(protein_sequences)]
    ligands = None
    if ligand_smiles:
        ligands = [{"id": f"L{i}", "smiles": smi, "predict_affinity": predict_affinity} for i, smi in enumerate(ligand_smiles)]
    return _bio().boltz2(polymers=polymers, ligands=ligands)


@mcp.tool()
def design_binder(
    target_pdb: str,
    contigs: str,
    hotspot_res: list[str] | None = None,
    num_sequences: int = 4,
) -> dict[str, Any]:
    """Convenience pipeline: RFdiffusion backbone, then ProteinMPNN sequences for it, in one call.

    Returns a dict with `backbone_pdb` and `designs` (FASTA) plus `scores`. Fold the designs against
    the target with `fold_complex` to score binding.
    """
    bio = _bio()
    bb = bio.rfdiffusion(input_pdb=target_pdb, contigs=contigs, hotspot_res=hotspot_res)
    seqs = bio.proteinmpnn(input_pdb=bb["output_pdb"], num_seq_per_target=num_sequences)
    return {"backbone_pdb": bb["output_pdb"], "designs": seqs.get("mfasta", ""), "scores": seqs.get("scores", [])}


def main() -> None:
    """Entry point: run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
