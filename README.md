# Blender Desktop Bridge MCP Server

A bidirectional Model Context Protocol (MCP) server that connects AI models (Gemini, Claude, GPT, Antigravity, and local LLMs) directly to an active Blender Desktop application.

The server allows AI coding agents and desktop assistants to inspect the Blender scene, open native file dialogs for 2D reference images, capture clipboard images, execute Python (bpy) scripts, and generate high-fidelity 3D assets with real-time viewport updates.

---

## Architecture Overview

```
+-----------------------------------------------------------------+
|                       AI Client Application                     |
|        (Pi Agent, Claude Desktop, Cursor, Antigravity IDE)      |
|                                                                 |
|   User Prompt: "Create a photorealistic crystal glass tumbler"  |
|       |                                                         |
|       v                                                         |
|   [LLM / Reasoning Model]                                       |
|       |                                                         |
|       v                                                         |
|   [MCP Tool Call: execute_blender_code(code)]                   |
+-------------------------------+---------------------------------+
                                | (JSON-RPC over stdio)
                                v
+-----------------------------------------------------------------+
|               blender-desktop-bridge (mcp_server.py)            |
|                                                                 |
|   - Exposes Tools: execute_blender_code, get_blender_status,    |
|                    pick_image_from_dialog, get_image_clipboard  |
|   - Exposes Resources: blender://design-guidelines              |
|   - Exposes Prompts: generate_3d_asset                          |
+-------------------------------+---------------------------------+
                                |
             +------------------+------------------+
             |                                     |
   (Primary: HTTP REST POST)             (Fallback: Shared File Watcher)
   http://localhost:9876/execute         ~/.blender_bridge/task.py
             |                                     |
             v                                     v
+-----------------------------------------------------------------+
|                      Blender Desktop GUI                        |
|                                                                 |
|   [blender_bridge.py] (Threaded Server + Modal Timer)           |
|       |                                                         |
|       v                                                         |
|   bpy.app.timers (Main Thread Execution)                        |
|       |                                                         |
|       +---> Executes bpy script (BMesh, Lathe, PBR Shaders)     |
|       +---> Immediate 3D Viewport Redraw                        |
|                                                                 |
|   3D Asset renders instantly in the Blender 3D Viewport!        |
+-----------------------------------------------------------------+
```

### Key Technical Characteristics

1. **Dual Transport Bridge:**
   - **HTTP REST Endpoint (Primary):** Connects to `http://localhost:9876/execute` with automatic WSL2 host gateway IP resolution for near-zero latency execution.
   - **Shared File Watcher (Zero-Configuration Fallback):** Reads `~/.blender_bridge/task.py` polled at 100ms intervals by Blender's modal timer loop, bypassing Windows/WSL firewall barriers.

2. **Universal Compatibility:**
   - Adheres strictly to the standard Model Context Protocol (MCP) JSON-RPC 2.0 specification over `stdio`.
   - Zero external package dependencies in the MCP server: runs directly on standard Python 3.10+ without requiring `pip install`.

3. **High-Fidelity 3D Pipeline:**
   - Preserves advanced procedural material generation (Subsurface Scattering, transmission weight, index of refraction, micro-bump textures).
   - Automated 2K PBR texture baking (Base Color, Roughness, Tangent Normal) and embedded `.glb` export via Cycles emission pass.

---

## MCP Tools and Capabilities

The server exposes the following tools to connected AI models:

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `execute_blender_code` | `code: string` | Executes Python (`bpy`) script directly inside active Blender desktop. Returns stdout, evaluation results, and error traces. |
| `get_blender_status` | none | Checks whether the Blender desktop listener is active and responsive via HTTP or file watcher. |
| `pick_image_from_dialog` | none | Launches a native operating system File Explorer dialog window allowing the user to select a 2D reference image. |
| `get_image_from_clipboard` | none | Captures an image from the system clipboard (e.g., from Snipping Tool or screenshot) and saves it to a local temporary path. |
| `get_design_guidelines` | none | Retrieves verified 3D asset architecture rules, lathe specifications, and PBR shader parameters from `design.md`. |
| `search_recipe_library` | `query: string`, `category?: string` | Searches verified 3D recipes by keyword. If no match exists, automatically returns component blocks and universal 3D quality standards. |
| `save_verified_recipe` | `asset_name: string`, `category: string`, `code: string`, `notes?: string` | Permanently saves a verified Blender Python script to the modular recipe library and logs it to `design.md` for continuous self-learning. |

