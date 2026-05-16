import polars as pl

from aniwa.models.profile import (
    ColumnProfile,
    DatasetProfile,
    DatasetSummary,
    Insight,
    NumericStats,
    QualityProfile,
)


NUMERIC_DTYPES = {
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
    pl.UInt8,
    pl.UInt16,
    pl.UInt32,
    pl.UInt64,
    pl.Float32,
    pl.Float64,
}


def profile_dataframe(df: pl.DataFrame) -> DatasetProfile:
    rows = df.height
    columns = df.width

    column_profiles: list[ColumnProfile] = []

    for col in df.columns:
        series = df[col]

        null_count = series.null_count()
        null_percent = round((null_count / rows) * 100, 2) if rows else 0
        unique_count = series.n_unique()

        numeric_stats = None

        if series.dtype in NUMERIC_DTYPES:
            numeric_stats = NumericStats(
                min=_safe_float(series.min()),
                max=_safe_float(series.max()),
                mean=_safe_float(series.mean()),
                median=_safe_float(series.median()),
                std=_safe_float(series.std()),
            )

        column_profiles.append(
            ColumnProfile(
                name=col,
                dtype=str(series.dtype),
                null_count=null_count,
                null_percent=null_percent,
                unique_count=unique_count,
                numeric_stats=numeric_stats,
            )
        )

    duplicate_rows = rows - df.unique().height
    duplicate_percent = round((duplicate_rows / rows) * 100, 2) if rows else 0

    insights = generate_insights(column_profiles, duplicate_rows, rows)

    return DatasetProfile(
        summary=DatasetSummary(rows=rows, columns=columns),
        columns=column_profiles,
        quality=QualityProfile(
            duplicate_rows=duplicate_rows,
            duplicate_percent=duplicate_percent,
        ),
        insights=insights,
    )


def _safe_float(value: object) -> float | None:
    if value is None:
        return None

    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def generate_insights(
    columns: list[ColumnProfile],
    duplicate_rows: int,
    total_rows: int,
) -> list[Insight]:
    insights: list[Insight] = []

    if duplicate_rows > 0:
        insights.append(
            Insight(
                level="warning",
                message=f"{duplicate_rows} duplicate rows detected.",
            )
        )

    for col in columns:
        if col.null_percent > 50:
            insights.append(
                Insight(
                    level="critical",
                    message=f"Column '{col.name}' is highly sparse with {col.null_percent}% nulls.",
                )
            )

        if col.unique_count == total_rows and total_rows > 0:
            insights.append(
                Insight(
                    level="info",
                    message=f"Column '{col.name}' may be a unique identifier.",
                )
            )

        if col.unique_count == 1:
            insights.append(
                Insight(
                    level="warning",
                    message=f"Column '{col.name}' has only one unique value.",
                )
            )

    return insights