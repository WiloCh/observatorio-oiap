import pandas as pd

from src.domain.constants import (
    DEDUPLICATION_COLUMNS,
    DERIVATION_TARGETS,
    EVENT_COLUMNS,
    FOLLOW_UP_STATUSES,
    LEVELS,
    RELEVANCE_RANGE,
    TEXT_COLUMNS,
)


def generate_template() -> pd.DataFrame:
    return pd.DataFrame(columns=EVENT_COLUMNS)


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_date(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return ""


def normalize_score(value: object) -> int:
    if pd.isna(value) or str(value).strip() == "":
        return 0
    try:
        number = int(float(value))
        return max(RELEVANCE_RANGE.minimum, min(number, RELEVANCE_RANGE.maximum))
    except (TypeError, ValueError):
        return 0


def normalize_level(value: object) -> str:
    value = normalize_text(value).capitalize()
    return value if value in LEVELS else ""


def normalize_derivation(value: object) -> str:
    value = normalize_text(value)
    return value if value in DERIVATION_TARGETS else ""


def normalize_follow_up_status(value: object) -> str:
    value = normalize_text(value)
    return value if value in FOLLOW_UP_STATUSES else "Detectado"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df.columns = [str(col).strip().lower() for col in clean_df.columns]

    for column in EVENT_COLUMNS:
        if column not in clean_df.columns:
            clean_df[column] = ""

    clean_df = clean_df[EVENT_COLUMNS]
    clean_df["fecha"] = clean_df["fecha"].apply(normalize_date)

    for column in TEXT_COLUMNS:
        clean_df[column] = clean_df[column].apply(normalize_text)

    clean_df["nivel_riesgo"] = clean_df["nivel_riesgo"].apply(normalize_level)
    clean_df["nivel_oportunidad"] = clean_df["nivel_oportunidad"].apply(normalize_level)
    clean_df["relevancia"] = clean_df["relevancia"].apply(normalize_score)
    clean_df["derivacion"] = clean_df["derivacion"].apply(normalize_derivation)
    clean_df["estado_seguimiento"] = clean_df["estado_seguimiento"].apply(
        normalize_follow_up_status
    )

    clean_df = clean_df[clean_df["titulo"] != ""]
    clean_df = clean_df.drop_duplicates(
        subset=DEDUPLICATION_COLUMNS,
        keep="first",
    )

    return clean_df.reset_index(drop=True)
