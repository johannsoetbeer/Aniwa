from enum import Enum

class ReportSection(str, Enum):
    summary = "summary"
    schema = "schema"
    statistics = "statistics"
    quality = "quality"
    insights = "insights"
    charts = "charts"