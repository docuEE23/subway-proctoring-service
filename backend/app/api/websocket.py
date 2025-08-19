from typing import Dict, Optional

import os, socketio
from bson import ObjectId
import jwt
from dotenv import load_dotenv
from backend.app.core import Payload, decode_jwt_token
from backend.app.db import Logs, LogContent, User
from backend.app.db import logs_crud, user_crud

load_dotenv()

JWT_SECRET: str = os.getenv("JWT_SECRET")
ALGORITHM: str = os.getenv("ALGORITHM")

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


async def get_user_from_token(token: str) -> Optional[User]:
    """Helper function to authenticate user from a JWT token."""
    if not token:
        return None
    payload : Payload = await decode_jwt_token(token)
    if payload.sub is None:
        return None
    return await user_crud.get(ObjectId(payload.sub))


async def log_event(user_id: str, log_type: str, url_path: str, content: Optional[LogContent] = None):
    """Helper to create and save a log entry."""
    user = await user_crud.get(ObjectId(user_id))
    if user:
        log_entry = Logs(
            user=user,
            log_type=log_type,
            url_path=url_path,
            content=content
        )
        await logs_crud.create(log_entry)


@sio.on("connect")
async def connect(sid, environ, auth: Dict):
    """Handle new client connections with authentication."""
    token = auth.get("token")
    exam_id = auth.get("exam_id")

    if not token or not exam_id:
        print(f"Connection rejected for sid {sid}: Missing token or exam_id.")
        return False  # Reject connection

    user = await get_user_from_token(token)
    if not user or not user.id:
        print(f"Connection rejected for sid {sid}: Invalid token.")
        return False  # Reject connection

    await sio.save_session(sid, {"user_id": str(user.id), "role": user.role, "exam_id": exam_id})
    await sio.enter_room(sid, room=exam_id)

    await log_event(str(user.id), "WEBSOCKET_CONNECTED", f"/ws/signal/{exam_id}")
    print(f"Client connected: {sid}, User: {user.id}, Exam: {exam_id}")
    return True


@sio.on("disconnect")
async def disconnect(sid):
    """Handle client disconnections."""
    session = await sio.get_session(sid)
    if session:
        user_id = session.get("user_id")
        exam_id = session.get("exam_id")
        await log_event(user_id, "WEBSOCKET_DISCONNECT", f"/ws/signal/{exam_id}")
        print(f"Client disconnected: {sid}, User: {user_id}, Exam: {exam_id}")


@sio.on("webrtc-offer")
async def handle_webrtc_offer(sid, data: Dict):
    """Handle WebRTC offer from an examinee and forward it to the proctor."""
    session = await sio.get_session(sid)
    if not session:
        return await sio.emit("error", {"message": "Authentication failed."}, to=sid)

    exam_id = session["exam_id"]
    user_id = session["user_id"]
    role = session.get("role")

    # Offers should come from examinees
    if role != "examinee":
        return None

    # Find the proctor in the same exam room
    proctor_sid = None
    for other_sid in sio.rooms(exam_id):
        if other_sid != sid:
            other_session = await sio.get_session(other_sid)
            if other_session and other_session.get("role") == "proctor":
                proctor_sid = other_sid
                break

    if proctor_sid:
        # Forward the offer to the proctor, including the sender's user_id
        await sio.emit("webrtc-offer", {"offer": data, "from_user_id": user_id}, to=proctor_sid)
        return None
    else:
        await sio.emit("error", {"message": "Proctor not found in the exam room."}, to=sid)
        return None


