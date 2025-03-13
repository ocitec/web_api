from fastapi import WebSocket, APIRouter

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Flight status updated!")
    await websocket.close()
