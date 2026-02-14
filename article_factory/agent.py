"""Article Factory — ポッドキャスト文字起こしから月刊記事を自動生成するパイプライン。"""

from google.adk.agents import Agent, SequentialAgent

from .prompts import (
    DRAFT_WRITER_INSTRUCTION,
    EPISODE_MINER_INSTRUCTION,
    PUBLISHER_INSTRUCTION,
)
from .tools import generate_hero_image, load_transcript

MODEL = "gemini-2.0-flash-001"

# --- Step 1: TranscriptLoader ---
# ユーザー入力から文字起こしテキストを読み込み、state に保存する
transcript_loader = Agent(
    name="TranscriptLoader",
    model=MODEL,
    description="文字起こしテキストを読み込むエージェント",
    instruction="""あなたは文字起こしテキストの読み込みを担当するエージェントです。

ユーザーの入力を確認し、load_transcript ツールを使って文字起こしテキストを読み込んでください。

- ユーザーがファイルパスを指定した場合: そのパスを source に渡す
- ユーザーがテキストを直接入力した場合: そのテキストを source に渡す
- ユーザーが何も指定しない場合: "sample_data/sample_transcript.txt" をデフォルトとして使用

読み込みが完了したら、結果を簡潔に報告してください。""",
    tools=[load_transcript],
    # NOTE: output_key を使わない。ツールが直接 state["transcript"] を設定するため。
)

# --- Step 2: EpisodeMiner ---
# 文字起こしから構造化データを抽出する
episode_miner = Agent(
    name="EpisodeMiner",
    model=MODEL,
    description="ポッドキャストエピソードの構造データを抽出するエージェント",
    instruction=EPISODE_MINER_INSTRUCTION,
    output_key="episode_data",
)

# --- Step 3: DraftWriter ---
# 構造化データから Markdown 記事を生成する
draft_writer = Agent(
    name="DraftWriter",
    model=MODEL,
    description="Markdown 記事を生成するエージェント",
    instruction=DRAFT_WRITER_INSTRUCTION,
    output_key="draft_article",
)

# --- Step 4: ImageGenerator ---
# ヒーロー画像を生成する
image_generator = Agent(
    name="ImageGenerator",
    model=MODEL,
    description="記事のヒーロー画像を生成するエージェント",
    instruction="""あなたは記事のヒーロー画像の生成を担当するエージェントです。

以下のドラフト記事の内容を読み、記事のテーマに合ったヒーロー画像を生成してください。

## ドラフト記事
{draft_article}

## タスク
1. 記事のテーマを分析し、適切な画像プロンプトを英語で作成
2. generate_hero_image ツールを使って画像を生成
3. 結果を報告

## プロンプト作成のコツ
- 英語で記述（Imagen は英語プロンプトが最も高品質）
- 具体的でビジュアルな描写を含める
- ポッドキャスト / テクノロジー / コミュニケーションに関連する要素を入れる
- 480トークン以内に収める""",
    tools=[generate_hero_image],
    # NOTE: output_key を使わない。ツールが直接 state["hero_image_url"] を設定するため。
)

# --- Step 5: Publisher ---
# 最終記事を仕上げる
publisher = Agent(
    name="Publisher",
    model=MODEL,
    description="最終記事を仕上げるエージェント",
    instruction=PUBLISHER_INSTRUCTION,
    output_key="final_article",
)

# --- Root Agent: ArticleFactory Pipeline ---
root_agent = SequentialAgent(
    name="ArticleFactory",
    description="ポッドキャスト文字起こしから月刊記事を自動生成するパイプライン。TranscriptLoader → EpisodeMiner → DraftWriter → ImageGenerator → Publisher の順で処理します。",
    sub_agents=[
        transcript_loader,
        episode_miner,
        draft_writer,
        image_generator,
        publisher,
    ],
)