@sio.on("webrtc-answer")
async def handle_webrtc_answer(sid, data: Dict):
    """Handle WebRTC answer from a proctor and forward it to the correct examinee."""
    session = await sio.get_session(sid)
    if not session or session.get("role") != "proctor":
        return await sio.emit("error", {"message": "Authentication failed or not a proctor."}, to=sid)

    exam_id = session["exam_id"]
    target_user_id = data.get("to_user_id")
    answer = data.get("answer")

    if not target_user_id or not answer:
        return await sio.emit("error", {"message": "Missing target user ID or answer payload."}, to=sid)

    # Find the examinee's SID
    examinee_sid = None
    for other_sid in sio.rooms(exam_id):
        other_session = await sio.get_session(other_sid)
        if other_session and other_session.get("user_id") == target_user_id:
            examinee_sid = other_sid
            break

    if examinee_sid:
        # Forward the answer to the examinee
        await sio.emit("webrtc-answer", {"answer": answer}, to=examinee_sid)
        return None
    else:
        await sio.emit("error", {"message": f"Examinee {target_user_id} not found."}, to=sid)
        return None


@sio.on("webrtc-ice-candidate")
async def handle_ice_candidate(sid, data: Dict):
    """Handle and forward ICE candidates between peers (examinee and proctor)."""
    session = await sio.get_session(sid)
    if not session:
        return await sio.emit("error", {"message": "Authentication failed."}, to=sid)

    exam_id = session["exam_id"]
    target_user_id = data.get("to_user_id")
    candidate = data.get("candidate")

    if not target_user_id or not candidate:
        return await sio.emit("error", {"message": "Missing target user ID or ICE candidate."}, to=sid)

    # Find the target peer's SID
    target_sid = None
    for other_sid in sio.rooms(exam_id):
        other_session = await sio.get_session(other_sid)
        if other_session and other_session.get("user_id") == target_user_id:
            target_sid = other_sid
            break

    if target_sid:
        # Forward the ICE candidate, including the sender's user_id
        await sio.emit(
            "webrtc-ice-candidate",
            {"candidate": candidate, "from_user_id": session["user_id"]},
            to=target_sid,
        )
        return None
    return None


@sio.on("message")
async def handle_message(sid, data: Dict):
    """Handle incoming messages, either personal or broadcast."""
    session = await sio.get_session(sid)
    if not session:
        await sio.emit("error", {"message": "Authentication failed."}, to=sid)
        return

    exam_id = session["exam_id"]
    sender_id = session["user_id"]
    target_user_id = data.get("user_id")

    if target_user_id:
        # Personal message
        target_sid = None
        # Find the sid of the target user in the same exam room
        for other_sid in sio.rooms(exam_id):
            other_session = await sio.get_session(other_sid)
            if other_session and other_session.get("user_id") == target_user_id:
                target_sid = other_sid
                break

        if target_sid:
            await sio.emit("message", data, to=target_sid)
            log_content = LogContent(content=data.get("content", ""), user_ids=[target_user_id])
            await log_event(sender_id, "MESSAGE_TO_EXAMINEE", f"/ws/signal/{exam_id}", content=log_content)
        else:
            print(f"Error: User {target_user_id} not found in exam {exam_id}")
            await sio.emit("error", {"message": f"User {target_user_id} not found."}, to=sid)
    else:
        # Broadcast message to everyone in the exam room except the sender
        await sio.emit("message", data, room=exam_id, skip_sid=sid)
        
        # For logging, get all user IDs in the room
        all_user_ids = []
        for other_sid in sio.rooms(exam_id):
            other_session = await sio.get_session(other_sid)
            if other_session:
                all_user_ids.append(other_session.get("user_id"))
        
        log_content = LogContent(content=data.get("content", ""), user_ids=all_user_ids)
        await log_event(sender_id, "MESSAGE_TO_ALL_EXAMINEE", f"/ws/signal/{exam_id}", content=log_content)

# General error handler
@sio.on("*")
async def catch_all(event, sid, data):
    session = await sio.get_session(sid)
    if session:
        user_id = session.get("user_id")
        exam_id = session.get("exam_id")
        error_content = LogContent(content=f"Unhandled event '{event}' with data: {data}", user_ids=[])
        await log_event(user_id, "WEBSOCKET_ON_ERROR", f"/ws/signal/{exam_id}", content=error_content)
    print(f"Unhandled event for sid {sid}: {event} - {data}")
