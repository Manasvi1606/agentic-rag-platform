"""FastAPI entrypoint. Wires routers + middleware. Run with:

    uvicorn api.main:app --reload

This is glue and is essentially complete — the substance lives in the route
handlers and the retrieval/agent layers they call.
"""
from __future__ import annotations

from fastapi import FastAPI

from api.middleware.logging import RequestLoggingMiddleware
from api.routes import conversation, documents, query


def create_app() -> FastAPI:
    app = FastAPI(
        title="Enterprise AI Research & Intelligence Platform",
        version="0.1.0",
    )

    # TODO(you): add CORS, auth, and rate-limiting middleware before this is
    # exposed anywhere real. The security suite's services checklist covers the
    # auth/CORS/rate-limit patterns — apply them when you build the handlers.
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(query.router)
    app.include_router(documents.router)
    app.include_router(conversation.router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
