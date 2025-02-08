from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from models import WeeklyReportState, TopicStructure
from topic_extractor import TopicExtractor
from query_optimizer import QueryOptimizer
from search_executor import SearchExecutor
from report_generator import ReportGenerator


class WeeklyReportGraph:
    def __init__(
        self,
        llm: ChatGoogleGenerativeAI,
        tools: list
    ):
        self.topic_extractor = TopicExtractor(llm=llm)
        self.query_optimizer = QueryOptimizer(llm=llm)
        self.search_executor = SearchExecutor(tools=tools)
        self.report_generator = ReportGenerator(llm=llm)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        graph = StateGraph(WeeklyReportState)
        
        # ノードの追加
        graph.add_node("topic_extractor", self._extract_topics)
        graph.add_node("query_optimizer", self._optimize_queries)
        graph.add_node("search_executor", self._execute_search)
        graph.add_node("report_generator", self._generate_report)

        # エントリーポイントの設定
        graph.set_entry_point("topic_extractor")

        # エッジの追加
        graph.add_edge("topic_extractor", "query_optimizer")
        graph.add_edge("query_optimizer", "search_executor")
        graph.add_edge("search_executor", "report_generator")
        graph.add_edge("report_generator", END)

        return graph.compile()

    def _extract_topics(self, state: WeeklyReportState) -> Dict[str, Any]:
        """トピック抽出ノード"""
        extracted_topics = self.topic_extractor.run(
            journal_text=state.journal_text
        )
        # extracted_topicsをdictに変換して返す
        return {
            "extracted_topics": extracted_topics.dict()
        }

    def _optimize_queries(self, state: WeeklyReportState) -> Dict[str, Any]:
        """クエリ最適化ノード"""
        optimized_queries = self.query_optimizer.run(
            topics=state.extracted_topics
        )
        return {
            "search_queries": optimized_queries.text
        }

    def _execute_search(self, state: WeeklyReportState) -> Dict[str, Any]:
        """検索実行ノード"""
        search_results = self.search_executor.run(
            queries=state.search_queries
        )
        return {
            "search_results": search_results
        }

    def _generate_report(self, state: WeeklyReportState) -> Dict[str, Any]:
        """レポート生成ノード"""
        final_report = self.report_generator.run(
            journal_text=state.journal_text,
            topics=state.extracted_topics,
            search_results=state.search_results
        )
        return {
            "final_report": final_report
        }

    def invoke(self, journal_text: str, debug: bool = False) -> str:
        """グラフの実行"""
        initial_state = WeeklyReportState(journal_text=journal_text)
        final_state = self.graph.invoke(initial_state)
        return final_state["final_report"]