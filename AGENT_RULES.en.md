# Chatter to Chapter - Agent Rules

> 🇯🇵 [日本語版はこちら](./AGENT_RULES.md)

## Overview

Chatter to Chapter is an ADK multi-agent pipeline that automatically generates monthly articles from podcast transcripts.

## Pipeline Rules

### 1. TranscriptLoader

- **Input**: File path or inline text
- **Output**: Saves the full transcript to `state["transcript"]`
- If the file is not found, the input is treated as inline text

### 2. EpisodeMiner

- **Input**: `state["transcript"]`
- **Output**: Saves structured JSON to `state["episode_data"]`
- **Extracted fields**: title, guest names, list of topics, notable quotes, summary

### 3. DraftWriter

- **Input**: `state["episode_data"]`
- **Output**: Saves a Markdown article to `state["draft_article"]`
- **Article length**: 1,500–2,000 characters
- Tone should be friendly and make readers want to listen to the episode

### 4. ImageGenerator

- **Input**: Prompt based on the draft article's theme
- **Output**: Saves `artifact://hero_image.png` URL to `state["hero_image_url"]`
- Extracts the episode title from the `state["episode_data"]` JSON and composites Japanese text overlay at the center of the image
- **Text compositing**: Pillow — semi-transparent black rounded rectangle background + white text (Noto Sans JP Bold)
- **Font size**: ≤16 characters → 52px; >16 characters → 36px; automatic line break every 16 characters
- **DRY_RUN mode**: Generates a local placeholder image with text using Pillow (no external URLs)
- **Real mode**: Generates image with Imagen 4, then applies text overlay with Pillow
- **Fallback mode**: Generates a placeholder image with text on error
- All modes return an `artifact://` URL (artifact saved via `tool_context.save_artifact()`)

### 5. Publisher

- **Input**: `state["draft_article"]` + `state["hero_image_url"]`
- **Output**: Saves the final article with YAML frontmatter to `state["final_article"]`

## Quality Standards

- Output in Japanese
- Compliant with Markdown format
- YAML frontmatter compatible with Hugo/Zenn
- Quotes accurately reflect the original text
