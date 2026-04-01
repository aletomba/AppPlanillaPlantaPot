# Copilot Instructions — LaboratorioAgua (Python Front)

## Estructura de módulos
Cada módulo de dominio tiene: `dto.py`, `service.py`, `view.py`
- `cliente/` — ABM de clientes
- `libro_entrada/` — Libro de entradas de muestras
- `libro_fisico/` — Análisis físico-químico
- `libro_bacteriologia/` — Análisis bacteriológico
- `planilla_diaria/` — Planilla diaria de ensayos
- `data/` — `api_data_acces.py` (cliente HTTP hacia la API)
- `shared/` — Clase base `base_analisis_view.py`, `GenericReport.py`
- `presentation/` — `app.py`, navegación principal Tkinter

## Ejecución
```powershell
cd "C:\Users\tomba\OneDrive\Escritorio\AppPlanillaPlantaPot"
.venv\Scripts\Activate.ps1   # activar entorno virtual
python main.py              # lanzar aplicación
```

## Convenciones
- Antes de implementar código con dependencias externas, consultar **Context7 MCP** para obtener documentación actualizada de la librería (Tkinter, requests, reportlab, etc.).
- UI con **Tkinter + ttk**
- Cada `view.py` hereda de la vista base o implementa patrón similar
- Los `service.py` llaman a `api_data_acces.py` que apunta a `http://localhost:5261`
- Fechas en queries: formato `yyyy-MM-dd`
- Vistas con buscador tienen: `entry_desde`, `entry_hasta`, `_buscar_por_fecha()`, `_limpiar_busqueda()`
- Paginación manejada en cada vista con `_prev_page()` / `_next_page()` y flag `_buscando_por_fecha`

## Carpetas
- **Fuente**: `C:\Users\tomba\OneDrive\Escritorio\AppPlanillaPlantaPot\`
- **Producción**: `C:\Users\tomba\OneDrive\Escritorio\LaboratorioAgua_NEW\`
- El sistema completo se lanza con `LaboratorioAgua_NEW\START.bat`

## Git Flow
Todo el flujo se ejecuta con **GitHub MCP** (`mcp_github_*`). Respetar este orden siempre:
1. Usar **GitHub MCP** para crear rama `feat/nombre-feature` desde `develop`
2. Commit + push de la rama feat (vía terminal/git local)
3. Invocar el agente **Code Reviewer** (`@Code Reviewer revisá los cambios de esta rama antes del PR`) y aplicar las mejoras sugeridas
4. Usar **GitHub MCP** para crear PR `feat` → `develop`, mergearlo y borrar la rama feat
5. Usar **GitHub MCP** para crear PR `develop` → `main` y mergearlo
6. Repos GitHub: `aletomba/AppPlanillaPlantaPot` y `aletomba/ApiLaboratorioAgua`
7. **Al finalizar el flujo completo, siempre hacer `git checkout develop` para dejar el repo posicionado en `develop`.**
8. **Cerrar en GitHub las issues resueltas al terminar cada feature/fix.**

> El token del MCP está configurado en `settings.json` local (nunca en este archivo).

## Deploy Python (copiar a producción)
```powershell
$src = "C:\Users\tomba\OneDrive\Escritorio\AppPlanillaPlantaPot"
$dst = "C:\Users\tomba\OneDrive\Escritorio\LaboratorioAgua_NEW"

xcopy /E /Y "$src\presentation"        "$dst\presentation\"
xcopy /E /Y "$src\cliente"             "$dst\cliente\"
xcopy /E /Y "$src\libro_entrada"       "$dst\libro_entrada\"
xcopy /E /Y "$src\libro_fisico"        "$dst\libro_fisico\"
xcopy /E /Y "$src\libro_bacteriologia" "$dst\libro_bacteriologia\"
xcopy /E /Y "$src\shared"              "$dst\shared\"
xcopy /E /Y "$src\data"                "$dst\data\"
xcopy /E /Y "$src\planilla_diaria"     "$dst\planilla_diaria\"
Copy-Item "$src\main.py" "$dst\main.py" -Force
```
> También se puede correr `Update.bat` desde la carpeta fuente.
