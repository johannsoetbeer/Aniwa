from pathlib import Path

from aniwa.models.profile import DatasetProfile


def render_markdown_report(
    profile: DatasetProfile,
    output: str | None = None,
) -> str:
    sections = [
        _render_metadata(profile),
        _render_summary(profile),
        _render_columns(profile),
        _render_numeric_stats(profile),
        _render_quality(profile),
        _render_insights(profile),
    ]

    markdown_content = "\n\n".join(filter(None, sections))

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(markdown_content, encoding="utf-8")
        return f"Markdown report written to {output}"

    return markdown_content


def _render_metadata(profile: DatasetProfile) -> str:
    if not profile.metadata:
        return ""

    metadata = profile.metadata
    rows = []

    _append_metadata_row(rows, "Generated At", metadata.generated_at)
    _append_metadata_row(rows, "Aniwa Version", metadata.aniwa_version)
    _append_metadata_row(rows, "Python Version", metadata.python_version)
    _append_metadata_row(rows, "Operating System", metadata.operating_system)
    _append_metadata_row(rows, "Polars Version", metadata.polars_version)

    _append_metadata_row(rows, "Dataset Path", metadata.dataset_path)
    _append_metadata_row(rows, "Dataset File Type", metadata.dataset_file_type)
    _append_metadata_row(rows, "Dataset Size", metadata.dataset_size)

    _append_metadata_row(rows, "Profiling Mode", metadata.profiling_mode)
    _append_metadata_row(rows, "Report Format", metadata.report_format)
    _append_metadata_row(rows, "Report Template", metadata.report_template)

    if metadata.included_sections:
        _append_metadata_row(
            rows,
            "Included Sections",
            ", ".join(metadata.included_sections),
        )

    if metadata.excluded_sections:
        _append_metadata_row(
            rows,
            "Excluded Sections",
            ", ".join(metadata.excluded_sections),
        )

    _append_metadata_row(rows, "Profiling Duration", metadata.profiling_duration)
    _append_metadata_row(rows, "Command Used", metadata.command_used)

    return (
        "## Profiling Metadata\n"
        "| Field | Value |\n"
        "| --- | --- |\n"
        + "\n".join(rows)
    )


def _append_metadata_row(
    rows: list[str],
    field: str,
    value: str | None,
) -> None:
    if value is None:
        return

    rows.append(f"| {field} | {value} |")


def _render_summary(profile: DatasetProfile) -> str:
    if not profile.summary:
        return "## Summary\nNot available"

    return (
        "## Summary\n"
        "| Metric | Value |\n"
        "| --- | --- |\n"
        f"| Rows | {profile.summary.rows:,} |\n"
        f"| Columns | {profile.summary.columns:,} |"
    )


def _render_columns(profile: DatasetProfile) -> str:
    if not profile.columns:
        return ""

    header = (
        "| Column | Type | Nulls | Null % | Unique |\n"
        "| --- | --- | --- | --- | --- |"
    )

    rows = []

    for col in profile.columns:
        rows.append(
            f"| {col.name} | "
            f"{col.dtype} | "
            f"{col.null_count:,} | "
            f"{col.null_percent:.2f}% | "
            f"{col.unique_count:,} |"
        )

    return "## Columns\n" + header + "\n" + "\n".join(rows)


def _render_numeric_stats(profile: DatasetProfile) -> str:
    if not profile.columns:
        return ""

    numeric_cols = [col for col in profile.columns if col.numeric_stats]

    if not numeric_cols:
        return ""

    header = (
        "| Column | Min | Max | Mean | Median | Std |\n"
        "| --- | --- | --- | --- | --- | --- |"
    )

    rows = []

    for col in numeric_cols:
        stats = col.numeric_stats

        rows.append(
            f"| {col.name} | "
            f"{_format_number(stats.min)} | "
            f"{_format_number(stats.max)} | "
            f"{_format_number(stats.mean)} | "
            f"{_format_number(stats.median)} | "
            f"{_format_number(stats.std)} |"
        )

    return "## Numeric Statistics\n" + header + "\n" + "\n".join(rows)


def _render_quality(profile: DatasetProfile) -> str:
    if not profile.quality:
        return ""

    return (
        "## Data Quality\n"
        f"- **Duplicate Rows:** {profile.quality.duplicate_rows:,}\n"
        f"- **Duplicate %:** {profile.quality.duplicate_percent}%"
    )


def _render_insights(profile: DatasetProfile) -> str:
    if not profile.insights:
        return "## Insights\nNo major issues detected."

    rows = [
        f"| {insight.level.upper()} | {insight.message} |"
        for insight in profile.insights
    ]

    return (
        "## Insights\n"
        "| Level | Message |\n"
        "| --- | --- |\n"
        + "\n".join(rows)
    )


def _format_number(value: float | None) -> str:
    if value is None:
        return "-"

    if float(value).is_integer():
        return f"{int(value):,}"

    return f"{value:,.4f}"