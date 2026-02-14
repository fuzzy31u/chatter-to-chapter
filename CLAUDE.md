# hub.momit.fm — Article Factory

## Project Overview

Google Cloud Japan AI Hackathon Vol.4 エントリー作品。
ポッドキャスト文字起こしから月刊記事を自動生成する ADK マルチエージェントパイプライン。

**Deadline: 2026-02-15**

## Key URLs

- **Cloud Run**: https://article-factory-106018685388.us-central1.run.app
- **GCP Project**: `hub-momit-fm` (us-central1)
- **Branch**: `feature/concurrent-dev`

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
- Vertex AI backend on GCP
- Cloud Run for deployment
- ADK CLI: `python3 -m google.adk.cli` (not `adk` directly)

## Important Implementation Notes

- **output_key pitfall**: TranscriptLoader and ImageGenerator do NOT use `output_key` because their tools directly set state via `tool_context.state[key]`. Using `output_key` would overwrite tool-set values with the agent's text response.
- **Imagen 3 is SHUTDOWN** — using Imagen 4 (`imagen-4.0-generate-001`)
- **DRY_RUN mode**: Set `DRY_RUN=TRUE` in `.env` to use placeholder images
- **File paths in tools**: `transcript_loader.py` resolves relative paths from `article_factory/` directory
- **Publisher date**: Uses `date.today().isoformat()` at import time via f-string
- **Cloud Run deploy**: `python3 -m google.adk.cli deploy cloud_run --project=hub-momit-fm --region=us-central1 --service_name=article-factory --with_ui article_factory/`
- **requirements.txt** must include `deprecated` package (ADK dependency not auto-resolved)

## Phase Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: GCP Setup | DONE | Billing enabled, APIs activated |
| Phase 1: Skeleton + Local | DONE | All files created, local test passed |
| Phase 2: Cloud Run Deploy | DONE | Deployed at revision 4, allUsers access |
| Phase 3: Polish | DONE | output_key bug fixed, prompts tuned, redeployed |
| Phase 4: Submission | TODO | README finalize, git commit+push, Zenn article, demo video |

## Phase 4 TODO (Remaining Work)

1. **Git commit & push** — All files are created but not committed yet (only initial commit exists)
2. **README.md finalize** — Add actual Cloud Run URL, update architecture diagram
3. **GitHub repo public** — Push to main/remote, make repo public
4. **Zenn article** — Project overview, architecture (Mermaid), code snippets, demo results. Category: Idea, topic tag: `gch4`
5. **3-min demo video** — ADK Web UI pipeline execution demo → YouTube embed

## File Structure

```
hub.momit.fm/
  article_factory/
    __init__.py                     # from . import agent
    agent.py                        # root_agent = SequentialAgent(...)
    .env                            # GOOGLE_GENAI_USE_VERTEXAI=TRUE, DRY_RUN=TRUE
    requirements.txt                # google-adk[all], google-genai, deprecated
    tools/
      __init__.py
      transcript_loader.py          # load_transcript() — reads file or inline text
      image_generator.py            # generate_hero_image() — Imagen 4 / DRY_RUN placeholder
    prompts/
      __init__.py
      episode_miner.py              # EPISODE_MINER_INSTRUCTION
      draft_writer.py               # DRAFT_WRITER_INSTRUCTION
      publisher.py                  # PUBLISHER_INSTRUCTION (f-string with date.today())
    sample_data/
      sample_transcript.txt         # Demo transcript (~2000 chars)
  .env.example
  .gitignore
  README.md
  AGENT_RULES.md
  LICENSE                           # MIT
  CLAUDE.md                         # This file
```

## Required Hackathon Deliverables

1. Public GitHub repository URL
2. Deployed Cloud Run URL (already: https://article-factory-106018685388.us-central1.run.app)
3. Zenn article (category: Idea, topic tag: `gch4`)
4. 3-min demo video (YouTube)
