"""
Cursor MCP (stdio JSON-RPC) bridge to UnrealMCP TCP server.

Exposes one MCP tool per Unreal command string routed in EpicUnrealMCPBridge.cpp
so Cursor shows the full tool set (not a single generic forwarder).
"""

import json
import os
import socket
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


# Commands accepted by UEpicUnrealMCPBridge::ExecuteCommand (UE 5.6 plugin in this repo).
# Keep in sync with Plugins/UnrealMCP/Source/UnrealMCP/Private/EpicUnrealMCPBridge.cpp
_UNREAL_COMMAND_SPECS: List[Tuple[str, str]] = [
    ("ping", "Health check; returns pong."),
    ("get_actors_in_level", "List all actors in the current editor level."),
    ("find_actors_by_name", "Find actors whose name contains a pattern. Params: pattern."),
    ("spawn_actor", "Spawn a built-in actor type. Params: type, name, optional location/rotation/scale/static_mesh."),
    ("delete_actor", "Delete an actor by name. Params: name."),
    ("set_actor_transform", "Set location/rotation/scale for an actor. Params: name, optional location/rotation/scale."),
    ("spawn_blueprint_actor", "Spawn an instance of a Blueprint. Params: blueprint_name, actor_name, optional location/rotation."),
    ("create_blueprint", "Create a new Blueprint asset. Params: name, optional parent_class."),
    ("add_component_to_blueprint", "Add a component to a Blueprint SCS. Params: blueprint_name, component_type, component_name, ..."),
    ("set_physics_properties", "Set physics on a Blueprint component. Params: blueprint_name, component_name, ..."),
    ("compile_blueprint", "Compile a Blueprint. Params: blueprint_name."),
    ("set_static_mesh_properties", "Set mesh/material on a static mesh component in a Blueprint. Params: blueprint_name, component_name, ..."),
    ("set_mesh_material_color", "Set material color via MID. Params: blueprint_name, component_name, color [R,G,B,A], ..."),
    ("get_available_materials", "Search/list materials. Params: optional search_path, include_engine_materials."),
    ("apply_material_to_actor", "Apply material to actor mesh. Params: actor_name, material_path, optional material_slot."),
    ("apply_material_to_blueprint", "Apply material to Blueprint component. Params: blueprint_name, component_name, material_path, ..."),
    ("get_actor_material_info", "List material slots on an actor. Params: actor_name."),
    ("get_blueprint_material_info", "List material slots on a Blueprint component. Params: blueprint_name, component_name."),
    ("read_blueprint_content", "Read Blueprint structure. Params: blueprint_path, optional include_* flags."),
    ("analyze_blueprint_graph", "Analyze a Blueprint graph. Params: blueprint_path, optional graph_name, include_* flags."),
    ("get_blueprint_variable_details", "Inspect Blueprint variables. Params: blueprint_path, optional variable_name."),
    ("get_blueprint_function_details", "Inspect Blueprint functions. Params: blueprint_path, optional function_name, include_graph."),
    ("add_blueprint_node", "Add a K2 node. Params: blueprint_name, node_type, ..."),
    ("connect_nodes", "Connect two pins. Params: blueprint_name, source_node_id, source_pin_name, target_node_id, target_pin_name."),
    ("create_variable", "Create a Blueprint variable. Params: blueprint_name, variable_name, variable_type, ..."),
    ("set_blueprint_variable_properties", "Edit Blueprint variable metadata. Params: blueprint_name, variable_name, ..."),
    ("add_event_node", "Add an event node. Params: blueprint_name, event_name, ..."),
    ("delete_node", "Delete a graph node. Params: blueprint_name, node_id."),
    ("set_node_property", "Set node property (or semantic action). Params: blueprint_name, node_id, property_name or action, ..."),
    ("create_function", "Create a Blueprint function graph. Params: blueprint_name, function_name."),
    ("add_function_input", "Add input pin to function. Params: blueprint_name, function_name, param_name, ..."),
    ("add_function_output", "Add output pin to function. Params: blueprint_name, function_name, param_name, ..."),
    ("delete_function", "Delete a function. Params: blueprint_name, function_name."),
    ("rename_function", "Rename a function. Params: blueprint_name, old_function_name, new_function_name."),
]

_LEGACY_TOOL = "unreal_command"


