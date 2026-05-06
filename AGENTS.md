# AGENTS.md — AppPlanillaPlantaPot

## Antes de cada modificación

1. **`@Git Flow start`** — crear issue en GitHub y rama `feat/nombre` desde `develop`
2. **Consultar Context7 MCP** antes de escribir código
   - `context7_resolve-library-id` para resolver librería
   - `context7_query-docs` para consultar docs
3. **Escribir código**
4. **`@Code Reviewer revisá los cambios de esta rama antes del PR`** — aplicar mejoras
5. **`@Git Flow finish`** — commit + push + PRs feat→develop→main + issue cerrada

> Skills: `~/.agents/skills/git-flow/SKILL.md`

## Git Flow

- `@Git Flow start` — al iniciar un feature (crea issue + rama)
- `@Git Flow finish` — cuando el código está listo (PRs + merge + cierre de issue)

Repos: `aletomba/AppPlanillaPlantaPot` · `aletomba/ApiLaboratorioAgua`

## Proyectos

| Proyecto | Ruta | Puerto |
|----------|------|--------|
| API (ASP.NET 8) | `..\..\..\source\repos\ApiLaboratorioAgua\ApiLaboratorioAgua` | 5261 |
| Frontend (Python/Tkinter) | `.` | — |

## Deploy

Usar el skill **`@Deploy`** cuando se decide ir a producción:
- `@Deploy frontend` — corre `Update.bat`
- `@Deploy API` — publica y reinicia el proceso
- `@Deploy ambos` — ambos en orden

> Skill: `~/.agents/skills/deploy/SKILL.md`

## CI

GitHub Actions workflow en `.github/workflows/ci.yml`:
- Corre en cada push/PR a `develop` y `main`
- Steps: `flake8 . --max-line-length=120`

## Convenciones

### Frontend
- Módulos: `dto.py`, `service.py`, `view.py`
- `shared/`: `base_analisis_view.py` (clase base para FisicoQuimico/Bacteriologia), `GenericReport.py`, `logger.py`
- Tkinter + ttk
- Fechas: `yyyy-MM-dd`
- Paginación: `_prev_page()`, `_next_page()`, `_buscando_por_fecha`