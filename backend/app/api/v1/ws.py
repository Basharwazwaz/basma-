"""
WebSocket router for real-time notifications and chat.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.services.websocket_manager import manager

router = APIRouter()


async def _get_user_id_from_token(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except Exception:
        return None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = await _get_user_id_from_token(websocket)
    if not user_id:
        await websocket.close(code=4001)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Keep-alive ping/pong or future message handling
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)
