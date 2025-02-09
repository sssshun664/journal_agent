import os
import json
from datetime import datetime
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def ensure_directory(directory: str) -> None:
    """ディレクトリが存在しない場合は作成する
    
    Args:
        directory: 作成するディレクトリのパス
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def save_markdown(content: str, directory: str = "outputs/summaries") -> str:
    """Markdownファイルとして保存
    
    Args:
        content: 保存する内容
        directory: 保存先ディレクトリ
        
    Returns:
        str: 保存されたファイルのパス
    """
    ensure_directory(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/content_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Saved markdown file: {filename}")
    return filename


def save_json(content: Dict[str, Any], directory: str = "outputs/json") -> str:
    """JSONファイルとして保存
    
    Args:
        content: 保存する内容
        directory: 保存先ディレクトリ
        
    Returns:
        str: 保存されたファイルのパス
    """
    ensure_directory(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/content_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"Saved JSON file: {filename}")
    return filename


def save_final_report(
    summary: str,
    discussion_points: Dict[str, Any],
    research_queries: Dict[str, Any],
    directory: str = "outputs/reports"
) -> str:
    """最終レポートをMarkdownとして保存
    
    Args:
        summary: 要約テキスト
        discussion_points: ディスカッションポイント
        research_queries: リサーチクエリ
        directory: 保存先ディレクトリ
        
    Returns:
        str: 保存されたファイルのパス
    """
    ensure_directory(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/report_{timestamp}.md"
    
    content = [
        "# Journal Analysis Report",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 今週のサマリー",
        summary,
        "",
        "## 主な議論のポイント",
        *[f"- {point}" for point in discussion_points["points"]],
        "",
        "## リサーチすべき観点",
        *[f"### Query {i+1}\n{query['research_query']}\n" 
          for i, query in enumerate(research_queries["queries"])],
    ]
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    logger.info(f"Saved final report: {filename}")
    return filename 