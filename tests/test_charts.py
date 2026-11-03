import pytest

import charts
from constants import (CO2_WARNING_PPM, CO2_Y_RANGE, HUMIDITY_WARNING_PERCENT, HUMIDITY_Y_RANGE,
                       PM2_5_CAUTION_UG_M3, PM2_5_WARNING_UG_M3, PM2_5_Y_RANGE,
                       PM10_CAUTION_UG_M3, PM10_WARNING_UG_M3, PM10_Y_RANGE,
                       TEMPERATURE_WARNING_C, TEMPERATURE_Y_RANGE)
from tests.mock_data import SCENARIOS
from tests.preview import CHART_BUILDERS, PREVIEW_DIR, write_previews

# builder -> (fixed y range, warning thresholds lowest first)
EXPECTED = {
    charts.co2_chart: (CO2_Y_RANGE, [CO2_WARNING_PPM]),
    charts.temperature_chart: (TEMPERATURE_Y_RANGE, [TEMPERATURE_WARNING_C]),
    charts.humidity_chart: (HUMIDITY_Y_RANGE, [HUMIDITY_WARNING_PERCENT]),
    charts.pm2_5_chart: (PM2_5_Y_RANGE, [PM2_5_CAUTION_UG_M3, PM2_5_WARNING_UG_M3]),
    charts.pm10_chart: (PM10_Y_RANGE, [PM10_CAUTION_UG_M3, PM10_WARNING_UG_M3]),
}


@pytest.fixture(params=SCENARIOS.values(), ids=SCENARIOS.keys())
def df(request):
    return request.param()


@pytest.mark.parametrize("build", CHART_BUILDERS, ids=lambda b: b.__name__)
class TestEachChart:
    def test_builds_for_every_scenario(self, build, df):
        fig = build(df)
        assert len(fig.data) >= 1
        assert all(len(trace.x) == len(df) for trace in fig.data)

    def test_y_axis_is_fixed(self, build, df):
        y_range, _ = EXPECTED[build]
        assert tuple(build(df).layout.yaxis.range) == y_range

    def test_warning_bands_match_thresholds(self, build, df):
        y_range, thresholds = EXPECTED[build]
        bands = build(df).layout.shapes
        assert [band.y0 for band in bands] == thresholds
        # each band runs up to the next one, and the last reaches the top of the axis
        assert [band.y1 for band in bands] == thresholds[1:] + [y_range[1]]

    def test_title_uses_line_colour(self, build, df):
        fig = build(df)
        assert fig.layout.title.font.color == fig.data[0].line.color


def test_each_chart_has_its_own_colour(df):
    colours = [build(df).data[0].line.color for build in CHART_BUILDERS]
    assert len(set(colours)) == len(colours)


def test_writes_preview_pages():
    """Also the way to eyeball changes: run this, then open previews/*.html."""
    paths = write_previews()
    assert {p.stem for p in paths} == set(SCENARIOS)
    assert all(p.parent == PREVIEW_DIR and p.stat().st_size > 0 for p in paths)
