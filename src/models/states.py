from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DiscussionPoints(BaseModel):
    """ディスカッションポイントの構造"""
    points: List[str] = Field(..., description="抽出されたディスカッションポイント")
    context: Optional[str] = Field(None, description="追加のコンテキスト情報")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成時のタイムスタンプ")


class ResearchQueries(BaseModel):
    """リサーチクエリの構造"""
    queries: List[dict] = Field(..., description="生成されたリサーチクエリ")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成時のタイムスタンプ")

    class Config:
        json_schema_extra = {
            "example": {
                "queries": [
                    {
                        "discussion_point": "UXデザインに関する議論",
                        "research_query": "Find evidence that shows..."
                    }
                ]
            }
        }


class JournalAnalysisState(BaseModel):
    """ジャーナル分析の状態管理"""
    
    # Input
    journal_text: str = Field(..., description="分析対象のSlackログ")
    
    # SummaryNode Output
    summary: Optional[str] = Field(None, description="生成された要約")
    summary_file: Optional[str] = Field(None, description="要約が保存されたファイルパス")
    
    # DiscussionPointNode Output
    discussion_points: Optional[dict] = Field(None, description="抽出されたディスカッションポイント")
    discussion_points_file: Optional[str] = Field(None, description="ディスカッションポイントが保存されたファイルパス")
    
    # QueryGeneratorNode Output
    research_queries: Optional[dict] = Field(None, description="生成されたリサーチクエリ")
    queries_file: Optional[str] = Field(None, description="クエリが保存されたファイルパス")
    
    # Final Output
    report_file: Optional[str] = Field(None, description="最終レポートが保存されたファイルパス")
    slack_success: bool = Field(default=False, description="Slackへの送信が成功したかどうか")

    class Config:
        """設定クラス"""
        json_schema_extra = {
            "example": {
                "journal_text": "Slackログのテキスト...",
                "summary": "要約テキスト...",
                "summary_file": "summaries/summary_20240209.md",
                "discussion_points": {
                    "points": ["ポイント1", "ポイント2"],
                    "context": "追加コンテキスト"
                },
                "research_queries": {
                    "queries": [
                        {
                            "discussion_point": "ポイント1",
                            "research_query": "リサーチクエリ1"
                        }
                    ]
                }
            }
        } 