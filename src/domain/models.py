from dataclasses import asdict, dataclass
import math

from src.domain.constants import (
    DERIVATION_TARGETS,
    EVENT_COLUMNS,
    FOLLOW_UP_STATUSES,
    LEVELS,
    RELEVANCE_RANGE,
    TEXT_COLUMNS,
)


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value)


def _coerce_int(value: object) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, float) and math.isnan(value):
        return 0
    return int(value)


@dataclass(frozen=True)
class EventRecord:
    fecha: str = ""
    pais: str = ""
    region: str = ""
    programa: str = ""
    tema: str = ""
    tipo_fuente: str = ""
    fuente: str = ""
    titulo: str = ""
    descripcion: str = ""
    nivel_riesgo: str = ""
    nivel_oportunidad: str = ""
    relevancia: int = 0
    decision_impacto: str = ""
    accion_recomendada: str = ""
    derivacion: str = ""
    estado_seguimiento: str = "Detectado"
    observaciones: str = ""

    def validate(self) -> None:
        if not self.titulo.strip():
            raise ValueError("El título es obligatorio.")
        if self.nivel_riesgo not in LEVELS:
            raise ValueError(f"Nivel de riesgo inválido: {self.nivel_riesgo}")
        if self.nivel_oportunidad not in LEVELS:
            raise ValueError(f"Nivel de oportunidad inválido: {self.nivel_oportunidad}")
        if not RELEVANCE_RANGE.minimum <= int(self.relevancia) <= RELEVANCE_RANGE.maximum:
            raise ValueError("La relevancia debe estar entre 0 y 5.")
        if self.derivacion not in DERIVATION_TARGETS:
            raise ValueError(f"Derivación inválida: {self.derivacion}")
        if self.estado_seguimiento not in FOLLOW_UP_STATUSES:
            raise ValueError(f"Estado de seguimiento inválido: {self.estado_seguimiento}")

    def to_row(self) -> tuple:
        self.validate()
        values = asdict(self)
        return tuple(values[column] for column in EVENT_COLUMNS)

    @classmethod
    def from_mapping(cls, data: dict) -> "EventRecord":
        values = {column: data.get(column, "") for column in EVENT_COLUMNS}
        for column in TEXT_COLUMNS:
            values[column] = _coerce_text(values[column])
        values["fecha"] = _coerce_text(values["fecha"])
        values["nivel_riesgo"] = _coerce_text(values["nivel_riesgo"])
        values["nivel_oportunidad"] = _coerce_text(values["nivel_oportunidad"])
        values["estado_seguimiento"] = _coerce_text(values["estado_seguimiento"]) or "Detectado"
        values["relevancia"] = _coerce_int(values.get("relevancia"))
        return cls(**values)
