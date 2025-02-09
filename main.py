import logging
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pathlib import Path
from dotenv import load_dotenv

from src.config import get_model, get_tools
from src.journal_analysis_graph import JournalAnalysisGraph
from src.utils.slack import get_slack_messages

logger = logging.getLogger(__name__)

def setup_logging():
    """ロギングの設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """メイン処理"""
    # 環境変数の読み込み
    load_dotenv()
    
    # ロギングの設定
    setup_logging()
    
    # モデルとツールの取得
    llm = get_model()
    tools = get_tools()
    
    # グラフの初期化
    graph = JournalAnalysisGraph(llm=llm, tools=tools)
    
    # Slackメッセージの取得
    journal_text = get_slack_messages()
    
    # グラフの実行
    final_state = graph.invoke(
        journal_text=journal_text,
        debug=True
    )
    
    # 結果の確認
    if final_state.get("report_file"):
        logger.info("Successfully completed journal analysis")
    else:
        logger.error("Failed to complete journal analysis")

if __name__ == "__main__":
    main() 