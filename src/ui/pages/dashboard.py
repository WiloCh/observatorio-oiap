import pandas as pd
import streamlit as st

from src.database.repository import get_all_data
from src.domain.constants import (
    ALERT_CRITICAL,
    ALERT_HIGH,
    ALERT_OPPORTUNITY,
    OBSERVATORY_DECISION_QUESTION,
)
from src.services.analysis_service import (
    enrich_dataframe,
    get_alert_distribution,
    get_decision_queue,
    get_executive_kpis,
    get_key_insights,
    get_priority_table,
    get_program_risk,
    get_risk_opportunity_matrix,
    get_timeline,
    get_top_risk_countries,
    get_top_themes,
)
from src.services.dashboard_service import (
    ALL_FILTER_LABEL,
    CUSTOM_FILTER_LABEL,
    apply_dashboard_filters,
    get_date_bounds,
    get_filter_options,
    has_custom_filter,
)


def color_alert(value: str) -> str:
    if value == ALERT_CRITICAL:
        return "background-color: #7f1d1d; color: white;"
    if value == ALERT_HIGH:
        return "background-color: #b45309; color: white;"
    if value == ALERT_OPPORTUNITY:
        return "background-color: #166534; color: white;"
    return "background-color: #374151; color: white;"


def color_risk(value: str) -> str:
    if value == "Crítico":
        return "background-color: #991b1b; color: white;"
    if value == "Alto":
        return "background-color: #dc2626; color: white;"
    if value == "Medio":
        return "background-color: #d97706; color: white;"
    if value == "Bajo":
        return "background-color: #15803d; color: white;"
    return ""


def render_filter_control(label: str, options: list[str], key: str) -> list[str]:
    mode = st.radio(
        label,
        [ALL_FILTER_LABEL, CUSTOM_FILTER_LABEL],
        horizontal=True,
        key=f"{key}_mode",
    )

    if mode == ALL_FILTER_LABEL:
        st.caption(f"{len(options)} opciones incluidas")
        return options

    return st.multiselect(
        f"Elegir {label.lower()}",
        options,
        default=options,
        key=f"{key}_values",
        placeholder="Selecciona una o varias opciones",
    )


def render_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    paises = get_filter_options(df, "pais")
    programas = get_filter_options(df, "programa")
    temas = get_filter_options(df, "tema")
    alertas = get_filter_options(df, "clasificacion_alerta")
    derivaciones = get_filter_options(df, "derivacion")
    estados = get_filter_options(df, "estado_seguimiento")
    date_bounds = get_date_bounds(df)

    with st.container(border=True):
        st.subheader("Filtros de decisión")

        top_left, top_right = st.columns([2, 1])
        with top_left:
            selected_date_range = None
            if date_bounds:
                selected_date_range = st.date_input(
                    "Periodo",
                    value=date_bounds,
                    min_value=date_bounds[0],
                    max_value=date_bounds[1],
                )
        with top_right:
            st.metric("Registros disponibles", len(df))

        row_one = st.columns(4)
        with row_one[0]:
            selected_paises = render_filter_control("País", paises, "pais")
        with row_one[1]:
            selected_programas = render_filter_control("Programa", programas, "programa")
        with row_one[2]:
            selected_temas = render_filter_control("Tema", temas, "tema")
        with row_one[3]:
            selected_alertas = render_filter_control("Clasificación", alertas, "alerta")

        row_two = st.columns(2)
        with row_two[0]:
            selected_derivaciones = render_filter_control("Derivación", derivaciones, "derivacion")
        with row_two[1]:
            selected_estados = render_filter_control("Seguimiento", estados, "seguimiento")

    filtered_df = apply_dashboard_filters(
        df,
        selected_paises,
        selected_programas,
        selected_temas,
        selected_alertas,
        selected_derivaciones,
        selected_estados,
        selected_date_range,
    )

    active_filters = {
        "paises": has_custom_filter(selected_paises, paises),
        "programas": has_custom_filter(selected_programas, programas),
        "temas": has_custom_filter(selected_temas, temas),
        "alertas": has_custom_filter(selected_alertas, alertas),
        "derivaciones": has_custom_filter(selected_derivaciones, derivaciones),
        "estados": has_custom_filter(selected_estados, estados),
        "periodo": bool(date_bounds and selected_date_range != date_bounds),
    }

    return filtered_df, active_filters


