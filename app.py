from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, validator

try:
    from html2image import Html2Image
except ImportError as exc:  # pragma: no cover - helps when dependency missing
    raise ImportError(
        "html2image is required. Install dependencies with 'pip install fastapi html2image uvicorn'."
    ) from exc


class RenderRequest(BaseModel):
    html: str = Field(..., description="Raw HTML markup to render")
    width: Optional[int] = Field(1200, ge=100, le=4000, description="Image width in pixels")
    height: Optional[int] = Field(630, ge=100, le=4000, description="Image height in pixels")
    delay_ms: Optional[int] = Field(250, ge=0, le=5000, description="Delay in ms before screenshot")

    @validator("html")
    def validate_html(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("HTML cannot be empty")
        return value


load_dotenv()
API_KEY = os.getenv("API_KEY")
CHROME_EXECUTABLE = os.getenv("CHROME_PATH") or os.getenv("HTML2IMAGE_CHROME_PATH")


app = FastAPI(title="HTML -> PNG API", version="1.1.0")


def require_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def render_html_to_png(payload: RenderRequest) -> bytes:
    size = None
    if payload.width and payload.height:
        size = (payload.width, payload.height)

    with TemporaryDirectory() as tmp_dir:
        hti_kwargs: dict[str, object] = {
            "output_path": tmp_dir,
            "custom_flags": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        }
        if CHROME_EXECUTABLE:
            hti_kwargs["browser_executable"] = CHROME_EXECUTABLE

        hti = Html2Image(**hti_kwargs)
        filename = f"render_{uuid4().hex}.png"

        if payload.delay_ms:
            time.sleep(payload.delay_ms / 1000)

        # html2image handles writing HTML to a temp file and taking the screenshot.
        hti.screenshot(
            html_str=payload.html,
            save_as=filename,
            size=size,
        )

        image_path = Path(tmp_dir) / filename
        if not image_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create image")

        return image_path.read_bytes()


@app.get("/health", dependencies=[Depends(require_api_key)])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/render")
def render_endpoint(payload: RenderRequest, _: None = Depends(require_api_key)) -> dict[str, object]:
    image_bytes = render_html_to_png(payload)
    b64_image = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:image/png;base64,{b64_image}"
    return {
        "width": payload.width,
        "height": payload.height,
        "delay_ms": payload.delay_ms,
        "image_base64": data_url,
    }


# To run locally: `uvicorn app:app --reload`
