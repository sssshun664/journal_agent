import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import List
from langchain_core.tools import BaseTool
import vertexai

def init_vertex_ai():
    """Vertex AI SDKの初期化"""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
    
    # 絶対パスに変換
    abs_credentials_path = os.path.abspath(credentials_path)
    if not os.path.exists(abs_credentials_path):
        raise FileNotFoundError(f"Service account key file not found at: {abs_credentials_path}")
    
    vertexai.init(
        project=project_id,
        location=location,
        credentials=abs_credentials_path
    )

def get_model(temperature: float = 0):
    """ChatVertexAI modelの初期化"""
    init_vertex_ai()  # Vertex AI SDKの初期化
    return ChatVertexAI(
        model="gemini-1.5-pro",
        temperature=temperature,
        max_output_tokens=None,
        top_k=40,
        top_p=0.8,
        max_retries=2
    )

def get_tools() -> List[BaseTool]:
    """使用するツールの設定"""
    return [TavilySearchResults(max_results=3)]

def setup_tracing():
    """LangSmithのトレース設定"""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "journal_agent"