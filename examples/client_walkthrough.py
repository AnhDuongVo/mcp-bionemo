"""Run a real stdio MCP client against the offline server: python examples/client_walkthrough.py."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "mcp_bionemo.server"], env={**os.environ, "BIONEMO_BACKEND": "simulated"}
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        assert {"info", "design_backbone", "design_sequences", "fold_complex", "design_binder"} <= names
        result = await session.call_tool("info", {})
        assert not result.is_error
        payload = result.structured_content
        if payload is None:
            payload = json.loads(result.content[0].text)
        assert payload["backend"] == "simulated"
        print("Discovered:", ", ".join(sorted(names)))
        arguments = {"input_pdb": "HEADER SYNTHETIC SIMULATOR INPUT\nEND\n", "contigs": "A1-50/0 50-60"}
        print("Calling design_backbone:", json.dumps(arguments))
        result = await session.call_tool("design_backbone", arguments)
        assert not result.is_error
        backbone = result.structured_content
        if backbone is None:
            backbone = json.loads(result.content[0].text)
        pdb = backbone["output_pdb"]
        assert isinstance(pdb, str) and "ATOM" in pdb
        print("Returned output_pdb:", len(pdb), "characters")
        print("First generated atom:", next(line for line in pdb.splitlines() if line.startswith("ATOM")))
        print("Simulator call succeeded; actual stdio MCP transport, no live NIM inference")


if __name__ == "__main__":
    asyncio.run(main())
