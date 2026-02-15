"""image_generator モジュールのテスト。"""

import json
from unittest.mock import patch

import pytest

from chatter_to_chapter.tools.image_generator import (
    _extract_title,
    generate_hero_image,
)


# ===========================================================================
# _extract_title
# ===========================================================================


class TestExtractTitle:
    def test_no_episode_data_returns_empty(self, mock_tool_context):
        assert _extract_title(mock_tool_context) == ""

    def test_empty_episode_data_returns_empty(self, mock_tool_context):
        mock_tool_context.state["episode_data"] = ""
        assert _extract_title(mock_tool_context) == ""

    def test_valid_json_with_title(self, mock_tool_context):
        data = json.dumps({"title": "エピソードタイトル", "summary": "概要"})
        mock_tool_context.state["episode_data"] = data
        assert _extract_title(mock_tool_context) == "エピソードタイトル"

    def test_fallback_to_episode_title(self, mock_tool_context):
        data = json.dumps({"episode_title": "別のタイトル"})
        mock_tool_context.state["episode_data"] = data
        assert _extract_title(mock_tool_context) == "別のタイトル"

    def test_title_preferred_over_episode_title(self, mock_tool_context):
        data = json.dumps({"title": "優先", "episode_title": "フォールバック"})
        mock_tool_context.state["episode_data"] = data
        assert _extract_title(mock_tool_context) == "優先"

    def test_markdown_json_block(self, mock_tool_context):
        md = '```json\n{"title": "Markdown内タイトル"}\n```'
        mock_tool_context.state["episode_data"] = md
        assert _extract_title(mock_tool_context) == "Markdown内タイトル"

    def test_generic_code_block(self, mock_tool_context):
        md = '```\n{"title": "コードブロック内"}\n```'
        mock_tool_context.state["episode_data"] = md
        assert _extract_title(mock_tool_context) == "コードブロック内"

    def test_invalid_json_returns_empty(self, mock_tool_context):
        mock_tool_context.state["episode_data"] = "これはJSONではない"
        assert _extract_title(mock_tool_context) == ""

    def test_json_without_title_keys_returns_empty(self, mock_tool_context):
        data = json.dumps({"summary": "概要のみ"})
        mock_tool_context.state["episode_data"] = data
        assert _extract_title(mock_tool_context) == ""


# ===========================================================================
# generate_hero_image
# ===========================================================================

PNG_MAGIC = b"\x89PNG"


class TestGenerateHeroImageDryRun:
    @pytest.mark.asyncio
    async def test_returns_success_with_dry_run_mode(self, mock_tool_context):
        mock_tool_context.state["episode_data"] = json.dumps({"title": "テスト"})

        with patch.dict("os.environ", {"DRY_RUN": "TRUE"}):
            result = await generate_hero_image("test prompt", mock_tool_context)

        assert result["status"] == "success"
        assert result["mode"] == "dry_run"

    @pytest.mark.asyncio
    async def test_saves_artifact(self, mock_tool_context):
        mock_tool_context.save_artifact.return_value = 1

        with patch.dict("os.environ", {"DRY_RUN": "TRUE"}):
            result = await generate_hero_image("test prompt", mock_tool_context)

        mock_tool_context.save_artifact.assert_awaited_once()
        assert result["image_url"] == "artifact://hero_image.png?version=1"

    @pytest.mark.asyncio
    async def test_sets_hero_image_url_in_state(self, mock_tool_context):
        mock_tool_context.save_artifact.return_value = 2

        with patch.dict("os.environ", {"DRY_RUN": "TRUE"}):
            await generate_hero_image("test prompt", mock_tool_context)

        assert mock_tool_context.state["hero_image_url"].startswith("artifact://")

    @pytest.mark.asyncio
    async def test_artifact_bytes_are_valid_png(self, mock_tool_context):
        with patch.dict("os.environ", {"DRY_RUN": "TRUE"}):
            await generate_hero_image("test prompt", mock_tool_context)

        saved_part = mock_tool_context.save_artifact.call_args[1]["artifact"]
        assert saved_part.inline_data.data[:4] == PNG_MAGIC


class TestGenerateHeroImageFallback:
    @pytest.mark.asyncio
    async def test_returns_fallback_when_imagen_fails(self, mock_tool_context):
        mock_tool_context.state["episode_data"] = json.dumps({"title": "テスト"})

        with patch.dict("os.environ", {"DRY_RUN": "FALSE"}):
            result = await generate_hero_image("test prompt", mock_tool_context)

        assert result["status"] == "fallback"

    @pytest.mark.asyncio
    async def test_fallback_saves_valid_png_artifact(self, mock_tool_context):
        with patch.dict("os.environ", {"DRY_RUN": "FALSE"}):
            await generate_hero_image("test prompt", mock_tool_context)

        mock_tool_context.save_artifact.assert_awaited_once()
        saved_part = mock_tool_context.save_artifact.call_args[1]["artifact"]
        assert saved_part.inline_data.data[:4] == PNG_MAGIC

    @pytest.mark.asyncio
    async def test_fallback_sets_hero_image_url(self, mock_tool_context):
        mock_tool_context.save_artifact.return_value = 5

        with patch.dict("os.environ", {"DRY_RUN": "FALSE"}):
            result = await generate_hero_image("test prompt", mock_tool_context)

        assert mock_tool_context.state["hero_image_url"] == "artifact://hero_image.png?version=5"
        assert result["image_url"] == "artifact://hero_image.png?version=5"
