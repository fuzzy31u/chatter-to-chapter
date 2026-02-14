"""テスト共通 fixtures。"""

from unittest.mock import MagicMock

import pytest


class _StateDict(dict):
    """CallbackContext.state の to_dict() をサポートする dict サブクラス。"""

    def to_dict(self):
        return dict(self)


@pytest.fixture
def mock_tool_context():
    """ADK ToolContext の軽量モック。state は通常の dict。"""
    ctx = MagicMock()
    ctx.state = {}
    return ctx


@pytest.fixture
def mock_callback_context():
    """ADK CallbackContext の軽量モック。state.to_dict() をサポート。"""
    ctx = MagicMock()
    ctx.state = _StateDict()
    return ctx
