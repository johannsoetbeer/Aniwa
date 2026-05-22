import polars as pl
import time

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


def profile_dataframe(df: pl.DataFrame, mode: str = "deep", sections: set[ReportSection] | None = None,) -> DatasetProfile:
    start_time = time.time()

    if sections is None:
        sections = set(ReportSection)

    rows = df.height
    columns = df.width

    summary = None
    if ReportSection.summary in sections:
        summary = DatasetSummary(rows=rows, columns=columns)

    column_profiles = None
    if (
            ReportSection.schema in sections
            or ReportSection.statistics in sections
            or ReportSection.quality in sections
            or ReportSection.insights in sections
    ):
        column_profiles = []

        for col in df.columns:
            series = df[col]

            null_count = series.null_count()
            null_percent = round((null_count / rows) * 100, 2) if rows else 0
            unique_count = series.n_unique()

            numeric_stats = None

            if ReportSection.statistics in sections and mode == "deep" and series.dtype in NUMERIC_DTYPES:
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

    duplicate_rows = 0
    duplicate_percent = 0

    if ReportSection.quality in sections or ReportSection.insights in sections:
        duplicate_rows = rows - df.unique().height
        duplicate_percent = round((duplicate_rows / rows) * 100, 2) if rows else 0

    quality = None
    if ReportSection.quality in sections:
        quality = QualityProfile(
            duplicate_rows=duplicate_rows,
            duplicate_percent=duplicate_percent,
        )

    insights = None
    if ReportSection.insights in sections:
        insights = generate_insights(column_profiles or [], duplicate_rows, rows)

    end_time = time.time()

    duration = round(end_time - start_time, 4)

    return DatasetProfile(
        summary=summary,
        columns=column_profiles,
        quality=quality,
        insights=insights,
        duration=duration
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
        column_name = col.name.lower()

        #
        # High null percentage
        #
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

        #
        # Constant columns
        #
        if col.unique_count == 1:
            insights.append(
                Insight(
                    level="warning",
                    message=(
                        f"Column '{col.name}' contains only one unique value."
                    ),
                )
            )

        #
        # Possible unique identifiers
        #
        if (
            col.unique_count == total_rows
            and total_rows > 0
            and "name" not in column_name
        ):
            insights.append(
                Insight(
                    level="info",
                    message=(
                        f"Column '{col.name}' may be a unique identifier."
                    ),
                )
            )

        #
        # High cardinality detection
        #
        if total_rows > 0:
            cardinality_ratio = col.unique_count / total_rows

            if cardinality_ratio >= 0.9 and total_rows > 20:
                insights.append(
                    Insight(
                        level="info",
                        message=(
                            f"Column '{col.name}' has very high cardinality."
                        ),
                    )
                )

        #
        # Potential PII detection
        #
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
                    message=(
                        f"Column '{col.name}' may contain sensitive information."
                    ),
                )
            )

        #
        # Numeric statistics insights
        #
        if col.numeric_stats:
            stats = col.numeric_stats

            #
            # Negative values
            #
            if stats.min is not None and stats.min < 0:
                insights.append(
                    Insight(
                        level="info",
                        message=(
                            f"Column '{col.name}' contains negative values."
                        ),
                    )
                )

            #
            # Large spread detection
            #
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
                            message=(
                                f"Column '{col.name}' shows high variability."
                            ),
                        )
                    )

    return insights