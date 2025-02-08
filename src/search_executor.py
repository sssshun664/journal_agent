from typing import List
from langchain_core.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults


class SearchExecutor:
    def __init__(self, tools: List[BaseTool]):
        """SearchExecutorの初期化
        
        Args:
            tools: 使用するツールのリスト（Tavily Search）
        """
        self.search_tool = next(
            tool for tool in tools 
            if isinstance(tool, TavilySearchResults)
        )

    def run(self, queries: List[str]) -> List[str]:
        """検索クエリのリストを実行し、結果を返す
        
        Args:
            queries: 最適化された検索クエリのリスト
            
        Returns:
            List[str]: 各クエリに対する検索結果のリスト
        """
        search_results = []
        
        for query in queries:
            try:
                # Tavily Searchを実行
                result = self.search_tool.invoke(query)
                # 検索結果をフォーマット
                formatted_result = (
                    f"検索クエリ: {query}\n"
                    f"検索結果:\n{result}"
                )
                search_results.append(formatted_result)
            except Exception as e:
                # エラー時は検索失敗を記録
                search_results.append(
                    f"検索クエリ: {query}\n"
                    f"検索失敗: {str(e)}"
                )
                continue
                
        return search_results