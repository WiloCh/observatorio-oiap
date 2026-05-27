# Observatorio OIAP

MVP de observatorio desarrollado con Python y Streamlit para gestionar, cargar, analizar y visualizar datos institucionales.

## Caracteristicas principales

- Carga de informacion desde archivos.
- Registro manual de datos.
- Limpieza y normalizacion de datos.
- Analisis y visualizacion en paneles.
- Persistencia local preparada para evolucionar segun las necesidades del proyecto.

## Requisitos

- Python 3.10 o superior
- pip

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecucion

```powershell
streamlit run app.py
```

## Pruebas

```powershell
pytest
```

## Estructura general

- `app.py`: punto de entrada de la aplicacion.
- `src/`: codigo principal del sistema.
- `tests/`: pruebas automatizadas.
- `data/`: datos locales y archivos generados no versionados.
