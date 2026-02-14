# Article Factory - Agent Rules

## Overview

Article Factory は、ポッドキャスト文字起こしから月刊記事を自動生成する ADK マルチエージェントパイプラインです。

## パイプラインルール

### 1. TranscriptLoader
- 入力: ファイルパスまたはインラインテキスト
- 出力: `state["transcript"]` に文字起こし全文を保存
- ファイルが見つからない場合はインラインテキストとして処理

### 2. EpisodeMiner
- 入力: `state["transcript"]`
- 出力: `state["episode_data"]` に構造化 JSON を保存
- 抽出項目: タイトル、ゲスト名、トピック一覧、印象的な引用、要約

### 3. DraftWriter
- 入力: `state["episode_data"]`
- 出力: `state["draft_article"]` に Markdown 記事を保存
- 記事の長さ: 1500-2000 字
- トーンは親しみやすく、読者が聴きたくなる内容

### 4. ImageGenerator
- 入力: ドラフト記事のテーマに基づくプロンプト
- 出力: `state["hero_image_url"]` に `artifact://hero_image.png` URL を保存
- `state["episode_data"]` JSON からエピソードタイトルを抽出し、画像中央に日本語テキストオーバーレイを合成
- テキスト合成: Pillow で半透明黒角丸矩形背景 + 白文字（Noto Sans JP Bold）
- フォントサイズ: 16 文字以下 → 52px、それ以上 → 36px、16 文字ごとに自動改行
- DRY_RUN モード: Pillow でテキスト付きプレースホルダー画像をローカル生成（外部 URL 不使用）
- Real モード: Imagen 4 で生成後、Pillow でテキストオーバーレイを適用
- Fallback モード: エラー時もテキスト付きプレースホルダーを生成
- 全モードで `artifact://` URL を返す（`tool_context.save_artifact()` でアーティファクト保存）

### 5. Publisher
- 入力: `state["draft_article"]` + `state["hero_image_url"]`
- 出力: `state["final_article"]` に YAML frontmatter 付き最終記事を保存

## 品質基準

- 日本語で出力
- Markdown フォーマット準拠
- YAML frontmatter は Hugo/Zenn 互換
- 引用は原文を正確に反映
