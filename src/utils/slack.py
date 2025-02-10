import os
import requests
from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def send_to_slack(content: str) -> Dict[str, Any]:
    """レポートをSlackに送信する
    
    Args:
        content: 送信するレポートの内容
        
    Returns:
        Dict[str, Any]: レスポンス情報を含む辞書
        
    Raises:
        ValueError: SLACK_WEBHOOK_URLが設定されていない場合
        requests.RequestException: Slack APIへのリクエストが失敗した場合
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL is not set in environment variables")
        
    try:
        # Slackメッセージのペイロード作成
        payload = {
            "text": content,
            "mrkdwn": True  # Markdownフォーマットを有効化
        }
        
        # Webhookにリクエスト送信
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        logger.info("Successfully sent report to Slack")
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text
        }
        
    except requests.RequestException as e:
        logger.error(f"Failed to send report to Slack: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_slack_messages() -> str:
    """サンプルのSlackメッセージを取得する
    
    Returns:
        str: サンプルのSlackメッセージテキスト
    """
    # サンプルログファイルのパスを取得
    data_dir = Path(__file__).parent.parent.parent / "data"
    sample_log_path = data_dir / "sample_log.txt"
    
    # サンプルログを読み込む
    with open(sample_log_path, "r", encoding="utf-8") as f:
        return f.read() 