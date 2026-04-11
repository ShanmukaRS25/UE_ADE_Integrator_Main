# Unreal_MCP_Plugin

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/fc22d707-555c-41f2-a3c3-3a2de386d272" />

> **Model Context Protocol (MCP) implementation for Unreal Engine 5.5.**
> *Bridge the gap between AI Coding agents and the Unreal Editor.*

## 📖 Table of Contents

- [Introduction](#-introduction)
- [Key Features](#-key-features)
- [Architecture & MCP Integration](#-architecture--mcp-integration)
- [Getting Started](#-getting-started)
- [MCP Tools & Commands](#-mcp-tools--commands)
  - [Editor & Level Commands](#-editor--level-commands)
  - [Blueprint Asset Commands](#-blueprint-asset-commands)
  - [Blueprint Graph Commands](#-blueprint-graph-commands)
  - [PCG Functions](#-pcg-functions)
- [Contributing](#-contributing)

---

## 🚀 Introduction

**UnrealMCP** is an open-source plugin that integrates the **Model Context Protocol (MCP)** into Unreal Engine 5.5. It functions as a bridge, allowing external AI agents (like Claude, ChatGPT, or custom LLMs) to interact directly with the Unreal Editor.

This project enables AI to:

- **Inspect and Query** the current level and assets.
- **Manipulate Actors** (Spawn, Move, Delete).
- **Generate and Modify Blueprints** programmatically.
- **Edit Blueprint Graphs** by adding nodes, connections, and variables.
- **Create Procedural Content** using PCG graph generation and execution.

By standardizing the communication protocol, UnrealMCP opens the door for advanced AI-assisted game development workflows, automated testing, and intelligent editor tools.

---

## ✨ Key Features

- **TCP Socket Server**: Robust, non-blocking server running within the Unreal Editor to handle MCP requests.
- **Extensible Command System**: Modular architecture allowing easy addition of new commands.
- **Direct Editor Manipulation**:
  - Spawn and control actors.
  - Query level data and object properties.
- **Blueprint Automation**:
  - Create new Blueprint assets.
  - Add components and variables.
  - Compile Blueprints remotely.
- **Graph Editing**:
  - Add nodes, events, and function calls to Blueprint graphs.
  - Connect pins and structure logic flows.
- **Procedural Content Generation (PCG)**:
  - Create PCG graphs and volumes programmatically.
  - Configure nodes, spawners, and random variations.
  - Execute PCG generation and analyze results.

---

## 🏗 Architecture & MCP Integration

UnrealMCP works by running a **TCP Server** inside the Unreal Editor via `UEpicUnrealMCPBridge`, which is an `UEditorSubsystem`. This ensures the server starts automatically when the editor launches and runs on the main game thread (via `AsyncTask` for thread safety) to interact with the Unreal API.

### How it works:

1. **Server Start**: `UEpicUnrealMCPBridge` initializes a TCP listener on port **55557** (default).
2. **Connection**: An external MCP client connects to `localhost:55557`.
3. **Command Handling**: JSON-formatted commands are received and routed to specific handlers:
   - `FEpicUnrealMCPEditorCommands`: Handles level and actor operations.
   - `FEpicUnrealMCPBlueprintCommands`: Handles Blueprint asset creation and modification.
   - `FEpicUnrealMCPBlueprintGraphCommands`: Handles low-level graph editing (nodes, pins).
   - `FEpicUnrealMCPPCGCommands`: Handles PCG graph generation and execution.
4. **Execution**: Commands are executed on the Game Thread to ensure thread safety with Unreal's garbage collection and object management.
5. **Response**: The result (or error) is sent back to the client as a JSON response.

---

## 🏁 Getting Started

### Prerequisites

- **Unreal Engine 5.5** or later.
- **Visual Studio 2022** (for C++ compilation).
- **Git** (optional, for cloning).
- **PCG Framework Plugin** (enable in Unreal Editor: Edit → Plugins → Search "PCG" → Enable)

---

## 🛠 MCP Tools & Commands

UnrealMCP exposes a wide range of tools to external agents. Commands are sent as JSON objects with a `command` field and a `parameters` object.

### 🏠 Editor & Level Commands

| Command | Description |
| :--- | :--- |
| `get_actors_in_level` | List all actors in the current level. |
| `find_actors_by_name` | Find specific actors by their name or label. |
| `spawn_actor` | Spawn a standard actor (e.g., StaticMesh, Light). |
| `delete_actor` | Remove an actor from the level. |
| `set_actor_transform` | Move, rotate, or scale an actor. |
| `spawn_blueprint_actor` | Spawn an instance of a Blueprint asset. |

### 📘 Blueprint Asset Commands

| Command | Description |
| :--- | :--- |
| `create_blueprint` | Create a new Blueprint asset. |
| `add_component_to_blueprint` | Add a component (Mesh, Light, etc.) to a BP. |
| `compile_blueprint` | Compile a Blueprint to apply changes. |
| `set_physics_properties` | Modify physics settings of a component. |
| `set_static_mesh_properties` | Set the mesh asset for a StaticMeshComponent. |
| `get_blueprint_variable_details` | Inspect variables within a Blueprint. |
| `analyze_blueprint_graph` | Analyze the structure of a Blueprint graph. |

### 🕸 Blueprint Graph Commands

| Command | Description |
| :--- | :--- |
| `add_blueprint_node` | Add a generic node to the graph. |
| `connect_nodes` | Connect two pins together. |
| `create_variable` | Create a new variable in the Blueprint. |
| `add_event_node` | Add an event node (e.g., BeginPlay). |
| `create_function` | Create a new function within the Blueprint. |
| `set_node_property` | Modify properties of a graph node. |

### 🌲 PCG Functions

| Command | Description |
| :--- | :--- |
| `create_pcg_graph` | Creates a new PCG graph asset for procedural generation. |
| `create_pcg_volume` | Defines a 3D volume area where PCG generation will occur. |
| `add_pcg_node` | Adds a node (sampler, spawner, filter) to an existing PCG graph. |
| `set_pcg_node_property` | Configures properties of a PCG node (density, scale, rotation). |
| `set_spawner_assets` | Assigns static meshes or Blueprint assets to a spawner node. |
| `assign_pcg_graph_to_volume` | Links a PCG graph to a volume for execution. |
| `connect_pcg_nodes` | Connects output pins to input pins between PCG graph nodes. |
| `create_random_variation` | Adds random scale and rotation variation to spawned objects. |
| `execute_pcg` | Runs the PCG generation within the specified volume. |
| `get_pcg_execution_log` | Retrieves generation logs for debugging and performance analysis. |
| `analyze_pcg_output` | Returns statistics about generated objects (count, density, variety). |
| `screenshot_pcg_result` | Captures a screenshot of the generated PCG output in the editor. |

---

## 🤝 Contributing

**This project is currently in active development:** We are looking for co-developers to help expand the capabilities of Unreal Plugin!

### How to Contribute

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with Unreal Engine 5.5+
- Powered by the Model Context Protocol (MCP)
- Community contributors and testers
