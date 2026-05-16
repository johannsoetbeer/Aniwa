from pydantic import BaseModel


class DatasetSummary(BaseModel):
    rows: int
    columns: int


class NumericStats(BaseModel):
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_count: int
    null_percent: float
    unique_count: int
    numeric_stats: NumericStats | None = None


class QualityProfile(BaseModel):
    duplicate_rows: int
    duplicate_percent: float


class Insight(BaseModel):
    level: str
    message: str


class DatasetProfile(BaseModel):
    summary: DatasetSummary
    columns: list[ColumnProfile]
    quality: QualityProfile
    insights: list[Insight]