# Using mcp-bionemo from NeMo Agent Toolkit

NeMo Agent Toolkit can consume any MCP server as a tool source. Point its MCP client at this server
(stdio transport, command `mcp-bionemo`), and the four tools below become callable from a NAT workflow:

- `design_backbone` (RFdiffusion)
- `design_sequences` (ProteinMPNN)
- `fold_complex` (Boltz-2, optional affinity)
- `design_binder` (RFdiffusion then ProteinMPNN, one call)

BioNeMo's models are otherwise available only as agent skills and raw NIM endpoints, so an MCP client has
no schema to discover them. Running this server gives every MCP client, NAT included, a typed interface.

To route the tools to the real NIMs instead of the simulator, set in the server environment:

```
BIONEMO_BACKEND=live
NGC_API_KEY=nvapi-...        # or BIONEMO_BASE_URL for a self-hosted NIM
```
