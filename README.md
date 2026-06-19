# Observatorio OIAP

Sistema de inteligencia de datos del Observatorio OIAP/IIAP desarrollado con Python, Streamlit y PostgreSQL para gestionar, analizar y priorizar hallazgos institucionales orientados a la toma de decisiones.

## Características principales

- Carga de información desde CSV o Excel.
- Registro manual de hallazgos.
- Limpieza, normalización y validación de datos.
- Priorización por riesgo, oportunidad y relevancia.
- Dashboard ejecutivo con cola de decisión.
- Persistencia institucional en PostgreSQL.
- Usuarios, roles y auditoría básica de acciones.
- Configuración por entorno mediante `.env` y archivos en `env/`.

## Requisitos

- Python 3.10 o superior
- PostgreSQL instalado y una base creada, por ejemplo `oiap`
- pip o Conda

## Instalación

```powershell
conda activate oiap-streamlit
pip install -r requirements.txt
```

## Configuración por entorno

La raíz del proyecto contiene un archivo `.env` con el entorno activo:

```env
APP_ENV=development
```

El sistema carga después el archivo correspondiente dentro de `env/`:

```text
env/development.env
env/production.env
```

Ejemplo de `env/development.env`:

```env
APP_NAME=Observatorio OIAP
OIAP_DATABASE_URL=postgresql://usuario:password@localhost:5432/oiap
OIAP_EVENT_TABLE=observatorio_eventos
OIAP_USER_TABLE=usuarios
OIAP_DECISION_TABLE=decisiones
OIAP_AUDIT_LOG_TABLE=audit_log
OIAP_USER_SESSION_TABLE=sesiones_usuario
OIAP_SCHEMA_MIGRATIONS_TABLE=schema_migrations
```

Los archivos `.env` y `env/*.env` están excluidos del repositorio porque pueden contener credenciales.

## Ejecución

Con `.env` configurado, basta ejecutar:

```powershell
streamlit run app.py
```

La aplicación crea y actualiza automáticamente las tablas base si la conexión tiene permisos suficientes.

## Tablas principales

Los nombres se configuran desde `env/development.env` o `env/production.env`. Por defecto:

- `usuarios`
- `observatorio_eventos`
- `decisiones`
- `audit_log`
- `sesiones_usuario`
- `schema_migrations`

## Pruebas

Las pruebas usan la configuración activa del entorno.

```powershell
pytest
```

## Estructura general

- `app.py`: punto de entrada de la aplicación.
- `src/ui`: pantallas de Streamlit.
- `src/services`: limpieza, análisis, dashboard y autenticación.
- `src/domain`: reglas institucionales del Observatorio.
- `src/database`: conexión PostgreSQL, esquema, repositorios y auditoría.
- `tests`: pruebas automatizadas.
