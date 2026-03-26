import asyncio

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app.core.security import decode_access_token, is_token_error
from app.db import get_db
from app.models.user import User as UserModel
from app.realtime import manager

router = APIRouter(tags=['realtime'])


def authenticate_websocket(token: str, db: Session) -> UserModel:
    try:
        payload = decode_access_token(token)
        subject = payload.get('sub')
        if subject is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Invalid authentication token')
        user_id = int(subject)
    except Exception as error:
        if is_token_error(error) or isinstance(error, ValueError):
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Invalid authentication token') from error
        raise

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Authenticated user not found')
    return user


async def wait_for_disconnect(websocket: WebSocket):
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        return


@router.websocket('/ws/project-management')
async def project_management_websocket(
    websocket: WebSocket,
    token: str = Query(),
    db: Session = Depends(get_db),
):
    authenticate_websocket(token, db)
    channel = 'project-management'
    queue = await manager.connect(channel, websocket)
    await websocket.send_json({'type': 'connected', 'channel': channel})
    disconnect_task = asyncio.create_task(wait_for_disconnect(websocket))
    try:
        while True:
            get_message_task = asyncio.create_task(queue.get())
            done, pending = await asyncio.wait(
                {get_message_task, disconnect_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if disconnect_task in done:
                return

            message = get_message_task.result()
            await websocket.send_json(jsonable_encoder(message))
    finally:
        disconnect_task.cancel()
        manager.disconnect(channel, queue)
