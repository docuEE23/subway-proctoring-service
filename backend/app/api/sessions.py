from backend.app.core import AuthenticationChecker
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from backend.app.db import exam_crud, exam_session_crud, user_crud, examinee_crud
from uuid import uuid4
from pydantic import BaseModel
from backend.app.db import ExamDetectRule, ExamSession, User, Examinee, Exam
from backend.app.db import Logs, logs_crud


session_router = APIRouter(prefix="/session")


class CreateSessionBody(BaseModel):
    exam_id: str
    detect_rule: ExamDetectRule


@session_router.post(
    "/create_session", summary="시험 세션 생성"
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
    exam: Exam | None = await exam_crud.get_by({"exam_id" : body.exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 세션을 생성하기 전에 exam_session_crud를 통해 현재의 exam_id 값을 가진 ExamSession 이 존재하진 않는지 확인하세요.
    # 만약 존재한다면 해당 ExamSession 의 session_id 값을 반환 하세요.
    existing_session_for_exam : ExamSession | None = await exam_session_crud.get_by({"exam_id" : body.exam_id})
    if existing_session_for_exam:
        response.set_cookie(key="session_id", value=existing_session_for_exam.session_id)
        return {"session_id": existing_session_for_exam.session_id}

    expected_examinees: list[User] = []
    for eei in exam.expected_examinee_ids:
        a_user : User | None = await user_crud.get_by({"user_id" : eei})
        if a_user is None:
            raise HTTPException(status_code=404, detail="Not all expected examinees were found in the User collection.")
        expected_examinees.append(a_user.to_ref())

    if len(expected_examinees) != len(exam.expected_examinee_ids):
        raise HTTPException(status_code=404, detail="Not all expected examinees were found in the User collection.")

    if not all([exam.exam_title, exam.proctor_id, expected_examinees]):
        raise HTTPException(status_code=400, detail="Missing required data from Exam or User to create a session")

    new_session_id = str(uuid4())
    new_session = ExamSession(
        session_id=new_session_id,
        exam_title=exam.exam_title,
        exam_id=body.exam_id,
        proctor_id=exam.proctor_id,
        expected_examinee=expected_examinees,
        detect_rule=body.detect_rule,
        session_status='draft'
    )
    await exam_session_crud.create(new_session)
    log = Logs(user_id=user.to_ref(),url_path="/session/create_session", log_type="SESSION_CREATED")
    await logs_crud.create(log)

    response.set_cookie(key="session_id", value=new_session_id)
    return {"session_id": new_session_id}


class JoinSessionBody(BaseModel):
    session_id: str


@session_router.post("/join_session", summary="시험 세션 참여")
async def join_session(
    response: Response,
    body: JoinSessionBody,
    current_user: User = Depends(AuthenticationChecker(role=["examinee"]))
):
    # ## 시험 세션 참여
    # endpoint : POST "/join_session"
    # join_session 메서드는 body 로 session_id 를 받고, AuthenticationChecker(role=["examinee"]) 를 통해 인증된 사용자 정보를 받습니다.

    # 먼저 body 로 들어온 session_id 를 통해 ExamSession 이 존재하는지 확인합니다.
    # 없다면 에러를 발생시킵니다.
    session : ExamSession | None = await exam_session_crud.get_by({"session_id": body.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 그 다음, 해당 세션의 상태(session_status)가 'ready' 인지 확인합니다.
    # 'ready' 상태가 아니라면 에러를 발생시킵니다.
    if session.session_status != 'ready':
        raise HTTPException(status_code=400, detail="Session is not ready to be joined")


    expected_user_ids = [linked_user.ref.id for linked_user in session.expected_examinee]
    if current_user.id not in expected_user_ids:
        raise HTTPException(status_code=403, detail="User is not an expected examinee for this session.")

    # examinee_crud 를 사용하여 이미 해당 세션에 참여한 응시자인지 확인합니다.
    # 이미 참여했다면, 해당 정보를 반환합니다.
    existing_examinee : Examinee | None = await examinee_crud.get_by(
        {'session_id': body.session_id, 'examinee': current_user.to_ref()}
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
        examinee=current_user.to_ref(),
        status='connected'
    )

    # 생성된 Examinee 문서를 DB에 저장하고, 성공 메시지를 반환합니다.
    await examinee_crud.create(new_examinee)
    # 세션 참여에 대한 로그를 남깁니다.
    log = Logs(user_id=current_user.to_ref(), url_path="/session/join_session", log_type="JOIN_SESSION")
    await logs_crud.create(log)

    # session_id 를 쿠키에 넣어 보냅니다.
    response.set_cookie(key="session_id", value=session.session_id)
    return {"message": "Successfully joined the session."}
