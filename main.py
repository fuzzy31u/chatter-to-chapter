"""Chatter to Chapter — カスタム Web UI 付き FastAPI エントリーポイント。"""

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app

BASE_DIR = Path(__file__).parent.resolve()

app = get_fast_api_app(
    agent_dir=str(BASE_DIR),
    web=False,
    allow_origins=["*"],
)


@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "web" / "index.html")


app.mount("/web", StaticFiles(directory=str(BASE_DIR / "web")), name="web")
