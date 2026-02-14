"""agent callbacks のテスト。"""

import os

from chatter_to_chapter.agent import _after_transcript_loader


# ===========================================================================
# _after_transcript_loader
# ===========================================================================


class TestAfterTranscriptLoader:
    def test_transcript_already_set_no_change(self, mock_callback_context):
        """transcript が既にセットされている場合、上書きしない。"""
        mock_callback_context.state["transcript"] = "既存のテキスト"
        result = _after_transcript_loader(mock_callback_context)
        assert result is None
        assert mock_callback_context.state["transcript"] == "既存のテキスト"

    def test_transcript_missing_loads_sample(self, mock_callback_context):
        """transcript が未設定の場合、sample_transcript.txt で補完する。"""
        result = _after_transcript_loader(mock_callback_context)
        assert result is None
        transcript = mock_callback_context.state.get("transcript", "")
        assert len(transcript) > 0

    def test_transcript_empty_string_loads_sample(self, mock_callback_context):
        """transcript が空文字列の場合もフォールバックする。"""
        mock_callback_context.state["transcript"] = ""
        result = _after_transcript_loader(mock_callback_context)
        assert result is None
        assert len(mock_callback_context.state["transcript"]) > 0

    def test_fallback_reads_correct_file(self, mock_callback_context):
        """フォールバックで読み込むファイルの内容が sample_transcript.txt と一致する。"""
        sample_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "chatter_to_chapter",
            "sample_data",
            "sample_transcript.txt",
        )
        with open(sample_path, encoding="utf-8") as f:
            expected = f.read()

        _after_transcript_loader(mock_callback_context)
        assert mock_callback_context.state["transcript"] == expected
