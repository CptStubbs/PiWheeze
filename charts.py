import pandas as pd
import plotly.graph_objects as go

from constants import (CO2_PPM, CO2_WARNING_PPM, CO2_Y_RANGE,
                       HUMIDITY, HUMIDITY_WARNING_PERCENT, HUMIDITY_Y_RANGE,
                       PM1_0, PM2_5, PM10,
                       PM2_5_CAUTION_UG_M3, PM2_5_WARNING_UG_M3, PM2_5_Y_RANGE,
                       PM10_CAUTION_UG_M3, PM10_WARNING_UG_M3, PM10_Y_RANGE,
                       TEMPERATURE, TEMPERATURE_WARNING_C, TEMPERATURE_Y_RANGE,
                       TIMESTAMP)

# Chart construction for the dashboard. Kept free of Streamlit so charts can be
# built (and previewed) from plain DataFrames; see tests/test_charts.py.

# One colour per chart so they're recognisable at a glance. Kept away from red/yellow,
# which are reserved for the warning bands, and mid-tone so they read on light and dark themes.
CO2_COLOUR = "#2E86DE"
TEMPERATURE_COLOUR = "#9B59B6"
HUMIDITY_COLOUR = "#16A085"
PM2_5_COLOUR = "#E84393"
PM1_0_COLOUR = "#F8A5CF"  # lighter shade of the PM2.5 colour: same chart, secondary line
PM10_COLOUR = "#A1887F"

RED = "rgba(220, 50, 47, 0.18)"
YELLOW = "rgba(240, 180, 0, 0.18)"


def line_chart(df: pd.DataFrame, series: list[tuple[str, str, str]], title: str, unit: str,
               y_range: tuple[float, float], bands: list[tuple[float, str, str]] = ()) -> go.Figure:
    """
    Build one chart; series is a list of (column, legend name, colour) sharing one y-axis.

    y_range is fixed (not autoscaled) so the same level always sits at the same
    height. bands are (lower bound, colour, label) warning areas, listed lowest
    first; each is shaded up to the next band's lower bound (the last, to the top).
    """
    fig = go.Figure()
    for column, name, colour in series:
        fig.add_trace(go.Scatter(x=df[TIMESTAMP], y=df[column], mode='lines', name=name,
                                 line=dict(color=colour)))

    # Each band stops where the next one starts (the last runs to the top), and its
    # label sits at the bottom of the band, so stacked bands never overlap each other
    uppers = [lower for lower, _, _ in bands[1:]] + [y_range[1]]
    for (lower, colour, label), upper in zip(bands, uppers):
        fig.add_hrect(y0=lower, y1=upper, fillcolor=colour, line_width=0, layer="below",
                      annotation_text=label, annotation_position="bottom right")
    fig.update_layout(
        title=dict(text=title, font=dict(color=series[0][2])),
        xaxis=dict(title="Time"),
        yaxis=dict(title=unit, range=list(y_range)),
        legend=dict(x=0, y=1)
    )
    return fig


def co2_chart(df: pd.DataFrame) -> go.Figure:
    return line_chart(df, [(CO2_PPM, "CO2 ppm", CO2_COLOUR)], "CO₂ History", "ppm", CO2_Y_RANGE,
                      [(CO2_WARNING_PPM, RED, f"High CO₂ ({CO2_WARNING_PPM}+ ppm)")])


def temperature_chart(df: pd.DataFrame) -> go.Figure:
    return line_chart(df, [(TEMPERATURE, "Temperature °C", TEMPERATURE_COLOUR)],
                      "Temperature History", "°C", TEMPERATURE_Y_RANGE,
                      [(TEMPERATURE_WARNING_C, RED, f"Warm ({TEMPERATURE_WARNING_C}+ °C)")])


def humidity_chart(df: pd.DataFrame) -> go.Figure:
    return line_chart(df, [(HUMIDITY, "Humidity %", HUMIDITY_COLOUR)], "Humidity History", "%", HUMIDITY_Y_RANGE,
                      [(HUMIDITY_WARNING_PERCENT, RED, f"High humidity ({HUMIDITY_WARNING_PERCENT}+ %)")])


# PM2.5 and PM10 have different guideline values, so each gets its own chart
# (PM1.0 has no guideline; it rides along on the PM2.5 chart for context).
def pm2_5_chart(df: pd.DataFrame) -> go.Figure:
    return line_chart(df, [(PM2_5, "PM2.5", PM2_5_COLOUR), (PM1_0, "PM1.0", PM1_0_COLOUR)],
                      "PM2.5 / PM1.0 History", "µg/m³", PM2_5_Y_RANGE,
                      [(PM2_5_CAUTION_UG_M3, YELLOW, f"PM2.5 above WHO 24h guideline ({PM2_5_CAUTION_UG_M3})"),
                       (PM2_5_WARNING_UG_M3, RED, f"PM2.5 unhealthy for sensitive groups ({PM2_5_WARNING_UG_M3})")])


def pm10_chart(df: pd.DataFrame) -> go.Figure:
    return line_chart(df, [(PM10, "PM10", PM10_COLOUR)], "PM10 History", "µg/m³", PM10_Y_RANGE,
                      [(PM10_CAUTION_UG_M3, YELLOW, f"PM10 above WHO 24h guideline ({PM10_CAUTION_UG_M3})"),
                       (PM10_WARNING_UG_M3, RED, f"PM10 unhealthy for sensitive groups ({PM10_WARNING_UG_M3})")])
