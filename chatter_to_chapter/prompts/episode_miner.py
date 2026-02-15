"""EpisodeMiner エージェントのプロンプト。"""

import os

_AFFILIATE_ENABLED = os.environ.get("ENABLE_AFFILIATE_LINKS", "").upper() == "TRUE"

_AFFILIATE_SCHEMA = """,
  "affiliate_suggestions": [
    {{
      "product_name": "製品・サービス・書籍名",
      "slug": "kebab-case-slug",
      "category": "tool | book | service | course | hardware",
      "reason": "推薦理由（1文）"
    }}
  ]"""

_AFFILIATE_NOTES = """
- affiliate_suggestions は文字起こし内で直接言及されている製品・サービス・書籍 + 文脈から有用と判断される関連製品を 3-5 件抽出
- slug は kebab-case（URL safe、英数字とハイフンのみ）
- category は tool / book / service / course / hardware のいずれか"""

EPISODE_MINER_INSTRUCTION = f"""あなたはポッドキャストのエピソード分析の専門家です。

以下の文字起こしテキストを分析し、構造化された JSON データを出力してください。

## 入力
{{transcript}}

## 出力フォーマット

以下の JSON 形式で出力してください。JSON のみを出力し、他のテキストは含めないでください。

```json
{{{{
  "title": "エピソードのタイトル（文字起こしから推測）",
  "guests": ["ゲスト名1", "ゲスト名2"],
  "hosts": ["ホスト名"],
  "topics": [
    {{{{
      "title": "トピック名",
      "summary": "トピックの要約（2-3文）",
      "key_points": ["ポイント1", "ポイント2"]
    }}}}
  ],
  "quotes": [
    {{{{
      "speaker": "発言者名",
      "text": "印象的な引用文",
      "context": "引用の文脈"
    }}}}
  ],
  "summary": "エピソード全体の要約（200-300字）",
  "keywords": ["キーワード1", "キーワード2", "キーワード3"]{_AFFILIATE_SCHEMA if _AFFILIATE_ENABLED else ""}
}}}}
```

## 注意事項
- 発言者名は文字起こしテキストに登場する名前をそのまま使用すること
- 引用（quotes）は文字起こしテキスト内の実際の発言をそのまま抜き出すこと。絶対に創作しないこと
- ホスト（hosts）とゲスト（guests）は文字起こしの文脈から判断すること（「お迎えしています」と紹介される側がゲスト）
- トピックは議論の流れに沿って時系列で抽出
- キーワードは SEO を意識して 5-10 個抽出
- JSON のみを出力すること（```json ブロックで囲んで出力）{_AFFILIATE_NOTES if _AFFILIATE_ENABLED else ""}
"""