def render_filter_status(filtered_df: pd.DataFrame, total_records: int, active_filters: dict) -> None:
    active_count = sum(1 for value in active_filters.values() if value)
    if active_count:
        st.info(
            f"Mostrando {len(filtered_df)} de {total_records} registros con {active_count} filtro(s) activo(s)."
        )
    else:
        st.info(f"Mostrando todos los registros: {total_records}.")


def render_kpis(filtered_df: pd.DataFrame) -> None:
    kpis = get_executive_kpis(filtered_df)

    st.subheader("Resumen para decisión")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Registros", kpis["total_registros"], help="Hallazgos incluidos en la vista actual.")
    c2.metric("Alertas críticas", kpis["alertas_criticas"], help="Riesgo alto y relevancia alta.")
    c3.metric("Alta prioridad", kpis["eventos_alta_prioridad"], help="Mayor puntaje combinado.")
    c4.metric("Pendientes", kpis["pendientes_de_accion"], help="Hallazgos de alta prioridad aún no usados ni descartados.")
    c5.metric("Accionables", kpis["insumos_accionables"], help="Hallazgos con decisión, acción manual o acción sugerida.")
    c6.metric("Usados", kpis["usados_en_decision"], help="Hallazgos marcados como usados en decisión.")


def render_insights(filtered_df: pd.DataFrame) -> None:
    insights = get_key_insights(filtered_df)

    st.subheader("Lectura rápida")
    i1, i2, i3 = st.columns(3)
    i1.metric("País con más riesgo", insights["pais_mas_critico"])
    i2.metric("Tema más frecuente", insights["tema_mas_recurrente"])
    i3.metric("Programa con más riesgo", insights["programa_mayor_riesgo"])


def render_decision_queue(filtered_df: pd.DataFrame) -> None:
    st.subheader("Cola de decisión")
    st.caption(OBSERVATORY_DECISION_QUESTION)

    queue = get_decision_queue(filtered_df)
    if queue.empty:
        st.warning("No hay hallazgos con decisión o acción recomendada en esta vista.")
        return

    styled_queue = queue.style.map(color_alert, subset=["clasificacion_alerta"])
    st.dataframe(
        styled_queue,
        width="stretch",
        hide_index=True,
        column_config={
            "fecha": st.column_config.DateColumn("Fecha"),
            "pais": st.column_config.TextColumn("País"),
            "programa": st.column_config.TextColumn("Programa"),
            "tema": st.column_config.TextColumn("Tema"),
            "clasificacion_alerta": st.column_config.TextColumn("Alerta"),
            "prioridad": st.column_config.NumberColumn("Prioridad", format="%d"),
            "titulo": st.column_config.TextColumn("Hallazgo"),
            "decision_impacto": st.column_config.TextColumn("Decisión que alimenta"),
            "accion_recomendada": st.column_config.TextColumn("Acción manual"),
            "accion_sugerida_sistema": st.column_config.TextColumn("Siguiente paso sugerido"),
            "derivacion": st.column_config.TextColumn("Derivar a"),
            "estado_seguimiento": st.column_config.TextColumn("Seguimiento"),
        },
    )


