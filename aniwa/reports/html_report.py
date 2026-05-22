from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from aniwa.models.profile import DatasetProfile


AVAILABLE_TEMPLATES = {
    "default": "default.html",
    "clean": "clean.html",
    "compact": "compact.html",
    "enterprise": "enterprise.html",
    "dark": "dark.html",
}


def render_html_report(
    profile: DatasetProfile,
    output: str | None = None,
    template: str = "default",
) -> str:
    template_dir = Path(__file__).parent / "templates"

    if template not in AVAILABLE_TEMPLATES:
        valid_templates = ", ".join(AVAILABLE_TEMPLATES)
        raise ValueError(
            f"Invalid HTML report template: {template}. "
            f"Valid templates are: {valid_templates}."
        )

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    html_template = env.get_template(AVAILABLE_TEMPLATES[template])
    html = html_template.render(profile=profile)

    if output:
        Path(output).write_text(html, encoding="utf-8")

    return html