The server also provides:
- **Resource:** `blender://design-guidelines` providing full access to `design.md`.
- **Prompt Template:** `generate_3d_asset` for consistent asset scaffolding.

---

## Directory Structure

```
gemini-desktop-bridge-skill/
|-- README.md                      # Comprehensive English documentation
|-- design.md                      # Living 3D asset design log and specifications
|-- mcp_server.py                  # Standalone MCP stdio server (JSON-RPC 2.0)
|-- blender_bridge.py              # Main listener script executed inside Blender
|-- install.sh                     # Automated installation script
|-- blender_addon/
|   \-- blender_bridge.py          # Blender add-on packaged listener
|-- skill/
|   |-- SKILL.md                   # Pi Agent Skill instructions and memory bank
|   \-- scripts/
|       |-- send_to_blender.py     # Dual-transport dispatch client
|       |-- pick_image.py          # Native OS file dialog and clipboard picker
|       \-- bake_pbr_export_glb.py # Automated 2K PBR texture baking and GLB exporter
\-- examples/
    |-- 01_coffee_cup.py           # Example: Procedural ceramic coffee cup
    |-- 02_lowpoly_car.py          # Example: Low-poly vehicle
    |-- 03_export_glb.py           # Example: Glowing crystal and GLB export
    \-- recipes/                   # Production-verified parametric recipes
```

---

## Setup and Installation

### Step 1: Run Bridge Listener in Blender Desktop

1. Launch **Blender** on your computer.
2. Navigate to the **Scripting** workspace tab at the top.
3. Open `blender_addon/blender_bridge.py` from this repository.
4. Click **Run Script** (shortcut: `Alt + P`).
5. Open the 3D Viewport sidebar by pressing `N`. The **MCP Bridge** tab will indicate:
   ```
   Status: Active (Port 9876)
   ```

*Tip: You can also install `blender_bridge.py` as a permanent Blender Add-on via `Edit > Preferences > Add-ons > Install`.*

---

### Step 2: Configure Your MCP Client

#### For Pi Agent
Run the installation script:
```bash
./install.sh
```
Or register manually in `~/.pi/agent/mcp.json`:
```json
{
  "mcpServers": {
    "blender-bridge": {
      "command": "python3",
      "args": [
        "/mnt/c/Users/Pongo/gemini-desktop-bridge-skill/mcp_server.py"
      ],
      "exposure": "direct",
      "description": "Blender Desktop Bridge MCP server for controlling Blender and generating 3D assets"
    }
  }
}
```

Verify connection:
```bash
pi mcp list
```

#### For Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "blender-bridge": {
      "command": "python3",
      "args": [
        "C:\\Users\\Pongo\\gemini-desktop-bridge-skill\\mcp_server.py"
      ]
    }
  }
}
```

#### For Cursor / Antigravity IDE / VS Code
Add to your MCP configuration settings:
```json
{
  "mcpServers": {
    "blender-bridge": {
      "command": "python3",
      "args": [
        "/mnt/c/Users/Pongo/gemini-desktop-bridge-skill/mcp_server.py"
      ]
    }
  }
}
```

---

## Usage Workflow

When prompting your AI assistant:

1. **Provide Reference via Native Dialog:**
   Ask the assistant to pick an image:
   - *"Let me pick an image from my computer to model in Blender"*
   - The assistant invokes `pick_image_from_dialog`, opening a native File Explorer window for selection.

2. **Provide Reference via Clipboard:**
   - Take a screenshot using Snipping Tool (`Win + Shift + S`).
   - Tell the assistant: *"Model the 3D object from my clipboard screenshot in Blender"*.
   - The assistant calls `get_image_from_clipboard` to read the image data.

3. **Natural Language Text Modeling:**
   - *"Create a stylized low-poly sports car in Blender"*
   - *"Create a photorealistic iced matcha latte in a crystal glass tumbler"*
   - The assistant generates Python `bpy` commands and calls `execute_blender_code`.
   - The asset appears live in your Blender 3D Viewport.

---

## Manual Verification via CLI

You can verify communication without an AI client:

```bash
# Check listener status
python3 skill/scripts/send_to_blender.py --status

# Execute procedural coffee cup recipe
python3 skill/scripts/send_to_blender.py --file examples/01_coffee_cup.py

# Execute low-poly car recipe
python3 skill/scripts/send_to_blender.py --file examples/02_lowpoly_car.py
```

---

## Author and License

Developed by Fidel Cristopher.
Open-source under standard permissive terms. Contributions and extensions are welcome.
