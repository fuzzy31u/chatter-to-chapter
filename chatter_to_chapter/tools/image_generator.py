"""ヒーロー画像を生成するツール。"""

import json
import logging
import os

from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .text_overlay import add_text_overlay, create_placeholder_with_text

logger = logging.getLogger(__name__)


def _extract_title(tool_context: ToolContext) -> str:
    """state["episode_data"] JSON からエピソードタイトルを抽出する。"""
    episode_data = tool_context.state.get("episode_data", "")
    if not episode_data:
        return ""
    try:
        # JSON ブロックを抽出（```json ... ``` 形式に対応）
        text = str(episode_data)
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        data = json.loads(text.strip())
        return data.get("title", data.get("episode_title", ""))
    except (json.JSONDecodeError, IndexError, AttributeError):
        logger.warning("episode_data からタイトルを抽出できませんでした")
        return ""


async def _save_image_artifact(
    tool_context: ToolContext, image_bytes: bytes
) -> str:
    """画像バイトデータをアーティファクトとして保存し、artifact URL を返す。"""
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    version = await tool_context.save_artifact(
        filename="hero_image.png", artifact=image_part
    )
    return f"artifact://hero_image.png?version={version}"


async def generate_hero_image(prompt: str, tool_context: ToolContext) -> dict:
    """記事のヒーロー画像を生成します。プロンプトに基づいて Imagen で画像を生成し、アーティファクトとして保存します。

    Args:
        prompt: 画像生成のプロンプト（英語推奨、480トークン以内）。
    """
    dry_run = os.environ.get("DRY_RUN", "TRUE").upper() == "TRUE"
    title = _extract_title(tool_context)

    if dry_run:
        image_bytes = create_placeholder_with_text(title)
        artifact_url = await _save_image_artifact(tool_context, image_bytes)
        tool_context.state["hero_image_url"] = artifact_url
        return {
            "status": "success",
            "mode": "dry_run",
            "message": "DRY_RUN モード: テキスト付きプレースホルダー画像を生成しました。",
            "image_url": artifact_url,
        }

    try:
        from google import genai

        client = genai.Client()
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            ),
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            if title:
                image_bytes = add_text_overlay(image_bytes, title)
            artifact_url = await _save_image_artifact(tool_context, image_bytes)
            tool_context.state["hero_image_url"] = artifact_url
            return {
                "status": "success",
                "mode": "real",
                "message": f"ヒーロー画像を生成しました（テキストオーバーレイ: {'あり' if title else 'なし'}）。",
                "image_url": artifact_url,
            }

        return {
            "status": "error",
            "message": "画像生成に失敗しました。レスポンスに画像が含まれていません。",
        }

    except Exception as e:
        image_bytes = create_placeholder_with_text(title)
        artifact_url = await _save_image_artifact(tool_context, image_bytes)
        tool_context.state["hero_image_url"] = artifact_url
        return {
            "status": "fallback",
            "message": f"画像生成でエラーが発生しました: {e}。テキスト付きプレースホルダーを使用します。",
            "image_url": artifact_url,
        }
