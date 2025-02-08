import os
import requests
from typing import Dict, Any
import logging

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