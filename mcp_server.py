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

SYSTEM_INSTRUCTIONS = """
MANDATORY 3D MODELING & SHADING QUALITY DIRECTIVES (PRODUCTION STANDARD):

Whenever creating or modifying 3D assets in Blender via execute_blender_code:

1. MANDATORY 2K STANDARD RESOLUTION:
   Always configure scene rendering to 2K (2048 x 2048):
   bpy.context.scene.render.resolution_x = 2048
   bpy.context.scene.render.resolution_y = 2048

2. TOPOLOGY & WATERTIGHT GEOMETRY:
   - All meshes must be 100% watertight, manifold geometry without open unmeshed base holes or inverted normals.
   - For rotational objects (cups, glasses, bowls, vases, bottles), ALWAYS construct a continuous lathe profile with uniform realistic wall thickness (e.g. 2-5mm) and a solid base bottom floor.
   - For beverage liquids in containers: liquid geometry MUST start directly on the inner glass floor and hug the inner container wall coordinates exactly (zero air gaps, zero penetration).

3. MODIFIERS & SMOOTH SHADING:
   - Never leave primitive polygonal facets visible. Always call bpy.ops.object.shade_smooth() or apply smooth shading on polygons.
   - Add a Bevel modifier (width: 0.015 - 0.04, segments: 3, limit_method='ANGLE') to catch physical specular edge highlights.
   - Add a Subdivision Surface modifier (levels: 2, render_levels: 2) on organic, curved, and ceramic surfaces.

4. PHOTOREALISTIC PBR MATERIALS:
   - Always construct materials using 'Principled BSDF' ('ShaderNodeBsdfPrincipled'). Never use flat, single-color unshaded diffuse shaders.
   - Glass & Optics: Transmission Weight = 1.0, Roughness = 0.02 - 0.04, IOR = 1.50, Alpha = 0.20, blend_method = 'HASHED' or 'BLEND', with subtle procedural condensation micro-bump (Scale 35.0, Strength 0.035).
   - Milky / Organic Liquids: Subsurface Scattering Weight = 0.35 - 0.45, Radius = (0.2, 0.5, 0.1), Roughness = 0.18.
   - Velvety Cream & Foam: Roughness = 0.85 - 0.90, Specular = 0.15, micro-noise Bump normal (Scale 50.0, Strength 0.25).
   - Ceramics & Pottery: Multi-scale Voronoi micro-iron flecks (Kuro-ten), dual-glaze vertex color blend, and toasted rim gradient.
   - Metals: Metallic = 1.0, Roughness = 0.15 - 0.35, subtle micro-scratch bump.

5. STUDIO 3-POINT LIGHTING:
   - Always illuminate assets using a professional 3-point studio lighting rig:
     - Key Light: Area or Sun light, warm/neutral (energy 100-300W), 45-degree angle.
     - Fill Light: Soft cool tone, lower intensity (energy 30-80W), opposite side.
     - Rim / Back Light: High intensity backlight behind the object to create edge separation and highlights.

6. VIEWPORT THEME PRESERVATION:
   - Maintain space.shading.background_type = 'THEME' (neutral dark-grey background). Never set a blinding 100% white environment background.

7. RECIPE LEVERAGE:
   - Before writing complex code from scratch, ALWAYS check if a relevant verified recipe exists by invoking 'search_recipe_library'. Reusing verified mathematical lathe profiles and PBR shader node configurations guarantees photorealistic results.

8. RE-INVOCATION & SAME-ASSET TRIAGE VALIDATION:
   When an asset or reference image (e.g., 'furui.png') is detected as already generated or discussed previously:
   - NEVER reject, deflect, or assume the file is an accidental duplicate.
   - If the user explicitly asks to regenerate ("generate ulang", "rebuild", "update with new rules"), IMMEDIATELY proceed to recreate the 3D model with maximum 2K PBR quality directives without redundant questions.
   - If the intent is unspecified, present this clear choice:
     "The selected reference image/asset '[name]' was previously generated. Would you like to:
      1. Regenerate / Rebuild Asset: Recreate this 3D model from scratch using the latest 2K PBR production quality rules.
      2. Change / Switch 3D Asset: Pick a new reference image from File Explorer, clipboard, or provide a new text description."
"""

