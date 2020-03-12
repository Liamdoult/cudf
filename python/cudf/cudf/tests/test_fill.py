import pytest
from pandas.util.testing import assert_series_equal

import cudf


@pytest.mark.parametrize(
    "fill_value,data",
    [
        ("x", ["a", "b", "c", "d", "e", "f"]),
        (7, [6, 3, 4, 2, 1, 7, 8, 5]),
        (0.8, [0.6, 0.3, 0.4, 0.2, 0.1, 0.7, 0.8, 0.5]),
    ],
)
@pytest.mark.parametrize("begin,end", [(0, -1), (0, 4), (1, -1), (1, 4)])
@pytest.mark.parametrize("inplace", [True, False])
def test_fill(data, fill_value, begin, end, inplace):
    gs = cudf.Series(data)
    ps = gs.to_pandas()

    if inplace:
        actual = gs
        gs[begin:end] = fill_value
    else:
        actual = gs._fill([fill_value], begin, end, inplace)
        assert actual is not gs

    ps[begin:end] = fill_value

    assert_series_equal(ps, actual.to_pandas())
