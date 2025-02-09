from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from .states import JournalAnalysisState
from .nodes.summary_generator import SummaryGenerator
from .nodes.discussion_extractor import DiscussionExtractor
from .nodes.query_generator import QueryGenerator
from .utils.file_handler import save_final_report
from .utils.slack import send_to_slack
import logging

logger = logging.getLogger(__name__)


class JournalAnalysisGraph:
    """ジャーナル分析のグラフを管理するクラス"""
    
    def __init__(
        self,
        llm: ChatGoogleGenerativeAI,
        tools: list
    ):
        """初期化
        
        Args:
            llm: Gemini-1.5-proモデル
            tools: 使用するツールのリスト（現在は未使用）
        """
        # ノードの初期化
        self.summary_generator = SummaryGenerator(llm=llm)
        self.discussion_extractor = DiscussionExtractor(llm=llm)
        self.query_generator = QueryGenerator(llm=llm)
        
        # グラフの構築
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        """グラフを構築する"""
        # グラフの初期化
        graph = StateGraph(JournalAnalysisState)
        
        # ノードの追加
        graph.add_node("generate_summary", self._generate_summary)
        graph.add_node("extract_discussion", self._extract_discussion)
        graph.add_node("generate_query", self._generate_queries)
        graph.add_node("create_report", self._create_report)
        
        # エントリーポイントの設定
        graph.set_entry_point("generate_summary")
        
        # エッジの追加（直線的なフロー）
        graph.add_edge("generate_summary", "extract_discussion")
        graph.add_edge("extract_discussion", "generate_query")
        graph.add_edge("generate_query", "create_report")
        graph.add_edge("create_report", END)
        
        return graph.compile()
    
    def _generate_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """要約生成ノード"""
        result = self.summary_generator.run(state["journal_text"])
        return {
            "summary": result["summary"],
            "summary_file": result["summary_file"]
        }
    
    def _extract_discussion(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """ディスカッションポイント抽出ノード"""
        result = self.discussion_extractor.run(state["summary"])
        return {
            "discussion_points": result["discussion_points"],
            "discussion_points_file": result["discussion_points_file"]
        }
    
    def _generate_queries(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """クエリ生成ノード"""
        result = self.query_generator.run(state["discussion_points"])
        return {
            "research_queries": result["research_queries"],
            "queries_file": result["queries_file"]
        }
    
    def _create_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """最終レポートを作成する"""
        report_file = save_final_report(
            summary=state["summary"],
            discussion_points=state["discussion_points"],
            research_queries=state["research_queries"]
        )
        
        # レポートの内容を読み込む
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # Slackに送信
        slack_result = send_to_slack(report_content)
        
        return {
            **state,
            "report_file": report_file,
            "slack_success": slack_result["success"]
        }
    
    def invoke(
        self,
        journal_text: str,
        debug: bool = False
    ) -> JournalAnalysisState:
        """グラフを実行する
        
        Args:
            journal_text: 分析対象のSlackログ
            debug: デバッグモードを有効にするかどうか
            
        Returns:
            JournalAnalysisState: 最終的な状態
        """
        # 初期状態の作成
        initial_state = JournalAnalysisState(journal_text=journal_text)
        
        try:
            # グラフの実行
            final_state = self.graph.invoke(initial_state)
            
            if debug:
                logger.info("=== Debug Information ===")
                logger.info(f"Summary File: {final_state.get('summary_file')}")
                logger.info(f"Discussion Points File: {final_state.get('discussion_points_file')}")
                logger.info(f"Queries File: {final_state.get('queries_file')}")
                logger.info(f"Final Report: {final_state.get('report_file')}")
                logger.info(f"Slack Delivery: {'Success' if final_state.get('slack_success') else 'Failed'}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Failed to execute graph: {str(e)}")
            raise 