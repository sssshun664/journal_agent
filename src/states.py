from typing import Optional, TypedDict
from typing_extensions import NotRequired
from pydantic import Field


class JournalAnalysisState(TypedDict):
    """ジャーナル分析の状態を表すクラス"""
    journal_text: str
    summary: NotRequired[Optional[str]]
    summary_file: NotRequired[Optional[str]]
    discussion_points: NotRequired[Optional[dict]]
    discussion_points_file: NotRequired[Optional[str]]
    research_queries: NotRequired[Optional[dict]]
    queries_file: NotRequired[Optional[str]]
    report_file: NotRequired[Optional[str]] 