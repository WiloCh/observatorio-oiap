import pandas as pd

from src.domain.constants import (
    ALERT_CRITICAL,
    ALERT_HIGH,
    ALERT_MONITORING,
    ALERT_OPPORTUNITY,
    FOLLOW_UP_DISCARDED,
    FOLLOW_UP_USED,
    LEVEL_ORDER,
)

PRIORITY_HIGH_THRESHOLD = 8
PRIORITY_MONITORING_THRESHOLD = 5
RISK_CRITICAL_THRESHOLD = 3
RISK_HIGH_THRESHOLD = 2
RELEVANCE_CRITICAL_THRESHOLD = 4
RELEVANCE_HIGH_THRESHOLD = 3
OPPORTUNITY_HIGH_THRESHOLD = 3


def _text_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series([""] * len(df), index=df.index)
    return df[column].fillna("").astype(str)


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    enriched = df.copy()
    enriched["fecha"] = pd.to_datetime(enriched["fecha"], errors="coerce")
    enriched["riesgo_score"] = enriched["nivel_riesgo"].map(LEVEL_ORDER).fillna(0).astype(int)
    enriched["oportunidad_score"] = (
        enriched["nivel_oportunidad"].map(LEVEL_ORDER).fillna(0).astype(int)
    )
    enriched["relevancia"] = pd.to_numeric(enriched["relevancia"], errors="coerce").fillna(0)

    enriched["prioridad"] = (
        enriched["riesgo_score"] * 2 + enriched["oportunidad_score"] + enriched["relevancia"]
    )

    enriched["clasificacion_alerta"] = enriched.apply(classify_alert, axis=1)
    enriched["accion_sugerida_sistema"] = enriched.apply(suggest_next_action, axis=1)
    return enriched


def classify_alert(row: pd.Series) -> str:
    riesgo = row.get("riesgo_score", 0)
    oportunidad = row.get("oportunidad_score", 0)
    relevancia = row.get("relevancia", 0)

    if riesgo >= RISK_CRITICAL_THRESHOLD and relevancia >= RELEVANCE_CRITICAL_THRESHOLD:
        return ALERT_CRITICAL
    if riesgo >= RISK_HIGH_THRESHOLD and relevancia >= RELEVANCE_HIGH_THRESHOLD:
        return ALERT_HIGH
    if oportunidad >= OPPORTUNITY_HIGH_THRESHOLD and relevancia >= RELEVANCE_HIGH_THRESHOLD:
        return ALERT_OPPORTUNITY
    return ALERT_MONITORING


def suggest_next_action(row: pd.Series) -> str:
    manual_action = str(row.get("accion_recomendada", "") or "").strip()
    if manual_action:
        return manual_action

    alert = row.get("clasificacion_alerta", "")
    prioridad = row.get("prioridad", 0)
    riesgo = row.get("riesgo_score", 0)
    oportunidad = row.get("oportunidad_score", 0)
    estado = str(row.get("estado_seguimiento", "") or "")

    if estado == FOLLOW_UP_USED:
        return "Registrar resultado y mantener evidencia para trazabilidad institucional."
    if alert == ALERT_CRITICAL:
        return "Elevar al Círculo Operativo y definir respuesta institucional inmediata."
    if prioridad >= PRIORITY_HIGH_THRESHOLD and riesgo >= RISK_HIGH_THRESHOLD:
        return "Preparar insumo ejecutivo para validar si corresponde intervención o propuesta."
    if alert == ALERT_OPPORTUNITY or oportunidad >= OPPORTUNITY_HIGH_THRESHOLD:
        return "Derivar a Think Tank o cooperación para evaluar propuesta, alianza o posicionamiento."
    if prioridad >= PRIORITY_MONITORING_THRESHOLD:
        return "Mantener en seguimiento y solicitar evidencia adicional antes de escalar."
    return "Monitorear sin escalar; revisar si aparecen nuevas señales o fuentes."


