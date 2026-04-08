"""
PCG Connection helpers for Unreal MCP Server.
Provides tools to connect nodes within PCG graphs.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def connect_pcg_nodes_handler(
    unreal_connection,
    graph_name: str,
    from_node: str,
    from_pin: str,
    to_node: str,
    to_pin: str
) -> Dict[str, Any]:
    """
    Connect two nodes in a PCG graph via their pins.

    Args:
        unreal_connection: The Unreal Engine connection object
        graph_name: Target PCG graph name
        from_node: Source node ID
        from_pin: Output pin name on the source node (usually "output")
        to_node: Target node ID
        to_pin: Input pin name on the target node (usually "input")

    Returns:
        Dictionary with connection result
    """
    try:
        if not unreal_connection:
            return {"success": False, "message": "No Unreal connection provided"}

        if not graph_name or not isinstance(graph_name, str):
            return {"success": False, "message": "graph_name is required and must be a non-empty string"}
        if not from_node or not isinstance(from_node, str):
            return {"success": False, "message": "from_node is required and must be a non-empty string"}
        if not from_pin or not isinstance(from_pin, str):
            return {"success": False, "message": "from_pin is required and must be a non-empty string"}
        if not to_node or not isinstance(to_node, str):
            return {"success": False, "message": "to_node is required and must be a non-empty string"}
        if not to_pin or not isinstance(to_pin, str):
            return {"success": False, "message": "to_pin is required and must be a non-empty string"}

        # Guard against self-connections
        if from_node == to_node:
            return {"success": False, "message": "Cannot connect a node to itself"}

        params = {
            "graph_name": graph_name,
            "from_node": from_node,
            "from_pin": from_pin,
            "to_node": to_node,
            "to_pin": to_pin
        }

        logger.info(
            f"Connecting '{from_node}.{from_pin}' -> '{to_node}.{to_pin}' in graph '{graph_name}'"
        )
        response = unreal_connection.send_command("connect_pcg_nodes", params)
        return response or {"success": False, "message": "No response from Unreal"}

    except Exception as e:
        logger.error(f"connect_pcg_nodes_handler error: {e}")
        return {"success": False, "message": str(e)}
