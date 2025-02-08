import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import List
from langchain_core.tools import BaseTool

def get_model(temperature: float = 0):
    """ChatGoogleGenerativeAI modelの初期化"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

def get_tools() -> List[BaseTool]:
    """使用するツールの設定"""
    return [TavilySearchResults(max_results=3)]

def setup_tracing():
    """LangSmithのトレース設定"""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "journal_agent"