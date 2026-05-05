"""
token_server.py — Minimal FastAPI token endpoint for LiveKit
─────────────────────────────────────────────────────────────
Bubble calls this endpoint to get a short-lived JWT before joining the room.

Run:
    uvicorn token_server:app --host 0.0.0.0 --port 8000

GET /token?room=lead-logger-room&identity=cre-abc123
Returns: { "token": "<jwt>" }
"""

import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LiveKit Token Server")

# Allow Bubble (and localhost dev) to call this endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to your Bubble domain in production
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/token")
async def get_token(
    room: str = Query(..., description="LiveKit room name"),
    identity: str = Query(..., description="Participant identity"),
):
    api_key    = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")

    if not api_key or not api_secret:
        raise HTTPException(status_code=500, detail="LiveKit credentials not configured")

    token = (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    return {"token": token, "room": room, "identity": identity}
