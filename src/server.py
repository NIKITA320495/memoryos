# src/server.py
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from src.tools import (
    tool_store_memory,
    tool_search_memory,
    tool_get_memory,
    tool_update_memory,
    tool_delete_memory,
    tool_list_memories,
)

app = Server("memoryos")

# ── 1. Declare all tools ───────────────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="store_memory",
            description=(
                "Store a new long-term memory for a user. "
                "Use this when the user shares a preference, fact, or "
                "important context you should remember across sessions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text":       {"type": "string",  "description": "The memory content to store"},
                    "user_id":    {"type": "string",  "description": "Unique user identifier"},
                    "tags":       {"type": "array", "items": {"type": "string"}, "description": "Optional tags"},
                    "importance": {"type": "integer", "minimum": 1, "maximum": 10, "description": "1=trivial, 10=critical"},
                },
                "required": ["text", "user_id"],
            },
        ),
        types.Tool(
            name="search_memory",
            description=(
                "Semantically search a user's memories. "
                "Use this at the start of any conversation to retrieve "
                "relevant past context before responding."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query":   {"type": "string",  "description": "Natural language search query"},
                    "user_id": {"type": "string",  "description": "Unique user identifier"},
                    "top_k":   {"type": "integer", "description": "Number of results (default 5)"},
                },
                "required": ["query", "user_id"],
            },
        ),
        types.Tool(
            name="get_memory",
            description="Retrieve a specific memory by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "The memory UUID"},
                },
                "required": ["memory_id"],
            },
        ),
        types.Tool(
            name="update_memory",
            description="Update the text content of an existing memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "The memory UUID to update"},
                    "new_text":  {"type": "string", "description": "Replacement text"},
                },
                "required": ["memory_id", "new_text"],
            },
        ),
        types.Tool(
            name="delete_memory",
            description="Permanently delete a memory by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "The memory UUID to delete"},
                },
                "required": ["memory_id"],
            },
        ),
        types.Tool(
            name="list_memories",
            description="List all stored memories for a user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique user identifier"},
                },
                "required": ["user_id"],
            },
        ),
    ]

# ── 2. Route tool calls ────────────────────────────────────────────────────────
@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:

    handlers = {
        "store_memory":  lambda a: tool_store_memory(
                            text=a["text"],
                            user_id=a["user_id"],
                            tags=a.get("tags", []),
                            importance=a.get("importance", 5),
                         ),
        "search_memory": lambda a: tool_search_memory(
                            query=a["query"],
                            user_id=a["user_id"],
                            top_k=a.get("top_k", 5),
                         ),
        "get_memory":    lambda a: tool_get_memory(a["memory_id"]),
        "update_memory": lambda a: tool_update_memory(a["memory_id"], a["new_text"]),
        "delete_memory": lambda a: tool_delete_memory(a["memory_id"]),
        "list_memories": lambda a: tool_list_memories(a["user_id"]),
    }

    handler = handlers.get(name)
    if not handler:
        result = json.dumps({"error": f"Unknown tool: {name}"})
    else:
        try:
            result = handler(arguments)
        except Exception as e:
            result = json.dumps({"error": str(e)})

    return [types.TextContent(type="text", text=result)]

# ── 3. Run ─────────────────────────────────────────────────────────────────────
async def main():
    print("[MemoryOS] Server starting...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())