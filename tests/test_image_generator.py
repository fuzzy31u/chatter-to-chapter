"""image_generator モジュールのテスト。"""

import json

from chatter_to_chapter.tools.image_generator import _extract_title


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
