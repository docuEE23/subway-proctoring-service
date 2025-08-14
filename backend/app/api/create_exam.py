from fastapi import APIRouter, UploadFile, File
from backend.app.db import Exam, User, user_crud, exam_crud, ExamQuestionSelection
import secrets

exam_create_router = APIRouter()


async def create_dummy_user_infos():
    dummy_user_info: list[dict] = [
        {"name" : "한예슬", "email" : "example@xxx.co.kr"},
        {"name" : '박상훈', "email" : "example1@xxx.co.kr"},
        {"name" : "박지성", "email" : "example2@xxx.com"}
    ]
    for dui in dummy_user_info:
        dummy_pwd: str = "pwd_" + secrets.token_urlsafe(25)
        dummy_user: User = User( email=dui.get("email"),
            name=dui.get("name"), role="examinee", pwd=dummy_pwd
        )
        await user_crud.create(dummy_user)
    return

"""
# 요청 : 시험 정보와 응시자 정보가 담긴 파일을 프론트엔드로 부터 받고 이를 가공하여 exam_crud, user_crud 에 저장하는 create_exam 이라는 메서드를 작성해주세요.
endpoint : POST /create_exam
예상 매개변수 : 
    current_user: User = Depends(AuthenticationChecker(role=["admin"]))
    exam_infos: ExamInfos(pydantic.BaseModel로 exam_title, start_datetime, end_datetime, proctor_ids 에 대한 필드가 존재해야 합니다)
    examinee_infos: UploadFile = File(...)
    examination_paper: UploadFile = File(...)

examinee_infos 로 들어올 파일에는 시험에 참여하는 응시자들의 이름과 이메일이 적혀 있습니다.
examination_paper 은 시험지입니다.

examinee_infos 와 examination_paper 로 받은 파일을 파싱하는 메서드는 아직 구현된 상태가 아닙니다. 그러므로, 가상의 메서드를 
"""