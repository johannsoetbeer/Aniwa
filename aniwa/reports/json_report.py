from pathlib import Path

from aniwa.models.profile import DatasetProfile


def render_json_report(
    profile: DatasetProfile,
    output: str | None = None,
) -> str:
    json_output = profile.model_dump_json(
        indent=2,
        exclude_none=True,
    )

    if output:
        output_path = Path(output)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json_output,
            encoding="utf-8",
        )

    return json_output