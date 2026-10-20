#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_CONFIG="$HOME/.pi/agent/mcp.json"

echo "============================================="
echo "Installing Blender Desktop Bridge MCP Server"
echo "============================================="

chmod +x "$SCRIPT_DIR/mcp_server.py"
chmod +x "$SCRIPT_DIR/skill/scripts/send_to_blender.py"
chmod +x "$SCRIPT_DIR/skill/scripts/pick_image.py"

# Configure in Pi Agent MCP configuration if available
if [ -d "$HOME/.pi/agent" ]; then
    mkdir -p "$HOME/.pi/agent"
    python3 -c "
import json, os
mcp_file = '$MCP_CONFIG'
config = {'mcpServers': {}}
if os.path.exists(mcp_file):
    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
    except Exception:
        pass
if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['blender-bridge'] = {
    'command': 'python3',
    'args': ['$SCRIPT_DIR/mcp_server.py'],
    'exposure': 'direct',
    'description': 'Blender Desktop Bridge MCP server for controlling Blender and generating 3D assets'
}

with open(mcp_file, 'w') as f:
    json.dump(config, f, indent=2)
print('[OK] Registered blender-bridge in ' + mcp_file)
"
fi

echo "============================================="
echo "Installation complete."
echo "1. Start Blender Desktop"
echo "2. Open blender_addon/blender_bridge.py in Blender's Scripting workspace and click Run Script"
echo "3. Use with any MCP client (Pi Agent, Claude Desktop, Cursor, Antigravity IDE)"
echo "============================================="
