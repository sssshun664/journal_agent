from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from models import TopicStructure

class TopicExtractor:
    def __init__(
        self,
        llm: ChatGoogleGenerativeAI,
    ):
        """TopicExtractorの初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm.with_structured_output(TopicStructure)

    def run(self, journal_text: str) -> TopicStructure:
        # プロンプトテンプレートの作成
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "あなたは7日分のSlackログから、重要なトピックと関連情報を抽出する分析官です。"
            ),
            (
                "human",
                "以下のログから、重要なトピックと関連情報を抽出してください。\n"
                "要件:\n"
                "1. トピックとキーワードの抽出:\n"
                "   - メインとなる議論や話題を特定する\n"
                "   - 各トピックに関連する重要なキーワードを抽出する\n"
                "   - トピックの重要度を0.0-1.0のスコアで評価する\n\n"
                "2. 文脈の理解:\n"
                "   - 議論の流れや背景を簡潔に説明する\n"
                "   - 技術的な用語や概念の関連性を整理する\n"
                "   - 参加者の関心事や論点を把握する\n\n"
                "3. 注意事項:\n"
                "   - 個人情報や機密情報は抽象化すること\n"
                "   - 技術的な議論は具体的に捉えること\n"
                "   - 表層的なキーワードだけでなく、議論の本質を掴むこと\n\n"
                "ログ内容:\n{input}"
            )
        ])
        
        # チェーンの実行
        chain = prompt | self.llm
        return chain.invoke({"input": journal_text})