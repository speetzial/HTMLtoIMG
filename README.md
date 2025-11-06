# HTML -> PNG API

FastAPI-Anwendung zum Rendern von HTML-Snippets als PNG-Bild mittels `html2image`.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Starten

```powershell
uvicorn app:app --reload
```

API erreichbar unter `http://127.0.0.1:8000`.

### API-Key setzen (.env)

1. `.env` im Projektordner anlegen:
   ```
   API_KEY=dein-geheimer-schluessel
   ```
2. Server neu starten.
3. Bei jedem Request den Header `X-API-Key: dein-geheimer-schluessel` mitsenden. Ohne gesetzte `API_KEY`-Variable sind alle Endpunkte frei erreichbar (praktisch fuer lokale Tests).

Optional: Setze `CHROME_PATH` oder `HTML2IMAGE_CHROME_PATH`, falls du einen eigenen Chromium-/Chrome-Pfad vorgibst (z. B. in Docker-Setups).

## Endpunkte

- `GET /health` - einfacher Healthcheck (erfordert `X-API-Key`, sobald `API_KEY` gesetzt ist).
- `POST /render` - akzeptiert JSON mit HTML-Inhalt und optionalen Render-Optionen.

### Beispiel-Request

```json
{
  "html": "<div style=\"font-size:48px;text-align:center\">Hallo PNG</div>",
  "width": 1000,
  "height": 600,
  "delay_ms": 200
}
```

### Beispiel-Response

```json
{
  "width": 1000,
  "height": 600,
  "delay_ms": 200,
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAA..."
}
```

`image_base64` ist direkt als Data-URL nutzbar (z. B. `<img src="...">`). Fuer Dateispeicherung den Base64-Anteil nach `data:image/png;base64,` dekodieren.
