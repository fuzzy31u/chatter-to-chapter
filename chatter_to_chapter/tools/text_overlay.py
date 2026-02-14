"""ヒーロー画像にテキストオーバーレイを合成するユーティリティ。"""

import io
import logging
import os

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "fonts",
    "NotoSansJP-Bold.ttf",
)

IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 630
CHARS_PER_LINE = 16


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """フォントをロードする。フォントファイルが見つからない場合はデフォルトを返す。"""
    try:
        return ImageFont.truetype(_FONT_PATH, size)
    except (OSError, IOError):
        logger.warning("フォントファイルが見つかりません: %s — デフォルトフォントを使用", _FONT_PATH)
        return ImageFont.load_default()


def _wrap_text(text: str, chars_per_line: int = CHARS_PER_LINE) -> str:
    """テキストを指定文字数で改行する。"""
    lines = []
    for i in range(0, len(text), chars_per_line):
        lines.append(text[i : i + chars_per_line])
    return "\n".join(lines)


def _choose_font_size(title: str) -> int:
    """タイトル長に応じてフォントサイズを選択する。"""
    if len(title) <= 16:
        return 52
    return 36


def _draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float, float, float],
    radius: int,
    fill: tuple[int, ...],
) -> None:
    """角丸矩形を描画する。"""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def add_text_overlay(image_bytes: bytes, title: str) -> bytes:
    """画像バイトデータにタイトルテキストを合成して返す。

    半透明黒の角丸矩形背景の上に白テキストを中央配置する。
    エラー時はオーバーレイなしの元画像を返す（graceful degradation）。

    Args:
        image_bytes: 元画像の PNG/JPEG バイトデータ。
        title: オーバーレイするタイトルテキスト。

    Returns:
        テキスト合成済み画像の PNG バイトデータ。
    """
    if not title or not title.strip():
        return image_bytes

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font_size = _choose_font_size(title)
        font = _load_font(font_size)
        wrapped = _wrap_text(title)

        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center")
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        pad_x, pad_y = 48, 32
        bg_w = text_w + pad_x * 2
        bg_h = text_h + pad_y * 2
        bg_x = (img.width - bg_w) / 2
        bg_y = (img.height - bg_h) / 2

        _draw_rounded_rect(
            draw,
            (bg_x, bg_y, bg_x + bg_w, bg_y + bg_h),
            radius=16,
            fill=(0, 0, 0, 180),
        )

        text_x = (img.width - text_w) / 2
        text_y = (img.height - text_h) / 2
        draw.multiline_text(
            (text_x, text_y),
            wrapped,
            font=font,
            fill=(255, 255, 255, 255),
            align="center",
        )

        composited = Image.alpha_composite(img, overlay)
        result = composited.convert("RGB")

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()

    except Exception:
        logger.exception("テキストオーバーレイの適用に失敗しました — 元画像を返します")
        return image_bytes


def create_placeholder_with_text(title: str) -> bytes:
    """DRY_RUN 用のプレースホルダー画像をテキスト付きで生成する。

    ダークネイビー背景にアクセントストライプとタイトルオーバーレイを配置する。

    Args:
        title: オーバーレイするタイトルテキスト。

    Returns:
        プレースホルダー画像の PNG バイトデータ。
    """
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), (26, 26, 46))
    draw = ImageDraw.Draw(img)

    # アクセントストライプ（上部と下部）
    accent_color = (233, 69, 96)
    draw.rectangle([0, 0, IMAGE_WIDTH, 6], fill=accent_color)
    draw.rectangle([0, IMAGE_HEIGHT - 6, IMAGE_WIDTH, IMAGE_HEIGHT], fill=accent_color)

    # DRY_RUN ラベル（右上）
    label_font = _load_font(18)
    draw.text((IMAGE_WIDTH - 160, 16), "DRY_RUN MODE", font=label_font, fill=(100, 100, 120))

    # タイトルオーバーレイ
    if title and title.strip():
        title_bytes = io.BytesIO()
        img.save(title_bytes, format="PNG")
        return add_text_overlay(title_bytes.getvalue(), title)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