TOOLS = [
    {
        "name": "execute_blender_code",
        "description": "Execute Python (bpy) script directly in the active Blender desktop session to generate or update 3D assets. MUST follow the mandatory 2K PBR quality guidelines: watertight manifold geometry, Bevel (segments 3) and Subsurf modifiers, Principled BSDF with realistic Roughness/Transmission/SSS, 3-point studio lighting, and 2048x2048 resolution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Complete, standalone Blender Python (bpy) code adhering to the mandatory 2K PBR production quality standards."
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
    },
    {
        "name": "search_recipe_library",
        "description": "Search production-verified 3D Blender Python recipes by keyword. Returns matching recipes, or fallback building blocks and universal production guidelines if no direct match exists.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords describing the asset, material, or shape (e.g., 'glass cup', 'ceramic chawan', 'sports car', 'wooden table')."
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter (e.g., 'recipes', 'ceramics', 'beverages', 'vehicles')."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_verified_recipe",
        "description": "Save a verified, high-quality Blender Python script as a reusable recipe file and permanently log it to the continuous learning design archive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_name": {
                    "type": "string",
                    "description": "Name of the 3D asset in snake_case (e.g., 'sci_fi_laser_rifle', 'wooden_dining_chair')."
                },
                "category": {
                    "type": "string",
                    "description": "Category name for organization (e.g., 'weapons', 'furniture', 'food', 'props')."
                },
                "code": {
                    "type": "string",
                    "description": "The complete, verified Blender Python (bpy) script."
                },
                "notes": {
                    "type": "string",
                    "description": "Optional architectural details, shader setup notes, or geometric rules."
                }
            },
            "required": ["asset_name", "category", "code"]
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


def handle_search_recipe_library(arguments):
    query = arguments.get("query", "").strip().lower()
    category_filter = arguments.get("category", "").strip().lower()

    if not query:
        return {"content": [{"type": "text", "text": "Error: 'query' argument is required."}], "isError": True}

    recipes_dir = CURRENT_DIR / "examples" / "recipes"
    examples_dir = CURRENT_DIR / "examples"

    all_py_files = []
    if recipes_dir.exists():
        all_py_files.extend(list(recipes_dir.rglob("*.py")))
    if examples_dir.exists():
        all_py_files.extend([f for f in examples_dir.glob("*.py") if f.is_file()])

    # Stop words to filter out
    stop_words = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "and", "or", "3d", "model", "asset"}
    tokens = [t for t in query.replace("-", " ").replace("_", " ").split() if t not in stop_words]
    if not tokens:
        tokens = [query]

    scored_recipes = []
    for file_path in all_py_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        filename_lower = file_path.name.lower()
        rel_path = file_path.relative_to(CURRENT_DIR)

        if category_filter and category_filter not in str(rel_path).lower():
            continue

        score = 0
        for token in tokens:
            if token in filename_lower:
                score += 6
            # Check first 30 lines (header / docstring)
            header_lines = "".join(content.splitlines()[:35]).lower()
            if token in header_lines:
                score += 3
            if token in content.lower():
                score += 1

        if score > 0:
            scored_recipes.append((score, file_path, rel_path, content))

    scored_recipes.sort(key=lambda x: x[0], reverse=True)

    if scored_recipes:
        output_parts = [f"Found {len(scored_recipes)} matching recipe(s) for query '{query}':\n"]
        # Take top 2 best matches to keep tokens compact
        for score, file_path, rel_path, content in scored_recipes[:2]:
            lines = content.splitlines()
            # Extract header docstring
            docstring_lines = []
            code_excerpt_lines = []
            in_doc = False
            for line in lines[:40]:
                if '"""' in line or "'''" in line:
                    in_doc = not in_doc
                    docstring_lines.append(line)
                elif in_doc or line.startswith("#"):
                    docstring_lines.append(line)

            # Sample key functions or code
            code_excerpt = "\n".join(lines[:80])
            if len(lines) > 80:
                code_excerpt += f"\n# ... [{len(lines) - 80} more lines in {rel_path}]"

            output_parts.append(
                f"--- Recipe: {rel_path} (Relevance Score: {score}) ---\n"
                f"{code_excerpt}\n"
            )
        return {"content": [{"type": "text", "text": "\n".join(output_parts)}], "isError": False}

    # FALLBACK TIER: When no direct recipe exists
    fallback_message = (
        f"No direct recipe found for '{query}'.\n\n"
        "=== FALLBACK LEVEL 1: REUSABLE COMPONENT BLOCKS ===\n"
        "You can borrow verified building blocks from existing recipes:\n"
        "  - Optical glass / liquid volume: see 'examples/recipes/04_iced_latte_glass_lathe.py'\n"
        "  - Ceramics / dual-glaze / spouts: see 'examples/recipes/06_katakuchi_matcha_chawan.py'\n"
        "  - Cast iron / dark metallic: see 'examples/recipes/14_japanese_tetsubin_tea_kettle.py'\n"
        "  - Thin plastic / thermoformed polymers: see 'examples/recipes/05_thermoformed_pet_plastic_cup.py'\n"
        "  - Organic food / seeds / leaves: see Asset Log #01 in 'design.md'\n"
        "  - Hard-surface vehicle / wheels: see 'examples/02_lowpoly_car.py'\n\n"
        "=== FALLBACK LEVEL 2: UNIVERSAL 3D PRODUCTION GUIDELINES ===\n"
        "Follow these mandatory quality standards for novel objects:\n"
        "  1. Topology: 100% watertight manifold mesh. Use BMesh curves or lathe profiles.\n"
        "  2. Modifiers: Always add Bevel (width 0.02 - 0.05, 3 segments) and Subdivision Surface level 2.\n"
        "  3. Shading: Principled BSDF with realistic Roughness (0.15 - 0.65), Specular 0.5. Never leave flat shading.\n"
        "  4. Studio Lighting: 3-point lighting setup (Key, Fill, Rim) with neutral dark-grey viewport.\n"
        "  5. Resolution: Always set 2K rendering (2048 x 2048).\n\n"
        "=== FALLBACK LEVEL 3: SELF-LEARNING ARCHIVE ===\n"
        "Once you successfully generate this novel model and verify it in Blender, call the "
        "'save_verified_recipe' tool to permanently archive it into the recipe library for future recall!"
    )
    return {"content": [{"type": "text", "text": fallback_message}], "isError": False}