def get_executive_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_registros": 0,
            "alertas_criticas": 0,
            "eventos_alta_prioridad": 0,
            "paises_criticos": 0,
            "promedio_relevancia": 0,
            "insumos_accionables": 0,
            "usados_en_decision": 0,
            "pendientes_de_accion": 0,
        }

    criticas = df[df["clasificacion_alerta"] == ALERT_CRITICAL]
    alta_prioridad = df[df["prioridad"] >= PRIORITY_HIGH_THRESHOLD]
    paises_criticos = criticas["pais"].nunique()
    insumos_accionables = df[
        _text_series(df, "decision_impacto").str.strip().ne("")
        | _text_series(df, "accion_recomendada").str.strip().ne("")
        | _text_series(df, "accion_sugerida_sistema").str.strip().ne("")
    ]
    usados_en_decision = df[_text_series(df, "estado_seguimiento").eq(FOLLOW_UP_USED)]
    pendientes_de_accion = df[
        (df["prioridad"] >= PRIORITY_HIGH_THRESHOLD)
        & ~_text_series(df, "estado_seguimiento").isin([FOLLOW_UP_USED, FOLLOW_UP_DISCARDED])
    ]

    return {
        "total_registros": len(df),
        "alertas_criticas": len(criticas),
        "eventos_alta_prioridad": len(alta_prioridad),
        "paises_criticos": paises_criticos,
        "promedio_relevancia": round(df["relevancia"].mean(), 2),
        "insumos_accionables": len(insumos_accionables),
        "usados_en_decision": len(usados_en_decision),
        "pendientes_de_accion": len(pendientes_de_accion),
    }


def get_top_risk_countries(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["pais", "riesgo_total"])

    result = (
        df.groupby("pais", dropna=False)["riesgo_score"]
        .sum()
        .reset_index(name="riesgo_total")
        .sort_values("riesgo_total", ascending=False)
        .head(top_n)
    )
    return result


def get_top_themes(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["tema", "total"])

    result = (
        df.groupby("tema", dropna=False)
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
        .head(top_n)
    )
    return result


def get_alert_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["clasificacion_alerta", "total"])

    result = (
        df.groupby("clasificacion_alerta")
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )
    return result


def get_program_risk(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["programa", "riesgo_total"])

    result = (
        df.groupby("programa")["riesgo_score"]
        .sum()
        .reset_index(name="riesgo_total")
        .sort_values("riesgo_total", ascending=False)
    )
    return result


def get_timeline(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["fecha", "total"])

    valid = df.dropna(subset=["fecha"]).copy()
    if valid.empty:
        return pd.DataFrame(columns=["fecha", "total"])

    result = valid.groupby(valid["fecha"].dt.date).size().reset_index(name="total")
    return result


def get_risk_opportunity_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    matrix = pd.crosstab(
        df["nivel_riesgo"].replace("", "Sin dato"),
        df["nivel_oportunidad"].replace("", "Sin dato"),
    )
    return matrix


def get_priority_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    columns = [
        "fecha",
        "pais",
        "programa",
        "tema",
        "nivel_riesgo",
        "nivel_oportunidad",
        "relevancia",
        "prioridad",
        "clasificacion_alerta",
        "titulo",
        "decision_impacto",
        "accion_recomendada",
        "accion_sugerida_sistema",
        "derivacion",
        "estado_seguimiento",
    ]

    table = (
        df[columns]
        .sort_values(["prioridad", "relevancia"], ascending=False)
        .reset_index(drop=True)
    )
    return table


def get_decision_queue(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    columns = [
        "fecha",
        "pais",
        "programa",
        "tema",
        "clasificacion_alerta",
        "prioridad",
        "titulo",
        "decision_impacto",
        "accion_recomendada",
        "accion_sugerida_sistema",
        "derivacion",
        "estado_seguimiento",
    ]
    existing_columns = [column for column in columns if column in df.columns]

    queue = df.copy()
    queue["tiene_orientacion"] = (
        _text_series(queue, "decision_impacto").str.strip().ne("")
        | _text_series(queue, "accion_recomendada").str.strip().ne("")
        | _text_series(queue, "accion_sugerida_sistema").str.strip().ne("")
    )

    return (
        queue[queue["tiene_orientacion"]]
        .sort_values(["prioridad", "relevancia"], ascending=False)
        .head(top_n)[existing_columns]
        .reset_index(drop=True)
    )


def get_key_insights(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "pais_mas_critico": "Sin datos",
            "tema_mas_recurrente": "Sin datos",
            "programa_mayor_riesgo": "Sin datos",
        }

    top_country_df = get_top_risk_countries(df, top_n=1)
    top_theme_df = get_top_themes(df, top_n=1)
    top_program_df = get_program_risk(df).head(1)

    return {
        "pais_mas_critico": (
            top_country_df.iloc[0]["pais"] if not top_country_df.empty else "Sin datos"
        ),
        "tema_mas_recurrente": (
            top_theme_df.iloc[0]["tema"] if not top_theme_df.empty else "Sin datos"
        ),
        "programa_mayor_riesgo": (
            top_program_df.iloc[0]["programa"] if not top_program_df.empty else "Sin datos"
        ),
    }
