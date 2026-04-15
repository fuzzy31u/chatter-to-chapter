# Chatter to Chapter

[日本語版 README はこちら](README.md)

An ADK multi-agent pipeline that automatically generates articles from podcast transcripts.

## Architecture

![System Architecture](docs/architecture-diagram.png)

Five sub-agents are executed sequentially using ADK `SequentialAgent`, sharing state via `output_key` and `tool_context.state`.

| Agent | Type | Role | Output |
|-------|------|------|--------|
| TranscriptLoader | Tool Agent | Load transcript text | `state["transcript"]` |
| EpisodeMiner | LLM Agent | Extract structured episode data | `state["episode_data"]` |
| DraftWriter | LLM Agent | Generate Markdown article | `state["draft_article"]` |
| ImageGenerator | Tool Agent | Generate hero image with Imagen 4 + Japanese text overlay | `state["hero_image_url"]` |
| Publisher | LLM Agent | Output final article with frontmatter | `state["final_article"]` |

### State Sharing Design

- **LLM Agents** (EpisodeMiner, DraftWriter, Publisher): Agent responses are automatically saved to state via `output_key`
- **Tool Agents** (TranscriptLoader, ImageGenerator): State is set directly within tool functions using `tool_context.state[key]`. `output_key` is not used (to prevent the agent's response from overwriting the values set by the tool)

### Hero Image Generation Flow

```
EpisodeMiner -> episode_data (JSON with title)
                    |
ImageGenerator -> _extract_title() extracts title
                    |
              +- DRY_RUN: create_placeholder_with_text() generates local image
              +- Real: Imagen 4 generation -> add_text_overlay() composites title
              +- Fallback: create_placeholder_with_text() generates image on error
                    |
              Saved as artifact://hero_image.png
```

Since Imagen struggles with CJK text rendering, text is composited as a post-processing step using Pillow after image generation.

## Tech Stack

- **Agent Framework**: [Google ADK](https://google.github.io/adk-docs/) v1.0.0
- **LLM**: Gemini 2.0 Flash (`gemini-2.0-flash-001`)
- **Image Generation**: Imagen 4 (`imagen-4.0-generate-001`) + Pillow text overlay / Local placeholder generation in DRY_RUN mode
- **Image Processing**: [Pillow](https://pillow.readthedocs.io/) (Japanese title overlay compositing)
- **Font**: Noto Sans JP (Google Fonts, OFL License)
- **Backend**: Vertex AI (GCP)
- **Deployment**: Google Cloud Run
- **Language**: Python 3.11+

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud`)
- GCP project (with Vertex AI API enabled)

### Setup

```bash
# Clone the repository
git clone https://github.com/fuzzy31u/chatter-to-chapter.git
cd chatter-to-chapter

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r chatter_to_chapter/requirements.txt

# Configure environment variables
cp .env.example chatter_to_chapter/.env
# Edit chatter_to_chapter/.env and set your GCP project ID

# Authenticate with GCP
gcloud auth application-default login
```

### Run Locally

```bash
uvicorn main:app --port 8000
```

Open `http://localhost:8000` in your browser and submit a transcript through the custom Web UI.

### Deploy to Cloud Run

```bash
gcloud run deploy chatter-to-chapter \
  --source . \
  --project hub-momit-fm \
  --region us-central1 \
  --port 8080 \
  --allow-unauthenticated
```

## Usage

Run the pipeline through the custom Web UI. Paste a transcript into the text area or click the "Use Sample" button to load demo data, then click "Generate Article".

The 5-step pipeline progress is displayed in real time. Once complete, the hero image and article preview are shown. You can retrieve the generated article using the Copy button or the Download .md button.

### Web UI Features

- **Pipeline Progress**: 5-step progress bar (TranscriptLoader -> EpisodeMiner -> DraftWriter -> ImageGenerator -> Publisher)
- **Agent Log**: Real-time display of each agent's execution log
- **Article Preview**: Rich rendering of Markdown (with YAML frontmatter support)
- **Hero Image**: Display of the generated hero image
- **Copy / Download**: Copy the final article to clipboard or download as a .md file

## File Structure

```
chatter-to-chapter/
├── main.py                        # FastAPI entrypoint (ADK + custom static files)
├── Dockerfile                     # Cloud Run deployment
├── web/
│   └── index.html                 # Custom Web UI (Tailwind CSS + marked.js)
├── chatter_to_chapter/
│   ├── __init__.py
│   ├── agent.py                   # root_agent (SequentialAgent)
│   ├── .env                       # Vertex AI / DRY_RUN settings
│   ├── requirements.txt
│   ├── fonts/
│   │   └── NotoSansJP-Bold.ttf    # Japanese font (Google Fonts, OFL)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── transcript_loader.py   # load_transcript()
│   │   ├── image_generator.py     # generate_hero_image()
│   │   └── text_overlay.py        # add_text_overlay(), create_placeholder_with_text()
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── episode_miner.py
│   │   ├── draft_writer.py
│   │   └── publisher.py
│   └── sample_data/
│       └── sample_transcript.txt
├── docs/
│   └── architecture-diagram.png   # System architecture diagram
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## License

MIT
