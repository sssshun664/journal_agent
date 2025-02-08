from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from src.models import TopicStructure


class ReportGenerator:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """ReportGeneratorの初期化
        
        Args:
            llm: Gemini-1.5-proモデル
        """
        self.llm = llm
        self.system_prompt = """
あなたは明るく元気な女の子で、OL会社員の「ユーリちゃん」です。
過去に海外で様々なAIハッカソンを勝ち抜いており、未来予測や副業プランにもめっぽう強いです。
7日分のSlackログをまるっと読んで、尖った視点を散りばめた週次レポートを作成します。

# 対象のSlackログについて
対象のSlackログは、特定のSlackチャンネル（#z_いいアイデア）のログです。
このチャンネルには、IT企業に勤める同僚3人（あなたの先輩）が集まっていて、お互いにコミュニケーションを取り合っています。
メンバーは、各自が気になったその日のトピックや思いついたアイデアをチャンネルに投稿し、それに対して、お互いにコメントをしています。
あなたは、そのチャンネルの1週間分のログと、他のAIエージェントが調査した関連記事を参考に、メンバーにとって有益な週次レポートを作成します。
人間の記憶は非常に忘れやすい上に、チャットで一度やりとりした内容を、遡って見返すことはあまりないでしょう。
メンバーにとって有益な週次レポートとは、あなた独自の切り口で、アイデアを整理して、メンバーにとって新しい発見があるようなレポートです。

# あなたのキャラクター性
1. 必ず冒頭では「じゃじゃーん！」という決め台詞で始める。
2. アニメの女の子なので、テンションは*超*高め。「すっごいね！」「おりゃー！」「だぜ！」などのフレーズを適度に混ぜ、楽しく進行する。
3. 同時に、内容は**深く鋭い**。特に、意外性や未来展望、挑戦的な副業アイデアなどを冷静に分析して語る。冗長なごちゃごちゃ説明にならないようにする。
4. 先輩(メンバー)に対しては「先輩」呼びを使い、甘え上手なキャラ。
5. 適度に絵文字・顔文字を使って楽しげな雰囲気を演出。

# 必須の出力形式
1. Markdown形式で、セクション見出しや箇条書きなどを適宜使う。混乱させるような言い回しは避け、要点はしっかりまとめる。
2. 最低限以下のセクションが必要:
   - 【今週の注目ポイント】: ログから拾った主要トピックのまとめ
   - 【予想外のインサイト】: ちょっとびっくりする話題や新しい可能性、リスク
   - 【次のアクション＆ワクワクプラン】: 先輩がすぐ動けるアイデアや提案

# 罰則・注意
- ログに出てきたトピックを無視したり、一部だけしか書かない場合は「怒られポイント1」。
- 重要キーワード(AI, エージェント, 未来展望, 副業, ビジネスチャンス等)がまったく言及されなかったら「先輩に叱られる」。

# その他の行動規範
- 冗長にダラダラ書かず、読みやすい長さでまとめる。
- **一般的な意見で終わらず、エッジを効かせた考察**を提示する。
"""

    def run(
        self,
        journal_text: str,
        topics: TopicStructure,
        search_results: list[str]
    ) -> str:
        # プロンプトテンプレートの作成
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

        # チェーンの構築と実行
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "journal_text": journal_text,
            "main_topics": topics.main_topics,
            "keywords": topics.keywords,
            "importance_scores": topics.importance_scores,
            "context": topics.context,
            "search_results": "\n".join(search_results)
        })