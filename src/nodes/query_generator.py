from typing import Any, Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.utils.file_handler import save_json
from src.models.states import ResearchQueries, DiscussionPoints
import logging

logger = logging.getLogger(__name__)


class QueryGeneratorOutput(BaseModel):
    """クエリ生成の出力形式"""
    queries: List[Dict[str, str]] = Field(..., description="生成されたリサーチクエリ")

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


class QueryGenerator:
    """ディスカッションポイントからリサーチクエリを生成するノード"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm
        self.output_parser = JsonOutputParser(pydantic_object=QueryGeneratorOutput)
        self.system_prompt = """
あなたは、ディスカッションポイントから効果的なリサーチクエリを生成するエキスパートです。
以下の点に注意して、各ディスカッションポイントに対応するリサーチクエリを生成してください：

【クエリ生成の方針】
1. クエリの特徴
   - 英語で記述（より広範な情報収集のため）
   - 約300文字以内
   - 具体的で明確な問いかけ
   - 事実やエビデンスを求める形式

2. 含めるべき要素
   - 具体的な調査対象
   - 求める情報の種類（例：事例、統計、研究結果）
   - 比較や評価の基準
   - 時間的な範囲（必要な場合）

3. 出力形式
   - queries: リサーチクエリのリスト
   - 各クエリは以下の要素を含む
     - discussion_point: 元となったディスカッションポイント
     - research_query: 生成されたリサーチクエリ（英語）

【出力例】
{{
    "queries": [
        {{
            "discussion_point": "アイコンとラベルを組み合わせたボタンのUX設計について、具体的なユーザビリティ調査の必要性が指摘された",
            "research_query": "Find evidence that shows whether buttons with icons & labels are more usable than buttons without labels, or labels without icons. Include recent user studies, detailed reports, and definitive answers on effectiveness. Focus on mobile and web applications from the last 5 years."
        }}
    ]
}}

上記の形式で、提供されたディスカッションポイントからリサーチクエリを生成してください。
"""

    def run(self, discussion_points: Dict[str, Any]) -> Dict[str, Any]:
        """リサーチクエリを生成する
        
        Args:
            discussion_points: 抽出されたディスカッションポイント
            
        Returns:
            Dict[str, Any]: 生成されたクエリとファイルパス
        """
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """以下のディスカッションポイントから、リサーチクエリを生成してください。
必ず以下のJSON形式で出力してください：

{{
    "queries": [
        {{
            "discussion_point": "ディスカッションポイントの内容",
            "research_query": "生成されたリサーチクエリ（英語）"
        }}
    ]
}}

【ディスカッションポイント】
{points}

【コンテキスト】
{context}""")
        ])
        
        # チェーンの構築と実行
        chain = prompt | self.llm | self.output_parser
        
        try:
            # クエリの生成
            result = chain.invoke({
                "points": "\n".join(f"- {p}" for p in discussion_points["points"]),
                "context": discussion_points["context"]
            })
            logger.info("Successfully generated research queries")
            
            # ResearchQueriesモデルの作成
            research_queries = ResearchQueries(
                queries=result["queries"]
            )
            
            # JSONとして保存
            queries_file = save_json(
                content=research_queries.model_dump(),
                directory="outputs/queries"
            )
            
            return {
                "research_queries": research_queries.model_dump(),
                "queries_file": queries_file
            }
            
        except Exception as e:
            logger.error(f"Failed to generate research queries: {str(e)}")
            raise 