def handle_save_verified_recipe(arguments):
    asset_name = arguments.get("asset_name", "").strip().lower()
    category = arguments.get("category", "props").strip().lower()
    code = arguments.get("code", "")
    notes = arguments.get("notes", "").strip()

    if not asset_name or not code:
        return {"content": [{"type": "text", "text": "Error: 'asset_name' and 'code' arguments are required."}], "isError": True}

    # Sanitize names
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in asset_name)
    safe_cat = "".join(c if c.isalnum() or c == "_" else "_" for c in category)

    target_dir = CURRENT_DIR / "examples" / "recipes" / safe_cat
    target_dir.mkdir(parents=True, exist_ok=True)
    recipe_file = target_dir / f"{safe_name}.py"

    import time
    timestamp = time.strftime("%Y-%m-%d")

    header_block = (
        f'"""\n'
        f'Recipe: {safe_name}\n'
        f'Category: {safe_cat}\n'
        f'Date: {timestamp}\n'
        f'Notes: {notes if notes else "Verified production 3D asset script."}\n'
        f'"""\n\n'
    )

    try:
        recipe_file.write_text(header_block + code, encoding="utf-8")
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error writing recipe file: {e}"}], "isError": True}

    # Automatically log to design.md
    if DESIGN_DOC_PATH.exists():
        try:
            design_content = DESIGN_DOC_PATH.read_text(encoding="utf-8")
            log_entry = (
                f"\n\n---\n\n"
                f"## Asset Log: {safe_name.replace('_', ' ').title()}\n\n"
                f"- **Date:** {timestamp}\n"
                f"- **Category:** {safe_cat.title()}\n"
                f"- **Source:** Verified Recipe Library (`examples/recipes/{safe_cat}/{safe_name}.py`)\n"
                f"- **Notes:** {notes if notes else 'Added via MCP self-learning auto-save.'}\n"
            )
            DESIGN_DOC_PATH.write_text(design_content + log_entry, encoding="utf-8")
        except Exception as e:
            pass

    rel_path = recipe_file.relative_to(CURRENT_DIR)
    return {
        "content": [{
            "type": "text",
            "text": (
                f"Successfully saved verified recipe to '{rel_path}' and updated 'design.md'!\n"
                f"The recipe library has expanded and can now be recalled via 'search_recipe_library' "
                f"for any future '{safe_name}' or '{safe_cat}' asset requests."
            )
        }],
        "isError": False
    }


TOOL_HANDLERS = {
    "execute_blender_code": handle_execute_blender_code,
    "get_blender_status": handle_get_blender_status,
    "pick_image_from_dialog": handle_pick_image_from_dialog,
    "get_image_from_clipboard": handle_get_image_from_clipboard,
    "get_design_guidelines": handle_get_design_guidelines,
    "search_recipe_library": handle_search_recipe_library,
    "save_verified_recipe": handle_save_verified_recipe
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
                    },
                    "instructions": SYSTEM_INSTRUCTIONS.strip()
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
