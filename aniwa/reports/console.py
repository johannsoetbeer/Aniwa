from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aniwa.models.profile import DatasetProfile


console = Console()


def render_console_report(profile: DatasetProfile) -> None:
    console.print(
        Panel.fit(
            f"[bold]Rows:[/bold] {profile.summary.rows}\n"
            f"[bold]Columns:[/bold] {profile.summary.columns}\n"
            f"[bold]Duplicate Rows:[/bold] {profile.quality.duplicate_rows}\n"
            f"[bold]Duplicate %:[/bold] {profile.quality.duplicate_percent}%",
            title="Aniwa Dataset Profile",
        )
    )

    table = Table(title="Column Profile")
    table.add_column("Column")
    table.add_column("Type")
    table.add_column("Nulls")
    table.add_column("Null %")
    table.add_column("Unique")

    for col in profile.columns:
        table.add_row(
            col.name,
            col.dtype,
            str(col.null_count),
            f"{col.null_percent}%",
            str(col.unique_count),
        )

    console.print(table)

    numeric_columns = [col for col in profile.columns if col.numeric_stats]

    if numeric_columns:
        stats_table = Table(title="Numeric Statistics")
        stats_table.add_column("Column")
        stats_table.add_column("Min")
        stats_table.add_column("Max")
        stats_table.add_column("Mean")
        stats_table.add_column("Median")
        stats_table.add_column("Std")

        for col in numeric_columns:
            stats = col.numeric_stats
            stats_table.add_row(
                col.name,
                str(stats.min),
                str(stats.max),
                str(stats.mean),
                str(stats.median),
                str(stats.std),
            )

        console.print(stats_table)

    if profile.insights:
        insight_table = Table(title="Insights")
        insight_table.add_column("Level")
        insight_table.add_column("Message")

        for insight in profile.insights:
            insight_table.add_row(insight.level, insight.message)

        console.print(insight_table)