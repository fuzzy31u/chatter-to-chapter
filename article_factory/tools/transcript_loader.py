"""文字起こしテキストを読み込むツール。"""

import os

from google.adk.tools.tool_context import ToolContext


def load_transcript(source: str, tool_context: ToolContext) -> dict:
    """文字起こしテキストを読み込みます。ファイルパスが指定された場合はファイルから、それ以外はインラインテキストとして処理します。

    Args:
        source: 文字起こしテキストのファイルパス、またはインラインの文字起こしテキスト。
    """
    # ファイルパスとして存在するか確認（相対パスは article_factory/ 基準で解決）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(base_dir, source) if not os.path.isabs(source) else source

    if os.path.exists(candidate):
        with open(candidate, encoding="utf-8") as f:
            transcript = f.read()
    elif os.path.exists(source):
        with open(source, encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = source

    if not transcript.strip():
        return {"status": "error", "message": "文字起こしテキストが空です。"}

    tool_context.state["transcript"] = transcript

    char_count = len(transcript)
    return {
        "status": "success",
        "message": f"文字起こしテキストを読み込みました（{char_count}文字）。",
        "char_count": char_count,
    }
