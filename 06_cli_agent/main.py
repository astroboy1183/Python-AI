# CLI Coding Agent — chain of thought, project scaffolding + code writing

from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import os
import json
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

# Anchored to the Python-AI root so all created projects land there
BASE_DIR: Path = Path(__file__).parent.parent.resolve()

# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a CLI coding agent. Your job is to scaffold project folder structures
and write code files exactly as the user requests.

You MUST reason out loud, step by step, before and during every action.

─────────────────────────────────────────────────────────────────
[Step 1 — Understand the request]
  • Re-state what the user wants in your own words.
  • Identify: project type, language, framework, any special requirements.

[Step 2 — Plan the structure]
  • List EVERY folder and file you intend to create, in creation order.
  • Briefly explain the purpose of each.

[Step 3 — Execute, one action at a time]
  • Before each tool call, announce it in plain text:
      "Creating folder: my-app/src"
      "Writing file:   my-app/src/index.js  — entry point for the Express server"
  • Call the appropriate tool immediately after the announcement.
  • After a file is written, summarise the code in 1-2 sentences.

[Step 4 — Confirm completion]
  • List a concise summary of everything created.
  • Suggest the next steps for the user (e.g. `npm install`, `pip install -r requirements.txt`).
─────────────────────────────────────────────────────────────────

Rules:
- NEVER skip narration — every tool call must be preceded by a plain-text announcement.
- All paths are RELATIVE to the working directory the user sees at startup.
- Write COMPLETE, working code. No placeholders unless the user explicitly asks for a skeleton.
- If the user asks you to add code to an existing file, read it first, then overwrite with the updated version.
- Keep your reasoning concise; do not repeat yourself."""

# ── Tool implementations ───────────────────────────────────────────────────────

def create_folder(path: str) -> str:
    target = BASE_DIR / path
    try:
        target.mkdir(parents=True, exist_ok=True)
        return json.dumps({"success": True, "path": str(target)})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def create_file(path: str, content: str) -> str:
    target = BASE_DIR / path
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return json.dumps({"success": True, "path": str(target), "bytes": len(content.encode())})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def list_directory(path: str = ".") -> str:
    target = BASE_DIR / path
    try:
        if not target.exists():
            return json.dumps({"error": f"'{path}' does not exist."})
        entries = [
            {"name": e.name, "type": "dir" if e.is_dir() else "file"}
            for e in sorted(target.iterdir())
        ]
        return json.dumps({"path": str(target), "entries": entries})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def read_file(path: str) -> str:
    target = BASE_DIR / path
    try:
        if not target.exists():
            return json.dumps({"error": f"'{path}' does not exist."})
        return json.dumps({"path": str(target), "content": target.read_text(encoding="utf-8")})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ── Tool schemas ───────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a directory (and any missing parents) on the filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the folder, e.g. 'my-app/src/components'",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": (
                "Create or overwrite a file with the given content. "
                "Parent directories are created automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the file, e.g. 'my-app/src/index.js'",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to inspect. Defaults to '.' (working directory).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full content of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the file to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "create_folder": create_folder,
    "create_file": create_file,
    "list_directory": list_directory,
    "read_file": read_file,
}

# ── Result display helpers ─────────────────────────────────────────────────────

def _display_result(fn_name: str, fn_args: dict, parsed: dict) -> None:
    if fn_name == "create_folder":
        if parsed.get("success"):
            console.print(f"  [bold green]✓[/bold green] Folder ready: [cyan]{fn_args['path']}[/cyan]")
        else:
            console.print(f"  [bold red]✗[/bold red] {parsed.get('error')}")

    elif fn_name == "create_file":
        if parsed.get("success"):
            kb = parsed.get("bytes", 0) / 1024
            console.print(
                f"  [bold green]✓[/bold green] File written: [cyan]{fn_args['path']}[/cyan] "
                f"[dim]({kb:.1f} KB)[/dim]"
            )
        else:
            console.print(f"  [bold red]✗[/bold red] {parsed.get('error')}")

    elif fn_name == "list_directory":
        if "entries" in parsed:
            console.print(f"  [bold blue]📁[/bold blue] [cyan]{fn_args.get('path', '.')}[/cyan]")
            for entry in parsed["entries"]:
                icon = "📁" if entry["type"] == "dir" else "📄"
                console.print(f"      {icon}  {entry['name']}")
        else:
            console.print(f"  [bold red]✗[/bold red] {parsed.get('error')}")

    elif fn_name == "read_file":
        if "content" in parsed:
            lines = parsed["content"].count("\n") + 1
            console.print(
                f"  [bold blue]📖[/bold blue] Read: [cyan]{fn_args['path']}[/cyan] "
                f"[dim]({lines} lines)[/dim]"
            )
        else:
            console.print(f"  [bold red]✗[/bold red] {parsed.get('error')}")


# ── Streaming agent loop ───────────────────────────────────────────────────────

def agent_turn(messages: list) -> None:
    while True:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=True,
        )

        full_content = ""
        tool_calls: list[dict] = []

        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta

            # Stream reasoning text live
            if delta.content:
                print(delta.content, end="", flush=True)
                full_content += delta.content

            # Accumulate tool-call deltas
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    while len(tool_calls) <= idx:
                        tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                    if tc_delta.id:
                        tool_calls[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tool_calls[idx]["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls[idx]["function"]["arguments"] += tc_delta.function.arguments

        if full_content:
            print()  # newline after streamed text

        # No tool calls → turn is complete
        if not tool_calls:
            messages.append({"role": "assistant", "content": full_content})
            return

        # Append assistant message with tool calls
        messages.append({
            "role": "assistant",
            "content": full_content or None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {"name": tc["function"]["name"], "arguments": tc["function"]["arguments"]},
                }
                for tc in tool_calls
            ],
        })

        # Execute each tool and feed result back
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            fn_args = json.loads(tc["function"]["arguments"])

            fn = TOOL_FUNCTIONS.get(fn_name)
            result = fn(**fn_args) if fn else json.dumps({"error": "unknown tool"})
            parsed = json.loads(result)

            _display_result(fn_name, fn_args, parsed)
            console.print()

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    global BASE_DIR

    console.print(
        Panel.fit(
            "[bold cyan]CLI Coding Agent[/bold cyan]\n"
            "[dim]Scaffolds projects and writes code — step by step, out loud[/dim]",
            border_style="cyan",
        )
    )
    console.print(f"[dim]Working directory: {BASE_DIR}[/dim]")
    console.print("[dim]Commands: 'cd <path>' to change working dir  |  'quit' to exit[/dim]\n")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\nWorking directory: {BASE_DIR}",
        }
    ]

    while True:
        try:
            user_input = console.input("[bold yellow]You:[/bold yellow] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            console.print("[dim]Goodbye![/dim]")
            break

        # Allow the user to change the working directory mid-session
        if user_input.lower().startswith("cd "):
            new_dir = Path(user_input[3:].strip()).expanduser()
            if not new_dir.is_absolute():
                new_dir = BASE_DIR / new_dir
            if new_dir.exists() and new_dir.is_dir():
                BASE_DIR = new_dir.resolve()
                messages[0]["content"] = SYSTEM_PROMPT + f"\n\nWorking directory: {BASE_DIR}"
                console.print(f"[dim]Working directory changed to: {BASE_DIR}[/dim]\n")
            else:
                console.print(f"[bold red]Directory not found:[/bold red] {new_dir}\n")
            continue

        messages.append({"role": "user", "content": user_input})
        console.print("\n[bold green]Agent:[/bold green]\n")
        agent_turn(messages)
        console.print()


if __name__ == "__main__":
    main()
