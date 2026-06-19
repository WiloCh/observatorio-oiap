from dataclasses import dataclass

EVENT_COLUMNS = [
    "fecha",
    "pais",
    "region",
    "programa",
    "tema",
    "tipo_fuente",
    "fuente",
    "titulo",
    "descripcion",
    "nivel_riesgo",
    "nivel_oportunidad",
    "relevancia",
    "decision_impacto",
    "accion_recomendada",
    "derivacion",
    "estado_seguimiento",
    "observaciones",
]

EVENT_READ_COLUMNS = ["id", *EVENT_COLUMNS, "created_at"]

TEXT_COLUMNS = [
    "pais",
    "region",
    "programa",
    "tema",
    "tipo_fuente",
    "fuente",
    "titulo",
    "descripcion",
    "decision_impacto",
    "accion_recomendada",
    "derivacion",
    "estado_seguimiento",
    "observaciones",
]

DEDUPLICATION_COLUMNS = ["fecha", "pais", "tema", "titulo"]

LEVELS = ["", "Bajo", "Medio", "Alto", "Crítico"]
LEVEL_ORDER = {
    "": 0,
    "Bajo": 1,
    "Medio": 2,
    "Alto": 3,
    "Crítico": 4,
}

ALERT_CRITICAL = "Crítica"
ALERT_HIGH = "Alta"
ALERT_OPPORTUNITY = "Oportunidad"
ALERT_MONITORING = "Monitoreo"

PROGRAMS = [
    "Monitoreo de Escenarios Internacionales",
    "Blockchain, Smart Cities y Tecnologías Emergentes",
    "Cooperación Sur-Sur y Triangular",
    "Análisis Comparado de Políticas Públicas",
    "Observación Territorial y Comités País",
]

SOURCE_TYPES = ["Reporte", "Noticia", "Documento institucional", "Base de datos", "Otro"]

DERIVATION_TARGETS = [
    "",
    "Think Tank",
    "Círculo Operativo",
    "Conversión y alianzas",
    "Cooperación institucional",
    "Monitoreo continuo",
]

FOLLOW_UP_DETECTED = "Detectado"
FOLLOW_UP_IN_ANALYSIS = "En análisis"
FOLLOW_UP_ESCALATED = "Elevado"
FOLLOW_UP_USED = "Usado en decisión"
FOLLOW_UP_DISCARDED = "Descartado"

FOLLOW_UP_STATUSES = [
    FOLLOW_UP_DETECTED,
    FOLLOW_UP_IN_ANALYSIS,
    FOLLOW_UP_ESCALATED,
    FOLLOW_UP_USED,
    FOLLOW_UP_DISCARDED,
]

USER_ROLES = ["admin", "direccion", "analista", "consulta"]

OBSERVATORY_DECISION_QUESTION = "¿A qué decisión concreta alimenta esto?"


@dataclass(frozen=True)
class ScoreRange:
    minimum: int = 0
    maximum: int = 5


RELEVANCE_RANGE = ScoreRange()
