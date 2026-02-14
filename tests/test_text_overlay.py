"""text_overlay モジュールのテスト。"""

import io

from PIL import Image

from chatter_to_chapter.tools.text_overlay import (
    _choose_font_size,
    _wrap_text,
    add_text_overlay,
    create_placeholder_with_text,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_png(width: int = 200, height: int = 100) -> bytes:
    """テスト用の最小 PNG バイトデータを生成する。"""
    img = Image.new("RGB", (width, height), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ===========================================================================
# _wrap_text
# ===========================================================================


class TestWrapText:
    def test_empty_string(self):
        assert _wrap_text("") == ""

    def test_short_text_no_wrap(self):
        assert _wrap_text("Hello") == "Hello"

    def test_exactly_16_chars_no_wrap(self):
        text = "a" * 16
        assert "\n" not in _wrap_text(text)

    def test_17_chars_wraps(self):
        text = "a" * 17
        result = _wrap_text(text)
        assert result == "a" * 16 + "\n" + "a"

    def test_32_chars_two_lines(self):
        text = "a" * 32
        result = _wrap_text(text)
        assert result == "a" * 16 + "\n" + "a" * 16

    def test_japanese_text(self):
        text = "ポッドキャスト文字起こしから記事を自動生成するパイプライン"
        result = _wrap_text(text)
        lines = result.split("\n")
        assert all(len(line) <= 16 for line in lines)
        assert "".join(lines) == text

    def test_custom_chars_per_line(self):
        text = "abcdefgh"
        result = _wrap_text(text, chars_per_line=4)
        assert result == "abcd\nefgh"


# ===========================================================================
# _choose_font_size
# ===========================================================================


class TestChooseFontSize:
    def test_short_title_returns_52(self):
        assert _choose_font_size("短いタイトル") == 52

    def test_empty_string_returns_52(self):
        assert _choose_font_size("") == 52

    def test_exactly_16_returns_52(self):
        assert _choose_font_size("a" * 16) == 52

    def test_17_chars_returns_36(self):
        assert _choose_font_size("a" * 17) == 36

    def test_long_title_returns_36(self):
        assert _choose_font_size("これは非常に長いタイトルで十六文字を超えます") == 36


# ===========================================================================
# add_text_overlay
# ===========================================================================


class TestAddTextOverlay:
    def test_none_title_returns_original(self):
        original = _make_png()
        assert add_text_overlay(original, None) is original

    def test_empty_title_returns_original(self):
        original = _make_png()
        assert add_text_overlay(original, "") is original

    def test_whitespace_title_returns_original(self):
        original = _make_png()
        assert add_text_overlay(original, "   ") is original

    def test_valid_title_returns_png(self):
        original = _make_png(400, 300)
        result = add_text_overlay(original, "テストタイトル")
        assert result != original
        # PNG magic bytes
        assert result[:8] == b"\x89PNG\r\n\x1a\n"
        # 画像として開けることを確認
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"

    def test_invalid_image_bytes_returns_original(self):
        bad_bytes = b"not an image"
        result = add_text_overlay(bad_bytes, "タイトル")
        assert result is bad_bytes


# ===========================================================================
# create_placeholder_with_text
# ===========================================================================


class TestCreatePlaceholderWithText:
    def test_valid_title_returns_png(self):
        result = create_placeholder_with_text("テストタイトル")
        assert result[:8] == b"\x89PNG\r\n\x1a\n"
        img = Image.open(io.BytesIO(result))
        assert img.size == (1200, 630)

    def test_empty_title_returns_png(self):
        result = create_placeholder_with_text("")
        assert result[:8] == b"\x89PNG\r\n\x1a\n"
        img = Image.open(io.BytesIO(result))
        assert img.size == (1200, 630)

    def test_none_title_returns_png(self):
        result = create_placeholder_with_text(None)
        assert result[:8] == b"\x89PNG\r\n\x1a\n"
