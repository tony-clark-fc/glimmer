"""Glimmer backend — direct-run entrypoint.

Allows starting the backend with:

    python -m app

Uses the host/port from Settings so the server automatically binds
to the configured network address (0.0.0.0 for LAN/VPN access).
"""

from __future__ import annotations

import uvicorn

from app.config import get_settings


def main() -> None:
    """Start the Glimmer backend using configured host and port."""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()

