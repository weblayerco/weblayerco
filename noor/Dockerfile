# Single-image build: compile the frontend, then serve it + the assessment API
# from one FastAPI process. Build context must be the `noor/` directory.

# --- Stage 1: build the frontend ---------------------------------------------
FROM node:22-alpine AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY public ./public
COPY src ./src
# Same-origin API path: the served app calls /assess on its own host.
ENV VITE_ASSESS_URL=/assess
RUN npm run build

# --- Stage 2: python runtime that serves API + built app ---------------------
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY server/app ./app
COPY server/references ./references
COPY --from=frontend /app/dist ./dist

ENV NOOR_STATIC_DIR=/app/dist \
    NOOR_REFERENCES_DIR=/app/references \
    NOOR_ENGINE=auto \
    PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
