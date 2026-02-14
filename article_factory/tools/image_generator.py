"""ヒーロー画像を生成するツール。"""

import os

from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def generate_hero_image(prompt: str, tool_context: ToolContext) -> dict:
    """記事のヒーロー画像を生成します。プロンプトに基づいて Imagen で画像を生成し、アーティファクトとして保存します。

    Args:
        prompt: 画像生成のプロンプト（英語推奨、480トークン以内）。
    """
    dry_run = os.environ.get("DRY_RUN", "TRUE").upper() == "TRUE"

    if dry_run:
        placeholder_url = "https://placehold.co/1200x630/1a1a2e/e94560?text=Article+Hero+Image"
        tool_context.state["hero_image_url"] = placeholder_url
        return {
            "status": "success",
            "mode": "dry_run",
            "message": "DRY_RUN モード: プレースホルダー画像を使用します。",
            "image_url": placeholder_url,
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
            image_part = types.Part.from_bytes(
                data=image_bytes, mime_type="image/png"
            )
            version = await tool_context.save_artifact(
                filename="hero_image.png", artifact=image_part
            )
            artifact_url = f"artifact://hero_image.png?version={version}"
            tool_context.state["hero_image_url"] = artifact_url
            return {
                "status": "success",
                "mode": "real",
                "message": f"ヒーロー画像を生成しました（version: {version}）。",
                "image_url": artifact_url,
            }

        return {
            "status": "error",
            "message": "画像生成に失敗しました。レスポンスに画像が含まれていません。",
        }

    except Exception as e:
        placeholder_url = "https://placehold.co/1200x630/1a1a2e/e94560?text=Article+Hero+Image"
        tool_context.state["hero_image_url"] = placeholder_url
        return {
            "status": "fallback",
            "message": f"画像生成でエラーが発生しました: {e}。プレースホルダーを使用します。",
            "image_url": placeholder_url,
        }
