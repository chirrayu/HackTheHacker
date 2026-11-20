import os
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import setup_logging
from app.database.connection import init_db
from app.api.routes import (
    health,
    events,
    alerts,
    attacks,
    assets,
    analytics,
    intelligence,
    reports,
    ingestion,
    sensors
)

settings = get_settings()
logger = setup_logging(settings.LOG_LEVEL, log_dir=settings.LOG_DIR)

# WebSocket Connection Manager for Live SOC Alert Broadcasting
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead_sockets = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_sockets.add(connection)
        for s in dead_sockets:
            self.active_connections.discard(s)

ws_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure logging and database tables are initialized
    logger.info("Initializing HACK THE HACKER Platform Backend...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield
    # Shutdown
    logger.info("HACK THE HACKER Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional VM-Based Cyber Threat Monitoring & Intelligence Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],  # Permits local React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api/v1
API_PREFIX = "/api/v1"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(alerts.router, prefix=API_PREFIX)
app.include_router(attacks.router, prefix=API_PREFIX)
app.include_router(assets.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(intelligence.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(ingestion.router, prefix=API_PREFIX)
app.include_router(sensors.router, prefix=API_PREFIX)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs",
        "api_v1_prefix": API_PREFIX
    }

# Live Alerts WebSocket Endpoint
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
