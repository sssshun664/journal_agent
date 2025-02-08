# Weekly Report Generator

Slackチャンネルの7日間のログから、キャラクター性のある週次レポートを自動生成するLangGraphベースのシステム。

## Features

- トピック抽出：重要な議論やキーワードを自動抽出
- 情報補完：Tavily Searchによる関連情報の収集
- キャラクター性：エッジの効いた視点と親しみやすい文体
- LangGraph活用：安定した状態管理とワークフロー制御

## Installation

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/weekly-report-generator.git
cd weekly-report-generator
```

2. 環境構築
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 環境変数の設定
`.env`ファイルを作成し、必要なAPIキーを設定：
```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Usage

1. データの準備
`data/sample_log.txt`にSlackログを配置

2. 実行
```bash
python src/main.py
```

## Project Structure

- `src/`: ソースコード
  - `models.py`: データモデル定義
  - `topic_extractor.py`: トピック抽出モジュール
  - `query_optimizer.py`: 検索クエリ最適化
  - `search_executor.py`: 検索実行
  - `report_generator.py`: レポート生成
  - `weekly_report_graph.py`: LangGraphワークフロー
  - `main.py`: エントリーポイント