"""
Render every dashboard chart from mock data into standalone HTML pages.

    python -m tests.preview            # write previews/*.html and open them
    python -m tests.preview --no-open  # just write them

The pages are self-contained (they work offline) and nothing here touches the
sensors, the CSVs or Streamlit.
"""
import sys
import webbrowser
from pathlib import Path

import charts
from readings import live_readings
from tests.mock_data import SCENARIOS

PREVIEW_DIR = Path(__file__).resolve().parent.parent / "previews"

CHART_BUILDERS = (
    charts.co2_chart,
    charts.temperature_chart,
    charts.humidity_chart,
    charts.pm2_5_chart,
    charts.pm10_chart,
)


def write_previews() -> list[Path]:
    """Write one HTML page per mock-data scenario and return their paths."""
    PREVIEW_DIR.mkdir(exist_ok=True)
    paths = []
    for name, make_data in SCENARIOS.items():
        df = make_data()
        figures = [build(df) for build in CHART_BUILDERS]
        table = live_readings(df.iloc[-1], df.iloc[-1]).to_html()
        # Embed plotly.js once, in the first figure, and reuse it for the rest
        body = "\n".join(
            fig.to_html(full_html=False, include_plotlyjs=True if i == 0 else False)
            for i, fig in enumerate(figures)
        )
        path = PREVIEW_DIR / f"{name}.html"
        path.write_text(
            f"<!doctype html><meta charset='utf-8'><title>{name}</title>"
            f"<body style='font-family:sans-serif'><h2>{name}</h2><h3>Live Readings</h3>{table}{body}</body>"
        )
        paths.append(path)
    return paths


if __name__ == "__main__":
    written = write_previews()
    for path in written:
        print(path)
        if "--no-open" not in sys.argv:
            webbrowser.open(path.as_uri())
