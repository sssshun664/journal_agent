from typing import Annotated, List
import operator
from pydantic import BaseModel, Field


class TopicStructure(BaseModel):
    """抽出されたトピック情報の構造"""
    main_topics: List[str] = Field(..., description="主要なトピックのリスト")
    keywords: List[str] = Field(..., description="関連キーワードのリスト")
    importance_scores: List[float] = Field(..., description="各トピックの重要度スコア")
    context: str = Field(..., description="議論の文脈や背景")


class WeeklyReportState(BaseModel):
    """週次レポート生成のための状態管理"""
    
    # Input
    journal_text: str = Field(..., description="7日分のSlackログ")
    
    # TopicExtractor Output
    extracted_topics: TopicStructure = Field(
        default=None, 
        description="抽出されたトピックと関連情報"
    )
    
    # QueryOptimizer Output
    search_queries: List[str] = Field(
        default_factory=list,
        description="最適化された検索クエリ"
    )
    
    # SearchExecutor Output
    search_results: Annotated[List[str], operator.add] = Field(
        default_factory=list,
        description="検索結果"
    )
    
    # ReportGenerator Output
    final_report: str = Field(
        default="",
        description="最終レポート"
    )