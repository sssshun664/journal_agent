from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.utils.file_handler import save_json
from src.models.states import DiscussionPoints
import logging

logger = logging.getLogger(__name__)


class DiscussionPointsOutput(BaseModel):
    """ディスカッションポイント抽出の出力形式"""
    points: list[str] = Field(..., description="抽出されたディスカッションポイント（2-3個）")
    context: str = Field(..., description="ディスカッションの背景や文脈")


class DiscussionExtractor:
    """要約からディスカッションポイントを抽出するノード"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm
        self.output_parser = JsonOutputParser(pydantic_object=DiscussionPointsOutput)
        self.system_prompt = """
あなたは、要約テキストから重要なディスカッションポイントを抽出するエキスパートです。
以下の点に注意して、2-3個の重要なディスカッションポイントを抽出してください：

【抽出の方針】
1. 以下のような観点を重視
   - 技術的な議論や検討事項
   - 意見の対立がある論点
   - 未解決の課題
   - 将来の展望に関する議論
   - 新しい発見や気づき

2. 各ポイントの選定基準
   - 具体的な事実や意見が含まれている
   - 深掘りして調査する価値がある
   - チームにとって重要な示唆がある
   - 今後のアクションにつながる

3. 出力形式
   - points: 抽出されたポイントのリスト（2-3個）
   - context: ポイントの背景や文脈の説明

【出力例】
{{
    "points": [
        "アイコンとラベルを組み合わせたボタンのUX設計について、具体的なユーザビリティ調査の必要性が指摘された",
        "AIモデルの推論速度と精度のトレードオフに関して、実務での最適なバランスを検討する必要がある"
    ],
    "context": "チームのUI/UX改善とAI実装における実践的な課題について、具体的なユースケースを交えた議論が行われた"
}}

上記の形式で、提供された要約からディスカッションポイントを抽出してください。
"""

    def run(self, summary: str) -> Dict[str, Any]:
        """ディスカッションポイントを抽出する
        
        Args:
            summary: 要約テキスト
            
        Returns:
            Dict[str, Any]: 抽出されたポイントとファイルパス
        """
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "以下の要約からディスカッションポイントを抽出してください：\n\n{summary}")
        ])
        
        # チェーンの構築と実行
        chain = prompt | self.llm | self.output_parser
        
        try:
            # ポイントの抽出
            result = chain.invoke({"summary": summary})
            logger.info("Successfully extracted discussion points")
            
            # DiscussionPointsモデルの作成
            discussion_points = DiscussionPoints(
                points=result["points"],
                context=result["context"]
            )
            
            # JSONとして保存
            points_file = save_json(
                content=discussion_points.model_dump(),
                directory="outputs/discussion_points"
            )
            
            return {
                "discussion_points": discussion_points.model_dump(),
                "discussion_points_file": points_file
            }
            
        except Exception as e:
            logger.error(f"Failed to extract discussion points: {str(e)}")
            raise 