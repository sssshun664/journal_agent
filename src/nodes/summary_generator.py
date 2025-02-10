from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.file_handler import save_markdown
import logging

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Slackログを要約するノード"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm
        self.system_prompt = """
あなたは、Slackのログを分析し、重要なディスカッションポイントを中心に要約するエキスパートです。
以下の点に注意して、約1000文字の要約を生成してください：

【要約の方針】
1. ディスカッションの内容を重視
   - 意見の対立点
   - 新しい発見や気づき
   - 技術的な議論のポイント
   - 将来の展望に関する議論

2. 重要な文脈を保持
   - 議論の背景
   - 参加者の関心事
   - 未解決の課題
   - 今後の検討事項

3. 出力形式
   - Markdown形式で出力
   - 箇条書きを適切に使用
   - セクションを明確に分ける
   - コードブロックは保持

【出力例】
# 週間ディスカッション要約

## 主要な議論
- トピックA
  - 賛成意見：...
  - 反対意見：...
  - 未解決の点：...

## 技術的な検討事項
- 課題1
  - 現状：...
  - 提案された解決策：...
  - 検討が必要な点：...

## 今後の展望
- 短期的な目標
- 長期的な検討事項
- 必要なリソース

上記の形式を参考に、提供されたSlackログを要約してください。
"""

    def run(self, journal_text: str) -> Dict[str, Any]:
        """要約を生成する
        
        Args:
            journal_text: Slackログのテキスト
            
        Returns:
            Dict[str, Any]: 生成された要約とファイルパス
        """
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "以下のSlackログを要約してください：\n\n{text}")
        ])
        
        # チェーンの構築と実行
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            # 要約の生成
            summary = chain.invoke({"text": journal_text})
            logger.info("Successfully generated summary")
            
            # 要約の保存
            summary_file = save_markdown(
                content=summary,
                directory="outputs/summaries"
            )
            
            return {
                "summary": summary,
                "summary_file": summary_file
            }
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise 