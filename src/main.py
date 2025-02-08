import os
from pathlib import Path
from config import get_model, get_tools
from weekly_report_graph import WeeklyReportGraph

def main():
    # データディレクトリのパス設定
    data_dir = Path(__file__).parent.parent / "data"
    sample_log_path = data_dir / "sample_log.txt"

    # モデルとツールの初期化
    llm = get_model()
    tools = get_tools()
    
    # グラフの初期化
    graph = WeeklyReportGraph(llm=llm, tools=tools)
    
    # Mermaidグラフの出力
    mermaid = graph.graph.get_graph().draw_mermaid()
    print("\n=== Graph Structure (Mermaid) ===")
    print(mermaid)
    
    # サンプルログの読み込み
    with open(sample_log_path, "r", encoding="utf-8") as f:
        journal_text = f.read()
    
    print("\n=== Executing Graph with Debug Mode ===")
    # デバッグモードでレポート生成を実行
    report = graph.invoke(
        journal_text,
        debug=True  # デバッグモードを有効化
    )
    
    print("\n=== Generated Report ===")
    print(report)

    # 必要に応じてPNG出力
    # from IPython.display import Image, display
    # display(Image(graph.graph.get_graph().draw_mermaid_png()))


if __name__ == "__main__":
    main()