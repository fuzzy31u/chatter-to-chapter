# Chatter to Chapter

## Project Overview

ポッドキャスト文字起こしから記事を自動生成する ADK マルチエージェントパイプライン。

## Key URLs

- **Cloud Run**: https://article-factory-106018685388.us-central1.run.app
- **GCP Project**: `hub-momit-fm` (us-central1)
- **Branch**: `main`

## Architecture

```
User Input (transcript path or text)
  → TranscriptLoader (tool agent, sets state["transcript"])
  → EpisodeMiner (LLM agent, output_key="episode_data")
  → DraftWriter (LLM agent, output_key="draft_article")
  → ImageGenerator (tool agent, sets state["hero_image_url"])
  → Publisher (LLM agent, output_key="final_article")
  → Final Article (Markdown + YAML frontmatter + hero image)
```

ADK `SequentialAgent` with 5 sub-agents. Model: `gemini-2.0-flash-001`.

## Tech Stack

- `google-adk` v1.0.0 (Agent Development Kit)
- `google-genai` (Imagen 4 for image generation)
- `Pillow` (日本語テキストオーバーレイ合成)
- Noto Sans JP Bold フォント (Google Fonts, OFL License)
- Vertex AI backend on GCP
- Cloud Run for deployment
- ADK CLI: `python3 -m google.adk.cli` (not `adk` directly)

## Important Implementation Notes

- **output_key pitfall**: TranscriptLoader and ImageGenerator do NOT use `output_key` because their tools directly set state via `tool_context.state[key]`. Using `output_key` would overwrite tool-set values with the agent's text response.
- **Imagen 3 is SHUTDOWN** — using Imagen 4 (`imagen-4.0-generate-001`)
- **DRY_RUN mode**: Set `DRY_RUN=TRUE` in `.env` — Pillow でテキスト付きプレースホルダー画像をローカル生成（外部 URL 不使用）
- **File paths in tools**: `transcript_loader.py` resolves relative paths from `chatter_to_chapter/` directory
- **Publisher date**: Uses `date.today().isoformat()` at import time via f-string
- **Cloud Run deploy**: `gcloud run deploy chatter-to-chapter --source . --project hub-momit-fm --region us-central1 --port 8080 --allow-unauthenticated`
- **Local dev**: `uvicorn main:app --port 8000` → `http://localhost:8000` でカスタム Web UI 表示
- **requirements.txt** must include `deprecated` package (ADK dependency not auto-resolved), `Pillow` (text overlay), and `uvicorn` (ASGI server)
- **Text overlay**: `text_overlay.py` が `episode_data` JSON の `title` フィールドを抽出し、Pillow で画像中央に半透明黒角丸矩形 + 白テキストを合成。フォントは `fonts/NotoSansJP-Bold.ttf`
- **Artifact URL 統一**: 全モード（DRY_RUN / Real / Fallback）で `artifact://hero_image.png` URL を返す（placehold.co 依存を排除）
- **Affiliate Links**: `ENABLE_AFFILIATE_LINKS=TRUE` でプロンプトにアフィリエイトリンク機能を注入。プレースホルダー URL `https://affiliate.example.com/{slug}` を使用。デフォルト OFF。各プロンプトファイルが `os.environ.get()` で条件分岐（`publisher.py` の `_TODAY` パターンに準拠）

## File Structure

```
chatter-to-chapter/
  main.py                           # FastAPI entrypoint (ADK + custom static files)
  Dockerfile                        # Cloud Run deployment
  web/
    index.html                      # Custom Web UI (Tailwind CSS + marked.js)
  chatter_to_chapter/
    __init__.py                     # from . import agent
    agent.py                        # root_agent = SequentialAgent(...)
    .env                            # GOOGLE_GENAI_USE_VERTEXAI=TRUE, DRY_RUN=TRUE
    requirements.txt                # google-adk[all], google-genai, deprecated, Pillow, uvicorn
    fonts/
      NotoSansJP-Bold.ttf           # Noto Sans JP (Google Fonts, OFL License)
    tools/
      __init__.py
      transcript_loader.py          # load_transcript() — reads file or inline text
      image_generator.py            # generate_hero_image() — Imagen 4 + text overlay / DRY_RUN
      text_overlay.py               # add_text_overlay(), create_placeholder_with_text()
    prompts/
      __init__.py
      episode_miner.py              # EPISODE_MINER_INSTRUCTION
      draft_writer.py               # DRAFT_WRITER_INSTRUCTION
      publisher.py                  # PUBLISHER_INSTRUCTION (f-string with date.today())
    sample_data/
      sample_transcript.txt         # Demo transcript (~2000 chars)
  docs/
    architecture-diagram.png        # System architecture diagram
  .env.example
  .gitignore
  README.md
  AGENT_RULES.md
  LICENSE                           # MIT
  CLAUDE.md                         # This file
```
