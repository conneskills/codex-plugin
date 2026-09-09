#!/usr/bin/env python3
"""Validate the Codex marketplace package and its Conneskills contract."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "conneskills"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
errors: list[str] = []

EXPECTED_VERSION = "2.0.0"
EXPECTED_SERVERS = {
    "conneskills-knowledge": {
        "url": "https://app.conneskills.com/api/mcp/knowledge",
        "scopes": ["kb:query"],
    },
    "conneskills-connectors": {
        "url": "https://app.conneskills.com/api/mcp/connectors",
        "scopes": ["connectors:read"],
    },
    "conneskills-code": {
        "url": "https://app.conneskills.com/api/mcp/code",
        "scopes": ["code:read", "code:index", "code:episodes"],
    },
    "conneskills-memory": {
        "url": "https://app.conneskills.com/api/mcp/memory",
        "scopes": [
            "memory:read",
            "memory:write",
            "memory:consolidate",
            "memory:intentions",
        ],
    },
    "conneskills-planning": {
        "url": "https://app.conneskills.com/api/mcp/planning",
        "scopes": ["planning:read", "planning:write", "planning:governance"],
    },
}
INDEXED_DATABASE_SCHEMA_TOOLS = {
    "database_list_schemas",
    "database_list_tables",
    "database_describe_table",
}
LIVE_DATABASE_TOOLS = {
    "database_list_connections",
    "database_count",
    "database_select",
    "database_aggregate",
}


def fail(message: str) -> None:
    errors.append(message)


def read_required_text(path: Path, label: str) -> str:
    try:
        return path.read_text()
    except Exception as exc:  # noqa: BLE001
        fail(f"{label}: cannot read — {exc}")
        return ""


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text())
        if not isinstance(value, dict):
            fail(f"{label}: root must be an object")
            return {}
        return value
    except Exception as exc:  # noqa: BLE001
        fail(f"{label}: invalid JSON — {exc}")
        return {}


def load_yaml(text: str, label: str):
    try:
        import yaml
    except ImportError:
        for line in text.splitlines():
            key, _, value = line.partition(": ")
            if key and not key.startswith(" ") and ": " in value:
                fail(f"{label}: `{key}` contains ': ' in an unquoted YAML scalar")
        return None
    try:
        return yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001
        fail(f"{label}: invalid YAML — {str(exc).splitlines()[0]}")
        return None


manifest = load_json(
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    "plugins/conneskills/.codex-plugin/plugin.json",
)
mcp = load_json(PLUGIN_ROOT / ".mcp.json", "plugins/conneskills/.mcp.json")
marketplace = load_json(
    ROOT / ".agents" / "plugins" / "marketplace.json",
    ".agents/plugins/marketplace.json",
)

if manifest.get("name") != "conneskills":
    fail(f"plugin name must be 'conneskills', got {manifest.get('name')!r}")
if manifest.get("version") != EXPECTED_VERSION:
    fail(f"plugin version must be {EXPECTED_VERSION}, got {manifest.get('version')!r}")
if manifest.get("skills") != "./skills/":
    fail("plugin skills path must be './skills/'")
if manifest.get("mcpServers") != "./.mcp.json":
    fail("plugin mcpServers path must be './.mcp.json'")

entries = marketplace.get("plugins", [])
matching_entries = [entry for entry in entries if entry.get("name") == "conneskills"]
if len(matching_entries) != 1:
    fail("marketplace must contain exactly one conneskills entry")
else:
    entry = matching_entries[0]
    if entry.get("source", {}).get("path") != "./plugins/conneskills":
        fail("marketplace conneskills source path must be './plugins/conneskills'")
    if entry.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        fail("marketplace conneskills policy must be AVAILABLE + ON_INSTALL")

server_configs = mcp.get("mcpServers", {})
if set(server_configs) != set(EXPECTED_SERVERS):
    fail(
        "MCP server set differs from the five-domain contract — "
        f"expected={sorted(EXPECTED_SERVERS)}, actual={sorted(server_configs)}"
    )

for name, expected in EXPECTED_SERVERS.items():
    config = server_configs.get(name, {})
    if config.get("type") != "http":
        fail(f"{name}: type must be 'http'")
    if config.get("url") != expected["url"]:
        fail(f"{name}: expected URL {expected['url']}, got {config.get('url')!r}")
    if config.get("scopes") != expected["scopes"]:
        fail(f"{name}: expected scopes {expected['scopes']!r}, got {config.get('scopes')!r}")

skills_root = PLUGIN_ROOT / "skills"
skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
if {path.name for path in skill_dirs} != set(EXPECTED_SERVERS):
    fail(
        "skill directories differ from MCP servers — "
        f"skills={sorted(path.name for path in skill_dirs)}"
    )

for directory in skill_dirs:
    skill_rel = f"plugins/conneskills/skills/{directory.name}/SKILL.md"
    skill_text = read_required_text(directory / "SKILL.md", skill_rel)
    match = FRONTMATTER.match(skill_text)
    if not match:
        fail(f"{skill_rel}: missing frontmatter")
        continue
    frontmatter = load_yaml(match.group(1), skill_rel)
    if frontmatter is not None:
        if frontmatter.get("name") != directory.name:
            fail(f"{skill_rel}: name must match directory {directory.name!r}")
        if not frontmatter.get("description"):
            fail(f"{skill_rel}: missing discovery description")

    agent_rel = f"plugins/conneskills/skills/{directory.name}/agents/openai.yaml"
    agent_text = read_required_text(directory / "agents" / "openai.yaml", agent_rel)
    agent = load_yaml(agent_text, agent_rel)
    if agent is None:
        continue
    prompt = agent.get("interface", {}).get("default_prompt", "")
    if f"${directory.name}" not in prompt:
        fail(f"{agent_rel}: default_prompt must mention ${directory.name}")
    dependencies = agent.get("dependencies", {}).get("tools", [])
    if len(dependencies) != 1:
        fail(f"{agent_rel}: expected exactly one MCP dependency")
        continue
    dependency = dependencies[0]
    expected = EXPECTED_SERVERS[directory.name]
    if dependency.get("type") != "mcp":
        fail(f"{agent_rel}: dependency type must be 'mcp'")
    if dependency.get("value") != directory.name:
        fail(f"{agent_rel}: dependency value must be {directory.name!r}")
    if dependency.get("transport") != "streamable_http":
        fail(f"{agent_rel}: transport must be 'streamable_http'")
    if dependency.get("url") != expected["url"]:
        fail(f"{agent_rel}: dependency URL differs from .mcp.json")

knowledge_reference = read_required_text(
    skills_root / "conneskills-knowledge" / "references" / "database-schema.md",
    "Knowledge database schema reference",
)
connectors_reference = read_required_text(
    skills_root / "conneskills-connectors" / "references" / "tool-families.md",
    "Connectors tool family reference",
)

for tool in sorted(INDEXED_DATABASE_SCHEMA_TOOLS):
    if f"| `{tool}` |" not in knowledge_reference:
        fail(f"Knowledge inventory is missing indexed schema tool {tool}")
    if f"| `{tool}` |" in connectors_reference:
        fail(f"Connectors incorrectly claims indexed schema tool {tool}")

for tool in sorted(LIVE_DATABASE_TOOLS):
    if f"| `{tool}` |" not in connectors_reference:
        fail(f"Connectors inventory is missing live database tool {tool}")

changelog = read_required_text(ROOT / "CHANGELOG.md", "CHANGELOG.md")
if f"## {manifest.get('version')}" not in changelog:
    fail(f"CHANGELOG.md has no entry for version {manifest.get('version')}")

if errors:
    print("\n".join(f"✗ {error}" for error in errors))
    sys.exit(1)

print(
    f"✓ {len(skill_dirs)} skills, {len(server_configs)} MCP servers, "
    f"Codex plugin {manifest.get('version')}"
)
