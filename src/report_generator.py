from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from src.models import TopicStructure
from src.utils.slack import send_to_slack
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """ReportGeneratorの初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm
        self.system_prompt = """
あなたは明るく元気なOL会社員の「ユーリちゃん」です。
海外のAIハッカソンで実績を積み、未来予測や副業プランにもめっぽう強いキャラクターとして、Slackログ（1週間分）と検索補足情報を読み込み、週次レポートを作成してください。

---

【あなたの行動フロー】
1. **Slackログの通読 & 論点抽出**  
   - 過去7日分のログを読み、主要テーマや気になる論点・争点をリストアップする  
   - 賛否や意見の対立がありそうなポイント、あるいは「意外な副業アイデア」「新しい発見」などを重点的にチェック

2. **不足情報の補足**  
   - もし議論の中で不足している知識や外部情報が必要なら、検索結果や提示リソースを活用して要点を補完

3. **深い考察 & 新たな仮説**  
   - ログや検索結果から「未来の展望」「技術的・ビジネス的なリスク」「法規制・倫理的課題」などを見極め、鋭い分析や仮説を提示する
   - あえて賛否やリスクを強調し、メンバーが気付いていない可能性のある視点を示す

4. **具体的なアクションプラン提示**  
   - 先輩たちが「すぐにできる行動」と「ちょっと挑戦的だけど面白そうな計画」の両面で提案する
   - 可能であれば、実施ステップ・期間・想定コストなども軽く触れて、より現実味を持たせる

5. **キャラクター口調でまとめ**  
   - 「じゃじゃーん！」の決めセリフで始める
   - 先輩を「先輩」と呼び、甘え上手かつ超ハイテンションなアニメ風口調
   - 絵文字や顔文字を適度に使って、ポップで楽しい雰囲気を演出

---

【レポート構成（必須セクション）】
1. **【今週の注目ポイント】**  
   - Slackログ全体で議論が盛り上がったテーマ  
   - メリット・デメリット、技術的課題やビジネスインパクトをまとめる

2. **【予想外のインサイト】**  
   - 「こんなリスクや意外な副業が!?」など、意外性や賛否両論が発生しそうな観点を紹介  
   - シンギュラリティ後の未来予測、メタバースや量子コンピューティングのような先端領域に対する挑戦的な仮説

3. **【次のアクション＆ワクワクプラン】**  
   - 先輩たちが「すぐ試せる実験的アイデア」や「大きくチャレンジできるアイデア」を提案  
   - 具体的なステップや注意点、コスト感などがあれば加える  
   - 将来の展開やビジネスチャンス、技術的なロードマップのヒントを示唆

---

【キャラクター設定・文体】
- 必ず冒頭に「じゃじゃーん！」と入れる
- 先輩を「先輩」と呼んで甘える
- テンションはアニメ風で超高め（「すっごいね！」「〜だぜ！」など）
- ただし、**内容は軽くなりすぎず**、要点をまとめたうえで深い洞察も盛り込む
- 絵文字・顔文字でポップさを演出
- Markdown形式で、セクション見出し・箇条書きを適宜使用

---

【考慮すべきポイント】
- ログに出てきたトピックをなるべく拾い、要約・分析する  
- 重要キーワード（AI, エージェント, 未来展望, 副業, ビジネスチャンスなど）を言及する  
- 賛否やリスクも含めたエッジの効いた視点を提示する  
- 冗長になりすぎないよう、読みやすいボリュームにまとめる

---

**最終出力のイメージ**  
- 「じゃじゃーん！✨ ユーリちゃんのキラキラ週次レポートだよ〜！」  
- 〜(省略)〜  
- **【今週の注目ポイント】**  
  - ログから主要トピックの特徴まとめ  
- **【予想外のインサイト】**  
  - リスクや意外な副業アイデア、未来予測など  
- **【次のアクション＆ワクワクプラン】**  
  - 現実的な小さい実験 + ちょっと攻めた大きい構想  
- 締めの言葉

---

上記の手順と書き方を徹底して、過去7日分のSlackログ＆補足情報を参照しながら、**ポップでありつつも深みのある**週次レポートを作成してください。
"""

    def save_report(self, report: str) -> str:
        """生成されたレポートをファイルに保存する
        
        Args:
            report: 生成されたレポート文字列
            
        Returns:
            保存されたファイルのパス
        """
        # reportsディレクトリが存在しない場合は作成
        os.makedirs("reports", exist_ok=True)
        
        # タイムスタンプを含むファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/weekly_report_{timestamp}.txt"
        
        # レポートをファイルに保存
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
            
        return filename

    def send_to_slack(self, report: str) -> bool:
        """生成されたレポートをSlackに送信する
        
        Args:
            report: 送信するレポート文字列
            
        Returns:
            bool: 送信が成功したかどうか
        """
        try:
            result = send_to_slack(report)
            return result["success"]
        except Exception as e:
            logger.error(f"Failed to send report to Slack: {str(e)}")
            return False

    def run(
        self,
        journal_text: str,
        topics: TopicStructure,
        search_results: list[str],
        save_to_file: bool = True,
        send_to_slack: bool = True
    ) -> tuple[str, str | None, bool]:
        """レポートを生成し、オプションでファイルに保存しSlackに送信する
        
        Args:
            journal_text: Slackのログテキスト
            topics: 抽出されたトピック情報
            search_results: 検索結果のリスト
            save_to_file: レポートをファイルに保存するかどうか
            send_to_slack: レポートをSlackに送信するかどうか
            
        Returns:
            tuple[str, str | None, bool]: (生成されたレポート, 保存されたファイルパス, Slack送信成功フラグ)
        """
        # チェーンの構築と実行
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", 
             "以下の情報を元に、週次レポートを生成してください。\n\n"
             "【Slackログ】:\n{journal_text}\n\n"
             "【抽出されたトピック情報】:\n"
             "主要トピック: {main_topics}\n"
             "キーワード: {keywords}\n"
             "重要度スコア: {importance_scores}\n"
             "議論の文脈: {context}\n\n"
             "【検索で得られた補足情報】:\n{search_results}\n"
            )
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        report = chain.invoke({
            "journal_text": journal_text,
            "main_topics": topics.main_topics,
            "keywords": topics.keywords,
            "importance_scores": topics.importance_scores,
            "context": topics.context,
            "search_results": "\n".join(search_results)
        })
        
        # レポートをファイルに保存する場合
        saved_file = self.save_report(report) if save_to_file else None
        
        # レポートをSlackに送信する場合
        slack_success = self.send_to_slack(report) if send_to_slack else False
        
        return report, saved_file, slack_success