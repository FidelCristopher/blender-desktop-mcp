#!/usr/bin/env python3
"""
mcp_server.py
Model Context Protocol (MCP) Server for Blender Desktop Bridge.
Enables any AI model (Gemini, Claude, GPT, local models) to inspect, control,
and generate high-fidelity 3D assets in an active Blender desktop session.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add project root and scripts directories to Python path
CURRENT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = CURRENT_DIR / "skill" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import existing bridge tools
try:
    import send_to_blender
except ImportError:
    send_to_blender = None

try:
    import pick_image
except ImportError:
    pick_image = None


PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "blender-desktop-bridge"
SERVER_VERSION = "1.0.0"

DESIGN_DOC_PATH = CURRENT_DIR / "design.md"

TOOLS = [
    {
        "name": "execute_blender_code",
        "description": "Execute Python (bpy) script directly in the active Blender desktop session. Returns execution output or error trace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Valid Blender Python (bpy) code to execute in Blender."
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "get_blender_status",
        "description": "Check if Blender desktop bridge is actively running, responsive, and check connection details.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "pick_image_from_dialog",
        "description": "Open a native operating system File Explorer dialog window to let the user select a 2D reference image file.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_image_from_clipboard",
        "description": "Capture an image directly from the operating system clipboard (e.g. from Snipping Tool or screenshot) and save it locally.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_design_guidelines",
        "description": "Retrieve comprehensive 3D asset design standards, PBR shader specifications, and verified geometric recipes.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

RESOURCES = [
    {
        "uri": "blender://design-guidelines",
        "name": "Blender 3D Asset Design Guidelines",
        "description": "Living architectural specifications, PBR material parameters, and geometric construction logs.",
        "mimeType": "text/markdown"
    }
]

PROMPTS = [
    {
        "name": "generate_3d_asset",
        "description": "Generate a high-fidelity 3D model in Blender following production PBR and topology guidelines.",
        "arguments": [
            {
                "name": "description",
                "description": "Natural language description or specifications of the 3D asset.",
                "required": True
            }
        ]
    }
]


def handle_execute_blender_code(arguments):
    code = arguments.get("code", "")
    if not code:
        return {"content": [{"type": "text", "text": "Error: 'code' argument is required."}], "isError": True}

    if send_to_blender is None:
        return {"content": [{"type": "text", "text": "Error: send_to_blender module not found."}], "isError": True}

    # First attempt: HTTP POST
    success, data = send_to_blender.try_http_send(code)
    if success:
        out = data.get("result", "")
        err = data.get("error", "")
        msg = f"Executed successfully via HTTP:\n{out}"
        if err:
            msg += f"\nStderr / Warnings:\n{err}"
        return {"content": [{"type": "text", "text": msg}], "isError": False}

    # Second attempt: File Watcher
    success, data = send_to_blender.try_file_send(code)
    if success:
        out = data.get("result", "")
        err = data.get("error", "")
        msg = f"Executed successfully via File Watcher:\n{out}"
        if err:
            msg += f"\nStderr / Warnings:\n{err}"
        return {"content": [{"type": "text", "text": msg}], "isError": False}

    return {
        "content": [{
            "type": "text",
            "text": "Failed to connect to Blender desktop. Please ensure Blender is running and 'blender_bridge.py' is started in Blender's Scripting tab."
        }],
        "isError": True
    }


def handle_get_blender_status(arguments):
    if send_to_blender is None:
        return {"content": [{"type": "text", "text": "Error: send_to_blender module not found."}], "isError": True}

    # Quick test ping
    ping_code = "import bpy; print('[MCP] Ping status check OK')"
    success, data = send_to_blender.try_http_send(ping_code)
    if success:
        return {
            "content": [{
                "type": "text",
                "text": "Blender Bridge Status: ACTIVE (Connected via HTTP on port 9876)."
            }],
            "isError": False
        }

    success, data = send_to_blender.try_file_send(ping_code)
    if success:
        return {
            "content": [{
                "type": "text",
                "text": "Blender Bridge Status: ACTIVE (Connected via Shared File Watcher)."
            }],
            "isError": False
        }

    return {
        "content": [{
            "type": "text",
            "text": "Blender Bridge Status: INACTIVE. No response on port 9876 or file watcher. Please launch Blender and run 'blender_bridge.py'."
        }],
        "isError": False
    }


def handle_pick_image_from_dialog(arguments):
    if pick_image is None:
        return {"content": [{"type": "text", "text": "Error: pick_image module not found."}], "isError": True}

    image_path = pick_image.pick_via_file_dialog()
    if image_path:
        return {
            "content": [{
                "type": "text",
                "text": f"Selected image path: {image_path}"
            }],
            "isError": False
        }
    return {
        "content": [{
            "type": "text",
            "text": "File selection was canceled or no file was selected."
        }],
        "isError": False
    }


def handle_get_image_from_clipboard(arguments):
    if pick_image is None:
        return {"content": [{"type": "text", "text": "Error: pick_image module not found."}], "isError": True}

    image_path = pick_image.grab_from_clipboard()
    if image_path:
        return {
            "content": [{
                "type": "text",
                "text": f"Captured clipboard image saved to: {image_path}"
            }],
            "isError": False
        }
    return {
        "content": [{
            "type": "text",
            "text": "No image found in clipboard."
        }],
        "isError": False
    }


def handle_get_design_guidelines(arguments):
    if DESIGN_DOC_PATH.exists():
        try:
            content = DESIGN_DOC_PATH.read_text(encoding="utf-8")
            return {
                "content": [{"type": "text", "text": content}],
                "isError": False
            }
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error reading design guidelines: {e}"}], "isError": True}
    return {
        "content": [{"type": "text", "text": "design.md not found in project root."}],
        "isError": True
    }


TOOL_HANDLERS = {
    "execute_blender_code": handle_execute_blender_code,
    "get_blender_status": handle_get_blender_status,
    "pick_image_from_dialog": handle_pick_image_from_dialog,
    "get_image_from_clipboard": handle_get_image_from_clipboard,
    "get_design_guidelines": handle_get_design_guidelines
}


def send_response(response_dict):
    body = json.dumps(response_dict)
    sys.stdout.write(body + "\n")
    sys.stdout.flush()


def run_stdio_server():
    """Main loop handling JSON-RPC 2.0 messages over standard input and output."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            })
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Handle notifications (no response needed)
        if req_id is None:
            if method == "notifications/initialized":
                pass
            continue

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            })
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            })
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name)
            if handler:
                try:
                    result = handler(arguments)
                    send_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result
                    })
                except Exception as e:
                    send_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Error executing tool {tool_name}: {str(e)}"}],
                            "isError": True
                        }
                    })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found."
                    }
                })
        elif method == "resources/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": RESOURCES
                }
            })
        elif method == "resources/read":
            uri = params.get("uri")
            if uri == "blender://design-guidelines" and DESIGN_DOC_PATH.exists():
                text_content = DESIGN_DOC_PATH.read_text(encoding="utf-8")
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/markdown",
                                "text": text_content
                            }
                        ]
                    }
                })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Resource not found: {uri}"
                    }
                })
        elif method == "prompts/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": PROMPTS
                }
            })
        elif method == "prompts/get":
            prompt_name = params.get("name")
            if prompt_name == "generate_3d_asset":
                desc = params.get("arguments", {}).get("description", "")
                prompt_text = (
                    "You are an expert 3D modeling and Blender Python (bpy) assistant. "
                    "Follow production PBR standards and geometric topology rules.\n"
                    f"Asset Request: {desc}\n"
                    "Use the execute_blender_code tool to create and update the model directly in Blender."
                )
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": prompt_text
                                }
                            }
                        ]
                    }
                })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Prompt '{prompt_name}' not found."
                    }
                })
        else:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not implemented."
                }
            })


if __name__ == "__main__":
    run_stdio_server()
