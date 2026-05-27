import pandas as pd

from src.domain.constants import ALERT_CRITICAL, ALERT_HIGH, ALERT_MONITORING, ALERT_OPPORTUNITY
from src.services.analysis_service import (
    classify_alert,
    enrich_dataframe,
    get_decision_queue,
    get_executive_kpis,
    suggest_next_action,
)


def test_classify_alert_by_priority_rules():
    assert classify_alert(pd.Series({"riesgo_score": 3, "oportunidad_score": 0, "relevancia": 4})) == ALERT_CRITICAL
    assert classify_alert(pd.Series({"riesgo_score": 2, "oportunidad_score": 0, "relevancia": 3})) == ALERT_HIGH
    assert classify_alert(pd.Series({"riesgo_score": 0, "oportunidad_score": 3, "relevancia": 3})) == ALERT_OPPORTUNITY
    assert classify_alert(pd.Series({"riesgo_score": 1, "oportunidad_score": 1, "relevancia": 1})) == ALERT_MONITORING


def test_enrich_dataframe_adds_scores_priority_alert_and_suggested_action():
    df = pd.DataFrame(
        [
            {
                "fecha": "2026-05-25",
                "pais": "Ecuador",
                "nivel_riesgo": "Crítico",
                "nivel_oportunidad": "Bajo",
                "relevancia": 5,
                "accion_recomendada": "",
                "estado_seguimiento": "Detectado",
            }
        ]
    )

    enriched = enrich_dataframe(df)

    assert enriched.loc[0, "riesgo_score"] == 4
    assert enriched.loc[0, "oportunidad_score"] == 1
    assert enriched.loc[0, "prioridad"] == 14
    assert enriched.loc[0, "clasificacion_alerta"] == ALERT_CRITICAL
    assert "Círculo Operativo" in enriched.loc[0, "accion_sugerida_sistema"]


def test_suggest_next_action_prefers_manual_action():
    row = pd.Series(
        {
            "accion_recomendada": "Validar con dirección institucional",
            "clasificacion_alerta": ALERT_CRITICAL,
            "prioridad": 12,
        }
    )

    assert suggest_next_action(row) == "Validar con dirección institucional"


def test_get_executive_kpis_for_empty_dataframe():
    assert get_executive_kpis(pd.DataFrame()) == {
        "total_registros": 0,
        "alertas_criticas": 0,
        "eventos_alta_prioridad": 0,
        "paises_criticos": 0,
        "promedio_relevancia": 0,
        "insumos_accionables": 0,
        "usados_en_decision": 0,
        "pendientes_de_accion": 0,
    }


def test_get_decision_queue_includes_system_suggested_actions():
    df = pd.DataFrame(
        [
            {
                "fecha": pd.Timestamp("2026-05-25"),
                "pais": "Ecuador",
                "programa": "A",
                "tema": "IA",
                "clasificacion_alerta": ALERT_HIGH,
                "prioridad": 8,
                "relevancia": 3,
                "titulo": "Sin acción manual",
                "decision_impacto": "",
                "accion_recomendada": "",
                "accion_sugerida_sistema": "Preparar insumo ejecutivo",
                "derivacion": "",
                "estado_seguimiento": "Detectado",
            },
            {
                "fecha": pd.Timestamp("2026-05-26"),
                "pais": "Perú",
                "programa": "B",
                "tema": "Gobernanza",
                "clasificacion_alerta": ALERT_CRITICAL,
                "prioridad": 12,
                "relevancia": 5,
                "titulo": "Elevar alerta",
                "decision_impacto": "Priorizar reunión estratégica",
                "accion_recomendada": "Elevar al Círculo Operativo",
                "accion_sugerida_sistema": "Elevar al Círculo Operativo",
                "derivacion": "Círculo Operativo",
                "estado_seguimiento": "Elevado",
            },
        ]
    )

    queue = get_decision_queue(df)

    assert len(queue) == 2
    assert queue.iloc[0]["titulo"] == "Elevar alerta"
