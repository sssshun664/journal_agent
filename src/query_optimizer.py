from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from models import TopicStructure


class OptimizedQueries(BaseModel):
    """最適化された検索クエリのリスト"""
    queries: List[str] = Field(
        ...,
        description="検索用に最適化されたクエリのリスト",
        min_items=1,
        max_items=3
    )

    @property
    def text(self) -> List[str]:
        return self.queries


class QueryOptimizer:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """QueryOptimizerの初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm.with_structured_output(OptimizedQueries)

    def run(self, topics: TopicStructure) -> OptimizedQueries:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "あなたは抽出されたトピック情報から、効果的な検索クエリを生成するスペシャリストです。"
            ),
            (
                "human",
                "以下のトピック情報から、効果的な検索クエリを生成してください。\n"
                "要件:\n"
                "1. 検索クエリの最適化:\n"
                "   - 各トピックの本質を捉えた検索キーワードの組み合わせを作成\n"
                "   - 重要度スコアの高いトピックを優先\n"
                "   - 一般的すぎる単語や曖昧な表現を避ける\n\n"
                "2. 検索の範囲:\n"
                "   - 技術トレンド、事例、市場動向など、多角的な情報収集が可能なクエリ\n"
                "   - 文脈に応じて、時期や地域を限定するキーワードを含める\n\n"
                "3. クエリ生成のルール:\n"
                "   - 1〜3個のクエリを生成\n"
                "   - 各クエリは検索エンジンで効果的な結果が得られる長さと形式\n"
                "   - 個人情報や機密情報を含まない\n\n"
                "トピック情報:\n"
                "主要トピック: {main_topics}\n"
                "関連キーワード: {keywords}\n"
                "重要度スコア: {importance_scores}\n"
                "議論の文脈: {context}"
            )
        ])
        
        # チェーンの実行
        chain = prompt | self.llm
        return chain.invoke({
            "main_topics": topics.main_topics,
            "keywords": topics.keywords,
            "importance_scores": topics.importance_scores,
            "context": topics.context
        })