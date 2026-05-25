from pathlib import Path

from typer.testing import CliRunner

from aniwa.cli import app


runner = CliRunner()


def write_csv(path: Path) -> None:
    path.write_text(
        "customer_id,name,email,revenue\n"
        "1,Ama,ama@example.com,1200\n"
        "2,Kofi,kofi@example.com,950\n"
        "3,Esi,,1100\n",
        encoding="utf-8",
    )


def test_cli_mutually_exclusive_include_exclude(tmp_path):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--include",
            "summary",
            "--exclude",
            "statistics",
        ],
    )

    assert result.exit_code != 0
    assert "Use either --include or --exclude, not both" in result.output


def test_cli_invalid_include_section(tmp_path):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--include",
            "invalid_section",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid report section: invalid_section" in result.output


def test_cli_invalid_exclude_section(tmp_path):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--exclude",
            "unknown_block",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid report section: unknown_block" in result.output


def test_cli_json_include_summary_only(tmp_path, monkeypatch):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)
    # CLI now writes a default JSON file when no --output is provided.
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "json",
            "--include",
            "summary",
        ],
    )

    expected_file = tmp_path / "aniwa_report.json"

    assert result.exit_code == 0
    assert "JSON report written to" in result.output
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert '"summary"' in content
    assert '"rows"' in content
    assert '"columns"' in content
    assert '"quality"' not in content
    assert '"insights"' not in content


def test_cli_json_include_summary_and_insights(tmp_path, monkeypatch):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)
    # CLI now writes a default JSON file when no --output is provided.
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "json",
            "--include",
            "summary,insights",
        ],
    )

    expected_file = tmp_path / "aniwa_report.json"

    assert result.exit_code == 0
    assert "JSON report written to" in result.output
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert '"summary"' in content
    assert '"insights"' in content
    assert '"quality"' not in content


def test_cli_json_exclude_statistics(tmp_path, monkeypatch):
    csv_path = tmp_path / "customers.csv"
    write_csv(csv_path)
    # CLI now writes a default JSON file when no --output is provided.
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "json",
            "--exclude",
            "statistics",
        ],
    )

    expected_file = tmp_path / "aniwa_report.json"

    assert result.exit_code == 0
    assert "JSON report written to" in result.output
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert '"summary"' in content
    assert '"quality"' in content
    assert '"insights"' in content
    assert '"numeric_stats"' not in content


def test_cli_html_include_summary_and_insights(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_path = tmp_path / "summary_insights.html"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "html",
            "--include",
            "summary,insights",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    html = output_path.read_text(encoding="utf-8")

    assert "Rows" in html
    assert "Columns" in html
    assert "Insights" in html
    assert '<div class="label">Duplicate Rows</div>' not in html
    assert "Column Profile" not in html
    assert "Numeric Statistics" not in html


def test_cli_html_include_summary_only(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_path = tmp_path / "summary_only.html"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "html",
            "--include",
            "summary",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    html = output_path.read_text(encoding="utf-8")

    assert "Rows" in html
    assert "Columns" in html
    assert '<div class="label">Duplicate Rows</div>' not in html
    assert "Column Profile" not in html
    assert "<h2>Charts</h2>" not in html
    assert "Insights" not in html


def test_cli_html_exclude_quality(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_path = tmp_path / "exclude_quality.html"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "html",
            "--exclude",
            "quality",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    html = output_path.read_text(encoding="utf-8")

    assert "Rows" in html
    assert "Columns" in html
    assert '<div class="label">Duplicate Rows</div>' not in html
    assert "Column Profile" in html
    assert "Insights" in html


def test_cli_html_exclude_charts(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_path = tmp_path / "exclude_charts.html"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "html",
            "--exclude",
            "charts",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    html = output_path.read_text(encoding="utf-8")

    assert "Rows" in html
    assert "Columns" in html
    assert "Column Profile" in html
    assert "<h2>Charts</h2>" not in html
    assert "aniwa-default-chart-data" not in html


def test_cli_markdown_include_summary_only(tmp_path, monkeypatch):
    csv_path = tmp_path / "customers.csv"

    write_csv(csv_path)
    # CLI now writes a default Markdown file when no --output is provided.
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "markdown",
            "--include",
            "summary",
        ],
    )

    expected_file = tmp_path / "aniwa_report.md"

    assert result.exit_code == 0
    assert "Markdown report written to" in result.output
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert "## Summary" in content
    assert "## Columns" not in content
    assert "## Data Quality" not in content
    assert "## Insights" not in content


def test_cli_json_output_dir_creates_json_file(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_dir = tmp_path / "reports"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "json",
            "--output-dir",
            str(output_dir),
        ],
    )

    expected_file = output_dir / "aniwa_report.json"

    assert result.exit_code == 0
    assert expected_file.exists()
    assert "JSON report written to" in result.output
    assert expected_file.read_text(encoding="utf-8").startswith("{")


def test_cli_html_output_dir_creates_html_file(tmp_path):
    csv_path = tmp_path / "customers.csv"
    output_dir = tmp_path / "reports"

    write_csv(csv_path)

    result = runner.invoke(
        app,
        [
            str(csv_path),
            "--report",
            "html",
            "--output-dir",
            str(output_dir),
        ],
    )

    expected_file = output_dir / "aniwa_report.html"

    assert result.exit_code == 0
    assert expected_file.exists()
    assert "HTML report written to" in result.output
    assert "<!DOCTYPE html>" in expected_file.read_text(encoding="utf-8")
