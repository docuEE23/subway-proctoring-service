from backend.app.core import AuthenticationChecker
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.app.db import exam_crud, exam_session_crud, user_crud
from uuid import uuid4
from pydantic import BaseModel
from backend.app.db import ExamDetectRule, ExamSession, User, Exam, Examinee


session_router = APIRouter(prefix="/session")


class CreateSessionBody(BaseModel):
    exam_id: str
    detect_rule: ExamDetectRule


@session_router.post(
    "/create_session", summary="시험 세션 생성",
    dependencies=[Depends(AuthenticationChecker(role=["admin"]))]
)
async def create_session(
    request: Request,
    body: CreateSessionBody
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
        return {"session_id": existing_session_for_exam.session_id}

    expected_examinees: list[User] = []
    for eei in exam.expected_examinee_ids:
        a_user : User | None = await user_crud.get_by({"user_id" : eei})
        if a_user is None:
            raise HTTPException(status_code=404, detail="Not all expected examinees were found in the User collection.")
        expected_examinees.append(a_user)

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
    return {"session_id": new_session_id}


"""
## 요청 : 
### 응시자의 시험 참여를 위한 join_exam_session 메서드를 작성해주세요.
endpoint : GET /join_exam_session/{exam_id}.
user_info : UserInfo = Depends(AuthenticationChecker(role=["examinee"])) 값을 매개변수로 받으세요.

응시자를 참여시키기 전, 쿠키에 session_id가 있는지 확인하세요. 있다면 에러를 발생시키세요.
exam_id 로 exam_session_crud 에서 얻은 expected_examinee를 가져오세요. 만약 exam_session_crud 에서 exam_id 값으로 ExamSession 을 가져올 수 없다면 에러를 발생시키세요.


session_id 를 반환하시면 됩니다.
"""