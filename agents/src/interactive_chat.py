"""Interactive chat session that can interpret tool calls.

Usage:
  python interactive_chat.py

This script provides a small framework for chatting with an LLM and interpreting
tool calls that the model returns as JSON objects. It ships with a working
`mock` backend so you can run and test the interactive behaviour without any
API keys. Replace or extend the `LLMClient` class to integrate real LLMs
(OpenAI, Azure, Ollama, etc.).
"""
import json
import re
import shlex
import subprocess
import sys
from typing import Any, Dict, List


def extract_json_object(text: str) -> Dict[str, Any] | None:
    """Find the first JSON object in the given text and return it as dict.
    Returns None if no JSON object could be parsed.
    """
    m = re.search(r"(\{[\s\S]*\})", text)
    if not m:
        return None
    candidate = m.group(1)
    try:
        return json.loads(candidate)
    except Exception:
        return None


class LLMClient:
    """Pluggable LLM client interface. Implement `get_response` for real backends."""

    def __init__(self, backend: str = "mock", model: str | None = None):
        self.backend = backend
        self.model = model or "mock-model"

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Return the model's response text for a list of messages.

        The `messages` list is a list of dicts with keys: `role` and `content`.
        """
        if self.backend == "mock":
            return self._mock_response(messages)

        # Real backends can be implemented by subclassing or extending this
        # method. For example: call OpenAI, AzureOpenAI, or Ollama here.
        raise RuntimeError(f"Unsupported backend: {self.backend}")

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        last = messages[-1]["content"].lower()
        # Simple behaviour: if user asked to list directory, return a tool call
        if any(word in last for word in ("list dir", "list directory", "ls", "show files")):
            return json.dumps({"tool": "list_dir", "path": "."})
        if "read file" in last or "open file" in last:
            # expect a path after a colon
            parts = last.split(":", 1)
            path = parts[1].strip() if len(parts) > 1 else "./README.md"
            return json.dumps({"tool": "read_file", "path": path})
        if "run" in last and "command" in last:
            # crude extraction: the user may type: run command: dir
            parts = last.split(":", 1)
            cmd = parts[1].strip() if len(parts) > 1 else "echo hello"
            return json.dumps({"tool": "shell", "command": cmd})

        # Default conversational reply
        return "I heard you. If you want me to run a tool, ask me to `list dir`, `read file: path`, or `run command: ...`"


def run_shell_command(cmd: str) -> Dict[str, Any]:
    """Run a shell command using PowerShell and return result dict."""
    if sys.platform.startswith("win"):
        # Use PowerShell (pwsh) if available
        runner = ["pwsh", "-NoProfile", "-Command", cmd]
    else:
        # On other platforms use /bin/sh -c
        runner = ["/bin/sh", "-c", cmd]
    try:
        completed = subprocess.run(runner, capture_output=True, text=True, timeout=30)
        return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


def handle_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Execute supported tools and return a result dict."""
    tool = tool_call.get("tool")
    if not tool:
        return {"error": "no tool specified"}

    if tool == "shell":
        cmd = tool_call.get("command") or tool_call.get("cmd")
        if not cmd:
            return {"error": "missing command"}
        return run_shell_command(cmd)

    if tool == "read_file":
        path = tool_call.get("path")
        if not path:
            return {"error": "missing path"}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {"content": f.read()}
        except Exception as e:
            return {"error": str(e)}

    if tool == "write_file":
        path = tool_call.get("path")
        content = tool_call.get("content", "")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"ok": True}
        except Exception as e:
            return {"error": str(e)}

    if tool == "list_dir":
        import os

        path = tool_call.get("path") or "."
        try:
            entries = os.listdir(path)
            return {"entries": entries}
        except Exception as e:
            return {"error": str(e)}

    return {"error": f"unsupported tool: {tool}"}


def run_interactive(backend: str = "mock"):
    client = LLMClient(backend=backend)
    messages: List[Dict[str, str]] = []
    print("Interactive LLM session (type 'exit' or Ctrl-C to quit).")
    try:
        while True:
            user = input("You: ")
            if user.strip().lower() in ("exit", "quit"):
                print("Goodbye")
                break
            messages.append({"role": "user", "content": user})

            # Ask LLM for a response
            resp_text = client.get_response(messages)
            print("LLM:")
            print(resp_text)

            # Check for tool calls encoded as JSON
            tool_call = extract_json_object(resp_text)
            if tool_call:
                print("Detected tool call:", tool_call)
                result = handle_tool_call(tool_call)
                print("Tool result:")
                try:
                    print(json.dumps(result, indent=2))
                except Exception:
                    print(result)

                # Send tool result back to the model as assistant-tool message
                tool_message = {
                    "role": "tool",
                    "content": json.dumps({"tool_call": tool_call, "result": result}),
                }
                messages.append({"role": "assistant", "content": resp_text})
                messages.append(tool_message)
                # Let the LLM continue (in this simple framework we immediately ask for follow-up)
                followup = client.get_response(messages)
                print("LLM (after tool):")
                print(followup)
                messages.append({"role": "assistant", "content": followup})
            else:
                messages.append({"role": "assistant", "content": resp_text})

    except KeyboardInterrupt:
        print("\nSession interrupted. Goodbye.")


if __name__ == "__main__":
    # Default to mock backend so the script is runnable out-of-the-box.
    backend = "mock"
    if len(sys.argv) > 1:
        backend = sys.argv[1]
    run_interactive(backend=backend)
