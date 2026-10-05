# Changelog

## 2.1.0

### Nuevo: servidor Insights

`conneskills-insights` (`/api/mcp/insights`) expone el radar de señales: lo que
la corrida diaria de la plataforma ya calculó sobre los datos del workspace. Se
añade como el sexto dominio MCP, con paridad de contrato con el plugin de
Claude. Cuatro herramientas de intención, sin tablas ni fechas como argumento:
`insights_brief`, `insights_explain`, `insights_report_outcome` e
`insights_setup`.

- Las señales **certificadas** salen de un playbook firmado y traen la acción
  que recomienda una decisión publicada. Los hallazgos **descubiertos** salen de
  una plantilla de análisis, traen su procedencia y no traen acción.
- La skill indica empezar por `insights_brief` ante cualquier pregunta abierta
  sobre el negocio, y armar tableros solo con esa respuesta.
- `insights_setup` es la sección "Turning the radar on": un owner o admin
  enciende la corrida diaria desde el propio servidor, con la plantilla, la
  conexión y `min_weekly_money`.
- Se solicitan los scopes `insights:read`, `insights:manage` e
  `insights:outcome`. `insights:read` es opt-in desde el Access Group;
  `insights_setup` exige owner o admin. Es un recurso OAuth nuevo, así que hay
  que autorizarlo al instalar.

Requiere una plataforma que sirva `/api/mcp/insights` (ADR-061). Los otros
cinco recursos no cambian.

### Validación

- `scripts/validate.py` exige la skill `conneskills-insights`, la URL, los
  scopes y la paridad skill↔servidor, además de comprobar en la referencia que
  se documentan las cuatro tools y los tres scopes del radar.

## 2.0.0

### Cinco dominios MCP canónicos

- Se añade `conneskills-connectors` para lecturas vivas y
  `conneskills-kbs` pasa a llamarse `conneskills-knowledge`.
- Code, Memory y Planning dejan los aliases `/api/mcp/brain/*`; los cinco
  servidores apuntan a `/api/mcp/{knowledge,connectors,code,memory,planning}`.
- Knowledge solicita solo `kb:query` y Connectors solicita
  `connectors:read`. Esta separación impide que el recurso Knowledge anuncie
  también las tools vivas conservadas por compatibilidad en el backend.

### Esquema de base de datos determinista

- `database_list_schemas`, `database_list_tables` y
  `database_describe_table` pertenecen a Knowledge. Reciben `kb_id`, leen el
  último snapshot indexado y nunca consultan la base de datos viva.
- Las skills documentan tamaños, relaciones, `performance_risk` y warnings
  estables que hay que revisar antes de preparar una lectura viva.
- Connectors conserva únicamente las operaciones DB de conexión,
  `database_count`, `database_select` y `database_aggregate`.

### Skills y validación

- Las cinco skills se refinan para activarse con peticiones reales en inglés y
  español y para explicar los límites de permisos y frescura.
- Los catálogos extensos pasan a referencias cargadas solo cuando hacen falta.
- Se añade validación en CI de frontmatter, manifiesto, URLs, scopes, paridad
  skill-servidor y propiedad de las tools DB.

### Migración desde 1.x

1. Actualiza o reinstala el plugin.
2. Vuelve a autorizar los recursos: las URLs canónicas tienen un token distinto
   para el cliente.
3. Actualiza allowlists que todavía nombren `conneskills-kbs`.

| Antes | Ahora |
|---|---|
| `conneskills-kbs` → `/api/mcp/kbs` | `conneskills-knowledge` → `/api/mcp/knowledge` |
| — | `conneskills-connectors` → `/api/mcp/connectors` |
| `conneskills-code` → `/api/mcp/brain/code` | `conneskills-code` → `/api/mcp/code` |
| `conneskills-memory` → `/api/mcp/brain/memory` | `conneskills-memory` → `/api/mcp/memory` |
| `conneskills-planning` → `/api/mcp/brain/planning` | `conneskills-planning` → `/api/mcp/planning` |

## 1.0.2

- Se fijan scopes OAuth explícitos para los cuatro recursos originales.

## 1.0.1

- Code, Memory y Planning se enrutan por los endpoints `/api/mcp/brain/*`.

## 1.0.0

- Primera versión con KBS, Code, Memory y Planning.
