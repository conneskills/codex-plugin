# Conneskills — plugin para Codex

Conecta Codex con cinco superficies gobernadas de Conneskills: **Knowledge**,
**Connectors**, **Code**, **Memory** y **Planning**. Cada una usa un recurso MCP
independiente y scopes OAuth explícitos, así que el agente no necesita mezclar
recuperación indexada con consultas a sistemas vivos.

## Instalación

```bash
codex plugin marketplace add conneskills/codex-plugin
codex plugin add conneskills@conneskills
```

Reinicia Codex o abre una conversación nueva después de instalar. Autoriza cada
recurso cuando Codex lo solicite.

## Recursos incluidos

| Servidor | URL | Scope solicitado | Para qué |
|---|---|---|---|
| `conneskills-knowledge` | `https://app.conneskills.com/api/mcp/knowledge` | `kb:query` | Conocimiento indexado y esquema DB determinista, con citas |
| `conneskills-connectors` | `https://app.conneskills.com/api/mcp/connectors` | `connectors:read` | Valores vivos de las conexiones autorizadas |
| `conneskills-code` | `https://app.conneskills.com/api/mcp/code` | `code:read`, `code:index`, `code:episodes` | Grafo de código, impacto e indexación |
| `conneskills-memory` | `https://app.conneskills.com/api/mcp/memory` | memoria e intenciones | Contexto duradero gobernado |
| `conneskills-planning` | `https://app.conneskills.com/api/mcp/planning` | planificación y gobernanza | Planes, evidencia y gates |

Los permisos opcionales de escritura de código, borrado o promoción de memoria
y gestión de ADRs no se solicitan. La disponibilidad final de cada tool también
depende del Access Group del workspace.

## Knowledge o Connectors

- **Knowledge** responde qué sabemos y cómo está estructurada una base de datos
  indexada. `database_list_schemas`, `database_list_tables` y
  `database_describe_table` leen exclusivamente el último snapshot; devuelven
  columnas, claves, relaciones, índices, tamaños, riesgo y warnings sin abrir
  una conexión viva.
- **Connectors** responde cuál es el valor actual. Para bases de datos expone
  discovery, count, select y aggregate. Cada llamada llega a la fuente, añade
  carga y consume presupuesto del workspace.

El orden recomendado es Knowledge para resolver estructura y riesgos, y
Connectors solo cuando la respuesta exige filas o agregados actuales. Los scopes
separados hacen que Knowledge no anuncie herramientas vivas por accidente.

## Compatibilidad con 1.x

La 2.0 renombra `conneskills-kbs` a `conneskills-knowledge`, añade
`conneskills-connectors` y usa las cinco URIs canónicas. Las instalaciones 1.x
siguen funcionando con aliases deprecados hasta el **2027-08-20**, pero al
actualizar hay que volver a autorizar porque el cliente asocia el token con la
URL del recurso. Consulta [CHANGELOG.md](CHANGELOG.md) para el mapa completo.

## Desarrollo

El plugin está en `plugins/conneskills` y el catálogo del repositorio en
`.agents/plugins/marketplace.json`. No requiere build. Antes de publicar:

```bash
python3 scripts/validate.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/conneskills
```
