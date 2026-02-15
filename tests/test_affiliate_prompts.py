"""アフィリエイトリンク機能のプロンプトトグルテスト。"""

import importlib
import os

import pytest

AFFILIATE_URL_BASE = "https://affiliate.example.com/"


class TestEpisodeMinerAffiliate:
    """EpisodeMiner プロンプトのアフィリエイトトグルテスト。"""

    def test_disabled_excludes_affiliate(self):
        """ENABLE_AFFILIATE_LINKS=FALSE 時に affiliate 関連文言が含まれない。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "FALSE"
        import chatter_to_chapter.prompts.episode_miner as mod

        importlib.reload(mod)

        assert "affiliate_suggestions" not in mod.EPISODE_MINER_INSTRUCTION
        assert "slug" not in mod.EPISODE_MINER_INSTRUCTION
        assert "kebab-case" not in mod.EPISODE_MINER_INSTRUCTION

    def test_enabled_includes_affiliate_schema(self):
        """ENABLE_AFFILIATE_LINKS=TRUE 時に affiliate_suggestions スキーマが含まれる。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "TRUE"
        import chatter_to_chapter.prompts.episode_miner as mod

        importlib.reload(mod)

        assert "affiliate_suggestions" in mod.EPISODE_MINER_INSTRUCTION
        assert "product_name" in mod.EPISODE_MINER_INSTRUCTION
        assert "slug" in mod.EPISODE_MINER_INSTRUCTION
        assert "category" in mod.EPISODE_MINER_INSTRUCTION
        assert "reason" in mod.EPISODE_MINER_INSTRUCTION
        assert "kebab-case" in mod.EPISODE_MINER_INSTRUCTION

    def test_default_env_excludes_affiliate(self):
        """環境変数未設定時は affiliate が含まれない。"""
        os.environ.pop("ENABLE_AFFILIATE_LINKS", None)
        import chatter_to_chapter.prompts.episode_miner as mod

        importlib.reload(mod)

        assert "affiliate_suggestions" not in mod.EPISODE_MINER_INSTRUCTION


class TestDraftWriterAffiliate:
    """DraftWriter プロンプトのアフィリエイトトグルテスト。"""

    def test_disabled_excludes_affiliate(self):
        """ENABLE_AFFILIATE_LINKS=FALSE 時にアフィリエイトルールが含まれない。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "FALSE"
        import chatter_to_chapter.prompts.draft_writer as mod

        importlib.reload(mod)

        assert AFFILIATE_URL_BASE not in mod.DRAFT_WRITER_INSTRUCTION
        assert "アフィリエイトリンク" not in mod.DRAFT_WRITER_INSTRUCTION

    def test_enabled_includes_affiliate_rules(self):
        """ENABLE_AFFILIATE_LINKS=TRUE 時にアフィリエイトリンク挿入ルールが含まれる。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "TRUE"
        import chatter_to_chapter.prompts.draft_writer as mod

        importlib.reload(mod)

        assert AFFILIATE_URL_BASE in mod.DRAFT_WRITER_INSTRUCTION
        assert "アフィリエイトリンク" in mod.DRAFT_WRITER_INSTRUCTION
        assert "最大 1 回" in mod.DRAFT_WRITER_INSTRUCTION


class TestPublisherAffiliate:
    """Publisher プロンプトのアフィリエイトトグルテスト。"""

    def test_disabled_excludes_affiliate(self):
        """ENABLE_AFFILIATE_LINKS=FALSE 時に affiliate_links が含まれない。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "FALSE"
        import chatter_to_chapter.prompts.publisher as mod

        importlib.reload(mod)

        assert "affiliate_links" not in mod.PUBLISHER_INSTRUCTION

    def test_enabled_includes_affiliate_frontmatter(self):
        """ENABLE_AFFILIATE_LINKS=TRUE 時に affiliate_links frontmatter が含まれる。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "TRUE"
        import chatter_to_chapter.prompts.publisher as mod

        importlib.reload(mod)

        assert "affiliate_links" in mod.PUBLISHER_INSTRUCTION
        assert AFFILIATE_URL_BASE in mod.PUBLISHER_INSTRUCTION

    def test_placeholder_url_format(self):
        """プレースホルダー URL が RFC 2606 の example.com を使用している。"""
        os.environ["ENABLE_AFFILIATE_LINKS"] = "TRUE"
        import chatter_to_chapter.prompts.draft_writer as dw
        import chatter_to_chapter.prompts.publisher as pub

        importlib.reload(dw)
        importlib.reload(pub)

        assert "affiliate.example.com" in dw.DRAFT_WRITER_INSTRUCTION
        assert "affiliate.example.com" in pub.PUBLISHER_INSTRUCTION
