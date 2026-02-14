"""文字起こしテキストを読み込むツール。"""

import logging
import os

from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

# Gemini 2.0 Flash のコンテキストウィンドウを考慮した安全な上限
# プロンプト + JSON 出力分のトークンを確保するため、文字数で制限
MAX_TRANSCRIPT_CHARS = 50_000  # 約 50,000 文字 ≒ ~25,000 トークン（日本語）


def load_transcript(source: str, tool_context: ToolContext) -> dict:
    """文字起こしテキストを読み込みます。ファイルパスが指定された場合はファイルから、それ以外はインラインテキストとして処理します。

    Args:
        source: 文字起こしテキストのファイルパス、またはインラインの文字起こしテキスト。
    """
    try:
        # ファイルパスとして存在するか確認（相対パスは chatter_to_chapter/ 基準で解決）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = (
            os.path.join(base_dir, source) if not os.path.isabs(source) else source
        )

        if os.path.exists(candidate):
            logger.info("ファイルから読み込み: %s", candidate)
            with open(candidate, encoding="utf-8") as f:
                transcript = f.read()
        elif os.path.exists(source):
            logger.info("ファイルから読み込み: %s", source)
            with open(source, encoding="utf-8") as f:
                transcript = f.read()
        else:
            logger.info("インラインテキストとして処理（%d 文字）", len(source))
            transcript = source

        if not transcript.strip():
            return {"status": "error", "message": "文字起こしテキストが空です。"}

        char_count = len(transcript)
        truncated = False

        if char_count > MAX_TRANSCRIPT_CHARS:
            logger.warning(
                "文字起こしテキストが上限を超えています（%d > %d）。切り詰めます。",
                char_count,
                MAX_TRANSCRIPT_CHARS,
            )
            transcript = transcript[:MAX_TRANSCRIPT_CHARS]
            truncated = True

        tool_context.state["transcript"] = transcript

        message = f"文字起こしテキストを読み込みました（{char_count}文字）。"
        if truncated:
            message += f" ※上限 {MAX_TRANSCRIPT_CHARS} 文字に切り詰めました。"

        return {
            "status": "success",
            "message": message,
            "char_count": char_count,
            "truncated": truncated,
            "effective_chars": len(transcript),
        }

    except FileNotFoundError as e:
        logger.error("ファイルが見つかりません: %s", e)
        return {"status": "error", "message": f"ファイルが見つかりません: {e}"}
    except PermissionError as e:
        logger.error("ファイルの読み取り権限がありません: %s", e)
        return {"status": "error", "message": f"ファイルの読み取り権限がありません: {e}"}
    except UnicodeDecodeError as e:
        logger.error("ファイルのエンコーディングエラー: %s", e)
        return {
            "status": "error",
            "message": f"ファイルのエンコーディングエラー（UTF-8 以外の可能性）: {e}",
        }
    except Exception as e:
        logger.exception("文字起こしテキストの読み込みで予期しないエラー")
        return {"status": "error", "message": f"予期しないエラー: {type(e).__name__}: {e}"}
