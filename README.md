# Conneskills plugin for Codex

Conecta Codex con cuatro superficies gobernadas de Conneskills:
**Conneskills KBS**, **Conneskills Code**, **Conneskills Memory** y
**Conneskills Planning**. Cada una usa su propio recurso MCP y consentimiento
OAuth.

## Instalación

```bash
codex plugin marketplace add conneskills/codex-plugin
codex plugin add conneskills@conneskills
```

Reinicia o abre una conversación nueva después de instalar. Codex solicitará
autorización cuando conecte cada recurso.

## Recursos incluidos

| Recurso | URL | Uso |
|---|---|---|
| Conneskills KBS | `https://app.conneskills.com/api/mcp/kbs` | KBs y conectores gobernados |
| Conneskills Code | `https://app.conneskills.com/api/mcp/code` | Índice y grafo de código |
| Conneskills Memory | `https://app.conneskills.com/api/mcp/memory` | Memoria e intenciones |
| Conneskills Planning | `https://app.conneskills.com/api/mcp/planning` | Planes y gobernanza |

Los permisos seguros por defecto no incluyen escritura de código, borrado de
memoria ni gestión de ADRs. El plugin fija explícitamente los scopes OAuth
mínimos por recurso para que Codex no solicite el catálogo completo del issuer.

## Uso

- “Busca en nuestras KBs qué dice el procedimiento de compras.”
- “Explica la arquitectura del repositorio indexado y traza esta función.”
- “Recupera la memoria relevante antes de continuar.”
- “Consulta el plan activo y comprueba sus gates de gobernanza.”

Para preguntas sobre datos, la skill de KBS busca primero en la información
indexada. Sólo usa el conector en vivo cuando se necesitan valores actuales o
una consulta estructurada que el índice no puede resolver.

## Desarrollo

El plugin está en `plugins/conneskills` y el catálogo del repositorio en
`.agents/plugins/marketplace.json`. No requiere build.
