# AppPlanillaPlantaPot

Aplicación de escritorio **Tkinter/Python** para operar el laboratorio de agua potable de planta potabilizadora. Se conecta a [ApiLaboratorioAgua](https://github.com/aletomba/ApiLaboratorioAgua) para persistir la información.

## Funcionalidades

- Carga de **planilla diaria** (análisis físicoquímicos por punto + ensayo de jarras)
- Gestión del **libro de entradas** (muestras bacteriológicas y físicoquímicas)
- Gestión de **clientes**
- Generación e impresión de **reportes PDF**
- Detección automática del puerto de la API

## Tecnologías

| Tecnología | Versión |
|---|---|
| Python | 3.11 |
| tkinter / ttkthemes | - |
| requests | - |
| ReportLab / QuestPDF (PDF) | - |

## Primeros pasos

### Prerrequisitos

- Python 3.11+
- [ApiLaboratorioAgua](https://github.com/aletomba/ApiLaboratorioAgua) corriendo localmente

### Instalación

```bash
git clone https://github.com/aletomba/AppPlanillaPlantaPot.git
cd AppPlanillaPlantaPot

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
python main.py
```

### Variable de entorno (opcional)

Por defecto la app detecta automáticamente el puerto de la API. Podés forzar una URL:

```bash
set API_BASE_URL=http://localhost:5000/api   # Windows
# export API_BASE_URL=http://localhost:5000/api
```

## Estructura

```
main.py                 ← Punto de entrada
cliente/                ← Módulo gestión de clientes
libro_entrada/          ← Módulo libro de entradas
libro_bacteriologia/    ← Módulo análisis bacteriológico
libro_fisico/           ← Módulo análisis físicoquímico
planilla_diaria/        ← Módulo planilla diaria
data/                   ← Acceso a la API REST
shared/                 ← Utilitarios comunes (logger, reportes)
presentation/           ← Ventana principal y navegación
```

## Licencia

MIT
