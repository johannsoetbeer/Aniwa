import polars as pl

from aniwa.core.profiler import profile_dataframe


def test_profile_dataframe_summary():
    df = pl.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Ama", "Kofi", "Yaw"],
        }
    )

    profile = profile_dataframe(df)

    assert profile.summary.rows == 3
    assert profile.summary.columns == 2


def test_profile_dataframe_nulls():
    df = pl.DataFrame(
        {
            "id": [1, 2, 3],
            "email": ["a@test.com", None, None],
        }
    )

    profile = profile_dataframe(df)

    email_profile = next(col for col in profile.columns if col.name == "email")

    assert email_profile.null_count == 2
    assert email_profile.null_percent == 66.67


def test_duplicate_detection():
    df = pl.DataFrame(
        {
            "id": [1, 1, 2],
            "name": ["Ama", "Ama", "Kofi"],
        }
    )

    profile = profile_dataframe(df)

    assert profile.quality.duplicate_rows == 1


def test_numeric_statistics():
    df = pl.DataFrame(
        {
            "revenue": [100, 200, 300, 400],
            "name": ["Ama", "Kofi", "Yaw", "Akosua"],
        }
    )

    profile = profile_dataframe(df)

    revenue_profile = next(col for col in profile.columns if col.name == "revenue")

    assert revenue_profile.numeric_stats is not None
    assert revenue_profile.numeric_stats.min == 100.0
    assert revenue_profile.numeric_stats.max == 400.0
    assert revenue_profile.numeric_stats.mean == 250.0
    assert revenue_profile.numeric_stats.median == 250.0