def render_charts(filtered_df: pd.DataFrame) -> None:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Riesgo por país")
        top_countries = get_top_risk_countries(filtered_df, top_n=7)
        if not top_countries.empty:
            st.bar_chart(top_countries.set_index("pais"))
        else:
            st.info("No hay información disponible.")

    with col_right:
        st.subheader("Temas más frecuentes")
        top_themes = get_top_themes(filtered_df, top_n=7)
        if not top_themes.empty:
            st.bar_chart(top_themes.set_index("tema"))
        else:
            st.info("No hay información disponible.")

    col_left_2, col_right_2 = st.columns([1, 1])

    with col_left_2:
        st.subheader("Alertas por clasificación")
        alert_distribution = get_alert_distribution(filtered_df)
        if not alert_distribution.empty:
            st.bar_chart(alert_distribution.set_index("clasificacion_alerta"))
        else:
            st.info("No hay información disponible.")

    with col_right_2:
        st.subheader("Riesgo por programa")
        risk_by_program = get_program_risk(filtered_df)
        if not risk_by_program.empty:
            st.bar_chart(risk_by_program.set_index("programa"))
        else:
            st.info("No hay información disponible.")

    st.subheader("Evolución temporal")
    timeline = get_timeline(filtered_df)
    if not timeline.empty:
        timeline["fecha"] = pd.to_datetime(timeline["fecha"])
        st.line_chart(timeline.set_index("fecha"))
    else:
        st.info("No hay fechas válidas para mostrar la serie temporal.")


def render_detail_tables(filtered_df: pd.DataFrame) -> None:
    st.subheader("Matriz riesgo vs oportunidad")
    matrix = get_risk_opportunity_matrix(filtered_df)
    if not matrix.empty:
        st.dataframe(matrix, width="stretch")
    else:
        st.info("No hay información para la matriz.")

    st.subheader("Eventos priorizados")
    priority_table = get_priority_table(filtered_df)
    styled_table = priority_table.style.map(color_alert, subset=["clasificacion_alerta"]).map(
        color_risk, subset=["nivel_riesgo"]
    )

    st.dataframe(
        styled_table,
        width="stretch",
        hide_index=True,
        column_config={
            "fecha": st.column_config.DateColumn("Fecha"),
            "pais": st.column_config.TextColumn("País"),
            "programa": st.column_config.TextColumn("Programa"),
            "tema": st.column_config.TextColumn("Tema"),
            "nivel_riesgo": st.column_config.TextColumn("Riesgo"),
            "nivel_oportunidad": st.column_config.TextColumn("Oportunidad"),
            "relevancia": st.column_config.NumberColumn("Relevancia", format="%d"),
            "prioridad": st.column_config.NumberColumn("Prioridad", format="%d"),
            "clasificacion_alerta": st.column_config.TextColumn("Clasificación"),
            "titulo": st.column_config.TextColumn("Título"),
            "decision_impacto": st.column_config.TextColumn("Decisión que alimenta"),
            "accion_recomendada": st.column_config.TextColumn("Acción manual"),
            "accion_sugerida_sistema": st.column_config.TextColumn("Siguiente paso sugerido"),
            "derivacion": st.column_config.TextColumn("Derivar a"),
            "estado_seguimiento": st.column_config.TextColumn("Seguimiento"),
        },
    )


def render_dashboard_page() -> None:
    st.title("Inteligencia del Observatorio")
    st.caption("Monitorear, anticipar y convertir evidencia en decisiones institucionales.")

    raw_df = get_all_data()
    if raw_df.empty:
        st.warning("Todavía no existen datos cargados.")
        return

    df = enrich_dataframe(raw_df)
    filtered_df, active_filters = render_filters(df)

    if filtered_df.empty:
        render_filter_status(filtered_df, len(df), active_filters)
        st.warning("No hay datos para los filtros seleccionados.")
        return

    render_filter_status(filtered_df, len(df), active_filters)
    render_kpis(filtered_df)
    render_insights(filtered_df)

    decision_tab, panorama_tab, detail_tab = st.tabs(
        ["Decisión", "Panorama", "Detalle de eventos"]
    )
    with decision_tab:
        render_decision_queue(filtered_df)
    with panorama_tab:
        render_charts(filtered_df)
    with detail_tab:
        render_detail_tables(filtered_df)
