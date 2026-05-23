import polars as pl

from aniwa.models.enums import ReportSection
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


def profile_dataframe(
    df: pl.DataFrame,
    mode: str = "deep",
    sections: set[ReportSection] | None = None,
) -> DatasetProfile:
    if sections is None:
        sections = set(ReportSection)

    rows = df.height
    columns = df.width

    summary = None
    if ReportSection.summary in sections:
        summary = DatasetSummary(
            rows=rows,
            columns=columns,
        )

    needs_column_profiles = _needs_column_profiles(sections)

    column_profiles = None
    if needs_column_profiles:
        column_profiles = _profile_columns(
            df=df,
            rows=rows,
            mode=mode,
            include_statistics=ReportSection.statistics in sections,
        )

    duplicate_rows = 0
    duplicate_percent = 0.0

    if _needs_duplicate_analysis(sections):
        duplicate_rows = rows - df.unique().height
        duplicate_percent = round((duplicate_rows / rows) * 100, 2) if rows else 0.0

    quality = None
    if ReportSection.quality in sections:
        quality = QualityProfile(
            duplicate_rows=duplicate_rows,
            duplicate_percent=duplicate_percent,
        )

    insights = None
    if ReportSection.insights in sections:
        insights = generate_insights(
            columns=column_profiles or [],
            duplicate_rows=duplicate_rows,
            total_rows=rows,
        )

    return DatasetProfile(
        summary=summary,
        columns=column_profiles,
        quality=quality,
        insights=insights,
    )


def _needs_column_profiles(sections: set[ReportSection]) -> bool:
    return any(
        section in sections
        for section in {
            ReportSection.schema,
            ReportSection.statistics,
            ReportSection.insights,
            ReportSection.charts,
        }
    )


def _needs_duplicate_analysis(sections: set[ReportSection]) -> bool:
    return any(
        section in sections
        for section in {
            ReportSection.quality,
            ReportSection.insights,
            ReportSection.charts,
        }
    )


def _profile_columns(
    df: pl.DataFrame,
    rows: int,
    mode: str,
    include_statistics: bool,
) -> list[ColumnProfile]:
    column_profiles: list[ColumnProfile] = []

    for col in df.columns:
        series = df[col]

        null_count = series.null_count()
        null_percent = round((null_count / rows) * 100, 2) if rows else 0.0
        unique_count = series.n_unique()

        numeric_stats = None

        if include_statistics and mode == "deep" and series.dtype in NUMERIC_DTYPES:
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

    return column_profiles


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
        column_name = col.name.lower()

        if col.null_percent >= 75:
            insights.append(
                Insight(
                    level="critical",
                    message=(
                        f"Column '{col.name}' is extremely sparse "
                        f"with {col.null_percent}% null values."
                    ),
                )
            )

        elif col.null_percent >= 40:
            insights.append(
                Insight(
                    level="warning",
                    message=(
                        f"Column '{col.name}' contains "
                        f"{col.null_percent}% null values."
                    ),
                )
            )

        if col.unique_count == 1:
            insights.append(
                Insight(
                    level="warning",
                    message=f"Column '{col.name}' contains only one unique value.",
                )
            )

        if (
            col.unique_count == total_rows
            and total_rows > 0
            and "name" not in column_name
        ):
            insights.append(
                Insight(
                    level="info",
                    message=f"Column '{col.name}' may be a unique identifier.",
                )
            )

        if total_rows > 0:
            cardinality_ratio = col.unique_count / total_rows

            if cardinality_ratio >= 0.9 and total_rows > 20:
                insights.append(
                    Insight(
                        level="info",
                        message=f"Column '{col.name}' has very high cardinality.",
                    )
                )

        pii_keywords = [
            "email",
            "phone",
            "mobile",
            "ssn",
            "passport",
            "card",
            "credit",
            "address",
        ]

        if any(keyword in column_name for keyword in pii_keywords):
            insights.append(
                Insight(
                    level="warning",
                    message=f"Column '{col.name}' may contain sensitive information.",
                )
            )

        if col.numeric_stats:
            stats = col.numeric_stats

            if stats.min is not None and stats.min < 0:
                insights.append(
                    Insight(
                        level="info",
                        message=f"Column '{col.name}' contains negative values.",
                    )
                )

            if (
                stats.mean is not None
                and stats.std is not None
                and stats.mean != 0
            ):
                variability_ratio = abs(stats.std / stats.mean)

                if variability_ratio > 2:
                    insights.append(
                        Insight(
                            level="info",
                            message=f"Column '{col.name}' shows high variability.",
                        )
                    )

    return insights