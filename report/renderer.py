from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from analysis.schema import KanoOutput

_TEMPLATE_DIR = Path(__file__).parent


def render_report(output: KanoOutput) -> str:
    """Render a KanoOutput to a self-contained HTML report string."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("template.html")
    return template.render(
        product_name=output.product_name,
        analysis_date=date.today().isoformat(),
        target_market=getattr(output, "target_market", None),
        features=output.features,
        summary=output.summary,
        roadmap=output.roadmap,
        strategic_narrative=output.strategic_narrative,
    )
