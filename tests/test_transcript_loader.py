"""transcript_loader モジュールのテスト。"""

import os

from chatter_to_chapter.tools.transcript_loader import (
    MAX_TRANSCRIPT_CHARS,
    load_transcript,
)


# ===========================================================================
# load_transcript
# ===========================================================================


class TestLoadTranscript:
    def test_empty_string_returns_error(self, mock_tool_context):
        result = load_transcript("", mock_tool_context)
        assert result["status"] == "error"

    def test_whitespace_only_returns_error(self, mock_tool_context):
        result = load_transcript("   ", mock_tool_context)
        assert result["status"] == "error"
        assert "空です" in result["message"]

    def test_inline_text_success(self, mock_tool_context):
        text = "これはテスト用のインラインテキストです。"
        result = load_transcript(text, mock_tool_context)
        assert result["status"] == "success"
        assert result["truncated"] is False
        assert mock_tool_context.state["transcript"] == text

    def test_inline_text_char_count(self, mock_tool_context):
        text = "あいうえお"
        result = load_transcript(text, mock_tool_context)
        assert result["char_count"] == 5

    def test_truncation_over_max_chars(self, mock_tool_context):
        text = "あ" * (MAX_TRANSCRIPT_CHARS + 100)
        result = load_transcript(text, mock_tool_context)
        assert result["status"] == "success"
        assert result["truncated"] is True
        assert result["effective_chars"] == MAX_TRANSCRIPT_CHARS
        assert len(mock_tool_context.state["transcript"]) == MAX_TRANSCRIPT_CHARS

    def test_exactly_max_chars_not_truncated(self, mock_tool_context):
        text = "a" * MAX_TRANSCRIPT_CHARS
        result = load_transcript(text, mock_tool_context)
        assert result["truncated"] is False

    def test_file_read_with_tmp_path(self, tmp_path, mock_tool_context):
        content = "ファイルから読み込んだテキスト"
        file = tmp_path / "transcript.txt"
        file.write_text(content, encoding="utf-8")
        result = load_transcript(str(file), mock_tool_context)
        assert result["status"] == "success"
        assert mock_tool_context.state["transcript"] == content

    def test_nonexistent_file_treated_as_inline(self, mock_tool_context):
        """存在しないパスはインラインテキストとして処理される。"""
        source = "/nonexistent/path/to/file.txt"
        result = load_transcript(source, mock_tool_context)
        # パスの文字列自体がインラインテキストとして扱われる
        assert result["status"] == "success"
        assert mock_tool_context.state["transcript"] == source

    def test_sample_transcript_relative_path(self, mock_tool_context):
        """sample_data/sample_transcript.txt が相対パスで読み込める。"""
        result = load_transcript(
            "sample_data/sample_transcript.txt", mock_tool_context
        )
        assert result["status"] == "success"
        assert len(mock_tool_context.state["transcript"]) > 0

    def test_encoding_error(self, tmp_path, mock_tool_context):
        """非 UTF-8 ファイルでエンコーディングエラーが返る。"""
        file = tmp_path / "bad_encoding.txt"
        file.write_bytes(b"\xff\xfe" + "テスト".encode("utf-16-le"))
        # UTF-16 LE BOM を含むファイルを UTF-8 として読むとエラーになる場合がある
        # ただし Python は BOM 付き UTF-16 を UTF-8 で読んでも decode はできる可能性があるため
        # バイナリ的に不正な UTF-8 で確実にエラーを起こす
        file.write_bytes(b"\x80\x81\x82\x83")
        result = load_transcript(str(file), mock_tool_context)
        assert result["status"] == "error"
