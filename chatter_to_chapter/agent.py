"""Chatter to Chapter — ポッドキャスト文字起こしから記事を自動生成するパイプライン。"""

import logging
import os
import time
from typing import Optional

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .prompts import (
    DRAFT_WRITER_INSTRUCTION,
    EPISODE_MINER_INSTRUCTION,
    IMAGE_GENERATOR_INSTRUCTION,
    PUBLISHER_INSTRUCTION,
)
from .tools import generate_hero_image, load_transcript

logger = logging.getLogger(__name__)

# ログ設定（未設定の場合のみ）
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

MODEL = "gemini-2.0-flash-001"

# --- Agent Callbacks ---

# エージェントごとの開始時刻を保持
_agent_start_times: dict[str, float] = {}


def _before_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """エージェント開始時のログ出力。"""
    agent_name = callback_context.agent_name
    _agent_start_times[agent_name] = time.time()
    state_keys = list(callback_context.state.to_dict().keys())
    logger.info(
        "▶ [%s] 開始 | state keys: %s",
        agent_name,
        state_keys,
    )
    return None  # 通常のエージェント実行を継続


def _after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """エージェント完了時のログ出力。"""
    agent_name = callback_context.agent_name
    elapsed = time.time() - _agent_start_times.pop(agent_name, time.time())
    state_keys = list(callback_context.state.to_dict().keys())
    logger.info(
        "✔ [%s] 完了（%.1f秒）| state keys: %s",
        agent_name,
        elapsed,
        state_keys,
    )
    return None  # エージェントのレスポンスをそのまま使用


def _after_transcript_loader(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """TranscriptLoader 完了後、transcript が未設定ならサンプルデータで補完する。"""
    _after_agent(callback_context)

    state_dict = callback_context.state.to_dict()
    if "transcript" not in state_dict or not state_dict.get("transcript"):
        sample_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sample_data",
            "sample_transcript.txt",
        )
        try:
            with open(sample_path, encoding="utf-8") as f:
                callback_context.state["transcript"] = f.read()
            logger.warning(
                "TranscriptLoader が transcript を設定しなかったため、サンプルデータで補完しました"
            )
        except Exception:
            logger.exception("サンプルデータの読み込みに失敗しました")

    return None


# --- Step 1: TranscriptLoader ---
# ユーザー入力から文字起こしテキストを読み込み、state に保存する
transcript_loader = Agent(
    name="TranscriptLoader",
    model=MODEL,
    description="文字起こしテキストを読み込むエージェント",
    instruction="""あなたは文字起こしテキストの読み込みを担当するエージェントです。

【重要】必ず load_transcript ツールを1回呼び出してください。テキストで応答するだけでは不十分です。

ユーザーの入力を確認し、load_transcript ツールを使って文字起こしテキストを読み込んでください。

- ユーザーがファイルパスを指定した場合: そのパスを source に渡す
- ユーザーがテキストを直接入力した場合: そのテキストを source に渡す
- ユーザーが何も指定しない場合: "sample_data/sample_transcript.txt" をデフォルトとして使用

読み込みが完了したら、結果を簡潔に報告してください。
ツールが error ステータスを返した場合は、エラーメッセージをそのまま報告してください。""",
    tools=[load_transcript],
    before_agent_callback=_before_agent,
    after_agent_callback=_after_transcript_loader,
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
    before_agent_callback=_before_agent,
    after_agent_callback=_after_agent,
)

# --- Step 3: DraftWriter ---
# 構造化データから Markdown 記事を生成する
draft_writer = Agent(
    name="DraftWriter",
    model=MODEL,
    description="Markdown 記事を生成するエージェント",
    instruction=DRAFT_WRITER_INSTRUCTION,
    output_key="draft_article",
    before_agent_callback=_before_agent,
    after_agent_callback=_after_agent,
)

# --- Step 4: ImageGenerator ---
# ヒーロー画像を生成する
image_generator = Agent(
    name="ImageGenerator",
    model=MODEL,
    description="記事のヒーロー画像を生成するエージェント",
    instruction=IMAGE_GENERATOR_INSTRUCTION,
    tools=[generate_hero_image],
    before_agent_callback=_before_agent,
    after_agent_callback=_after_agent,
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
    before_agent_callback=_before_agent,
    after_agent_callback=_after_agent,
)

# --- Root Agent: ChatterToChapter Pipeline ---
root_agent = SequentialAgent(
    name="ChatterToChapter",
    description="ポッドキャスト文字起こしから月刊記事を自動生成するパイプライン。TranscriptLoader → EpisodeMiner → DraftWriter → ImageGenerator → Publisher の順で処理します。",
    sub_agents=[
        transcript_loader,
        episode_miner,
        draft_writer,
        image_generator,
        publisher,
    ],
)
