FROM python:3.13-slim

ARG REPO_URL=https://github.com/speetzial/HTMLtoIMG
ARG REPO_REF=main
ENV APP_DIR=/srv/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git chromium \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -ms /bin/bash appuser

RUN git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${APP_DIR}"
WORKDIR ${APP_DIR}

ENV HTML2IMAGE_CHROME_PATH=/usr/bin/chromium \
    CHROME_PATH=/usr/bin/chromium

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && chown -R appuser:appuser ${APP_DIR}

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