def _command_names() -> Set[str]:
    return {name for name, _ in _UNREAL_COMMAND_SPECS}


def _build_tools_list() -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    schema_params_only = {
        "type": "object",
        "properties": {
            "params": {
                "type": "object",
                "description": (
                    "Payload forwarded to Unreal as JSON `params` for this command "
                    "(see Plugins/UnrealMCP and README)."
                ),
                "default": {},
            }
        },
        "additionalProperties": False,
    }
    for cmd, desc in _UNREAL_COMMAND_SPECS:
        tools.append(
            {
                "name": cmd,
                "description": f"[UnrealMCP] {desc}",
                "inputSchema": schema_params_only,
            }
        )
    # Backward compatibility: single generic tool
    tools.append(
        {
            "name": _LEGACY_TOOL,
            "description": "Legacy: send any UnrealMCP command by name. Prefer the specific tools above.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "UnrealMCP command name.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Command parameters.",
                        "default": {},
                    },
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        }
    )
    return tools


TOOLS = _build_tools_list()
_VALID_NAMES = _command_names() | {_LEGACY_TOOL}


def _read_json_line() -> Optional[Dict[str, Any]]:
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return {}
    return json.loads(line)


def _write(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _rpc_result(msg_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _rpc_error(msg_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": msg_id, "error": err}


def _unreal_host_port() -> Tuple[str, int]:
    host = os.environ.get("UNREAL_MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("UNREAL_MCP_PORT", "55557"))
    return host, port


def _send_unreal_command(command: str, params: Dict[str, Any]) -> str:
    host, port = _unreal_host_port()
    payload = json.dumps({"command": command, "params": params}, ensure_ascii=False) + "\n"
    with socket.create_connection((host, port), timeout=5) as s:
        s.sendall(payload.encode("utf-8"))
        s.settimeout(120)
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
        line = buf.split(b"\n", 1)[0]
        try:
            return line.decode("utf-8", errors="replace")
        except Exception:
            return repr(line)


def _call_tool(name: str, arguments: Dict[str, Any]) -> str:
    if name == _LEGACY_TOOL:
        command = arguments.get("command")
        if not isinstance(command, str) or not command:
            raise ValueError("Missing/invalid 'command'")
        cmd_params = arguments.get("params") or {}
        if not isinstance(cmd_params, dict):
            raise ValueError("'params' must be an object")
        return _send_unreal_command(command, cmd_params)

    if name not in _command_names():
        raise ValueError(f"Unknown tool: {name}")

    cmd_params = arguments.get("params") if isinstance(arguments, dict) else None
    if cmd_params is None:
        cmd_params = {}
    if not isinstance(cmd_params, dict):
        raise ValueError("'params' must be an object")
    return _send_unreal_command(name, cmd_params)


def main() -> int:
    while True:
        msg = _read_json_line()
        if msg is None:
            return 0
        if not msg:
            continue

        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") or {}

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                    "serverInfo": {
                        "name": "unreal-mcp-bridge",
                        "version": "0.2.0",
                    },
                    "capabilities": {"tools": {}},
                }
                _write(_rpc_result(msg_id, result))
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                _write(_rpc_result(msg_id, {"tools": TOOLS}))
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments") or {}
                if not isinstance(name, str) or name not in _VALID_NAMES:
                    _write(_rpc_error(msg_id, -32601, f"Unknown tool: {name}"))
                    continue
                response_text = _call_tool(name, arguments if isinstance(arguments, dict) else {})
                _write(
                    _rpc_result(
                        msg_id,
                        {
                            "content": [
                                {"type": "text", "text": response_text},
                            ],
                        },
                    )
                )
            else:
                _write(_rpc_error(msg_id, -32601, f"Method not found: {method}"))
        except (ConnectionError, OSError, socket.timeout) as e:
            _write(
                _rpc_error(
                    msg_id,
                    -32002,
                    "Failed to reach UnrealMCP server. Is Unreal Editor running and UnrealMCP enabled?",
                    {"error": str(e)},
                )
            )
        except ValueError as e:
            _write(_rpc_error(msg_id, -32602, str(e)))
        except Exception as e:
            _write(_rpc_error(msg_id, -32000, "Unhandled server error", {"error": str(e)}))


if __name__ == "__main__":
    raise SystemExit(main())
