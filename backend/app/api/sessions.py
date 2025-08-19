from backend.app.core import AuthenticationChecker
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from backend.app.db import exam_crud, exam_session_crud, user_crud, examinee_crud
from uuid import uuid4
from pydantic import BaseModel
from backend.app.db import ExamDetectRule, ExamSession, User, Examinee, Exam
from backend.app.db import Logs, logs_crud
from typing import Annotated

session_router = APIRouter()


class CreateSessionBody(BaseModel):
    exam_id: str
    detect_rule: ExamDetectRule


@session_router.post(
    "/create_session", summary="관리자 시험 세션 생성"
)
async def create_session(
    request: Request,
    response: Response,
    body: CreateSessionBody,
    user: User = Depends(AuthenticationChecker(role=["admin"]))
):
    session_id_from_cookie = request.cookies.get("session_id") # 쿠키로 있는 session_id 확인
    if session_id_from_cookie:
        # 실제로 session_id 값이 있는지 확인
        existing_session : ExamSession | None = await exam_session_crud.get_by({"session_id" : session_id_from_cookie})
        if existing_session:
            return {"session_id": existing_session.session_id}
    # Exam 컬렉션에 body 로 들어온 exam_id 가 존재하는지 확인
    exam: Exam | None = await exam_crud.get_by({"_id" : body.exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 세션을 생성하기 전에 exam_session_crud를 통해 현재의 exam_id 값을 가진 ExamSession 이 존재하진 않는지 확인하세요.
    # 만약 존재한다면 해당 ExamSession 의 session_id 값을 반환 하세요.
    existing_session_for_exam : ExamSession | None = await exam_session_crud.get_by({"exam_id" : body.exam_id})
    if existing_session_for_exam:
        response.set_cookie(key="session_id", value=existing_session_for_exam.session_id)
        return {"session_id": existing_session_for_exam.session_id}

    new_session_id = str(uuid4())
    new_session = ExamSession(
        session_id=new_session_id,
        exam=exam,
        proctor_ids=exam.proctor_ids,
        detect_rule=body.detect_rule,
        session_status='draft'
    )
    await exam_session_crud.create(new_session)
    log = Logs(user=user, url_path="/session/create_session", log_type="SESSION_CREATED")
    await logs_crud.create(log)

    response.set_cookie(key="session_id", value=new_session_id)
    return {"session_id": new_session_id}


@session_router.post("/join_session/{exam_id}", summary="응시자 시험 세션 참여")
async def examinee_join_session(
    exam_id: str,
    response: Response,
    session_id: Annotated[str | None, Cookie()] = None,
    current_user: User = Depends(AuthenticationChecker(role=["examinee"]))
):
    # ## 시험 세션 참여
    # endpoint : POST "/join_session"
    # AuthenticationChecker(role=["examinee"]) 를 통해 인증된 사용자 정보를 받습니다.

    # exam_id 를 통해 ExamSession 을 가져옵니다 만약 없다면 에러를 냅니다.
    session : ExamSession | None = await exam_session_crud.get_by({"exam_id": exam_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 그 다음, 해당 세션의 상태(session_status)가 'ready' 인지 확인합니다.
    # 'ready' 상태가 아니라면 에러를 발생시킵니다.
    if session.session_status != 'ready':
        raise HTTPException(status_code=400, detail="Session is not ready to be joined")

    # 시험 응시자 명단에 존재하지 않을 경우 에러를 발생.
    expected_user_ids = [str(linked_user.id) for linked_user in session.exam.expected_examinees]
    if str(current_user.id) not in expected_user_ids:
        raise HTTPException(status_code=403, detail="User is not an expected examinee for this session.")

    if session_id is not None and session.session_id == session_id:
        # examinee_crud 를 사용하여 이미 해당 세션에 참여한 응시자인지 확인합니다.
        # 이미 참여했다면, 해당 정보를 반환합니다.
        existing_examinee : Examinee | None = await examinee_crud.get_by(
            {'session_id': session_id, 'examinee._id': current_user.id}
        )
        if existing_examinee:
            return {"message": "User has already joined the session.", "examinee_info": existing_examinee.model_dump_json()}

    # 모든 검증을 통과했다면, 새로운 Examinee 문서를 생성합니다.
    # 필요한 필드(session_id, exam_id, examinee, status)를 채워서 생성합니다.
    # status 는 'connected' 로 설정합니다.
    # examinee 필드는 인증된 사용자의 User 객체입니다.
    new_examinee = Examinee(
        session_id=session.session_id,
        exam_id=session.exam_id,
        examinee=current_user,
        status='connected'
    )

    # 생성된 Examinee 문서를 DB에 저장하고, 성공 메시지를 반환합니다.
    await examinee_crud.create(new_examinee)
    # 세션 참여에 대한 로그를 남깁니다.
    log = Logs(user=current_user, url_path="/session/join_session", log_type="JOIN_SESSION")
    await logs_crud.create(log)

    # session_id 를 쿠키에 넣어 보냅니다.
    response.set_cookie(key="session_id", value=session.session_id)
    return {"message": "Successfully joined the session."}


@session_router.get("/supervisor_join_session/{exam_id}", summary="감독관 시험 참여 및 세션 준비")
async def supervisor_join_session(
    exam_id: str,
    response: Response,
    current_user: User = Depends(AuthenticationChecker(role=["supervisor"])),
    session_id: Annotated[str | None, Cookie()] = None,
):
    session: ExamSession | None = None

    # 1. 쿠키에 있는 session_id로 세션을 찾아봅니다.
    if session_id:
        session = await exam_session_crud.get_by({"session_id": session_id})
        # 쿠키의 세션 ID가 다른 시험의 것이라면 무시합니다.
        if session and session.exam_id != exam_id:
            session = None

    # 2. 쿠키로 세션을 찾지 못했다면, 경로의 exam_id로 세션을 찾아봅니다.
    if not session:
        session = await exam_session_crud.get_by({"exam_id": exam_id})

    # 3. 세션을 여전히 찾을 수 없다면, 이 시험에 대한 세션이 존재하지 않는 것입니다.
    if not session:
        raise HTTPException(status_code=404, detail="시험 세션을 찾을 수 없습니다. 감독관은 세션을 생성할 수 없습니다.")

    # 4. 감독관이 이 세션에 배정되었는지 확인합니다.
    if str(current_user.id) not in session.proctor_ids:
        raise HTTPException(status_code=403, detail="이 시험 세션에 배정된 감독관이 아닙니다.")

    # 5. 세션 상태가 참여 가능한지 확인합니다.
    if session.session_status not in ['draft', 'ready']:
        raise HTTPException(
            status_code=400,
            detail=f"세션에 참여할 수 있는 상태가 아닙니다. 현재 상태: {session.session_status}"
        )

    # 6. 세션이 'draft' 상태이면 'ready'로 업데이트합니다.
    if session.session_status == 'draft':
        await session.update({"$set": {"session_status": "ready"}})

        # 세션 준비 완료 로그를 생성합니다.
        log = Logs(
            user=current_user.to_ref(),
            url_path=f"/session/supervisor_join_session/{exam_id}",
            log_type="SESSION_READY"
        )
        await logs_crud.create(log)

        # 쿠키에 session_id를 설정하고 반환합니다.
        response.set_cookie(key="session_id", value=session.session_id)
        return {"message": "세션이 준비되었습니다.", "session_id": session.session_id}

    # 7. 세션이 이미 'ready' 상태이면, 참여 완료를 확인합니다.
    response.set_cookie(key="session_id", value=session.session_id)
    return {"message": "성공적으로 참여했습니다. 세션은 이미 준비 상태였습니다.", "session_id": session.session_id}
