"""The tools work end to end against the simulator (no key, no network)."""

from __future__ import annotations

from mcp_bionemo import server


def test_info_reports_simulated_by_default():
    out = server.info()
    assert out["backend"] == "simulated"
    assert "design_binder" in out["tools"]


def test_backbone_then_sequences():
    bb = server.design_backbone(input_pdb="HEADER\nEND\n", contigs="A1-50/0 50-60")
    assert "output_pdb" in bb and "ATOM" in bb["output_pdb"]
    seqs = server.design_sequences(input_pdb=bb["output_pdb"], num_sequences=4)
    assert len(seqs["scores"]) == 4
    assert seqs["mfasta"].count(">") == 4


def test_fold_complex_with_affinity():
    out = server.fold_complex(
        protein_sequences=["MKTAYIAKQR", "GGGSGGGS"],
        ligand_smiles=["CC(=O)O"],
        predict_affinity=True,
    )
    assert out["confidence_scores"]
    assert "affinities" in out


def test_design_binder_pipeline():
    out = server.design_binder(target_pdb="HEADER\nEND\n", contigs="A1-50/0 50-60", num_sequences=3)
    assert out["backbone_pdb"]
    assert len(out["scores"]) == 3
