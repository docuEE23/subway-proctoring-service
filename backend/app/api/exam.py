from fastapi import APIRouter, Depends, HTTPException
from backend.app.db.models import Exam, User, ExamSession
from backend.app.db.model_functions import exam_crud, exam_session_crud
from backend.app.core.utils import AuthenticationChecker
from typing import List

exam_router = APIRouter()


@exam_router.get(
    "/admin", response_model=List[Exam],
    dependencies=[Depends(AuthenticationChecker(role=["admin"]))]
)
async def get_exams_for_admin():
    """
    Returns all existing Exam information for an admin.
    """
    return await exam_crud.get_all(limit=1000)  # Increased limit to fetch more exams if needed


@exam_router.get("/supervisor", response_model=List[ExamSession])
async def get_exams_for_supervisor(user_info: User = Depends(AuthenticationChecker(role=['supervisor']))):
    """
    Returns Exam information for which the supervisor is assigned as a proctor.
    """
    # Find sessions where the current supervisor is a proctor
    return  await exam_session_crud.get_all(query={"proctor_ids": str(user_info.id)}, limit=1000)


@exam_router.get("/examinee", response_model=List[ExamSession])
async def get_exams_for_examinee(user_info: User = Depends(AuthenticationChecker(role=['examinee']))):
    """
    Returns Exam information for which the examinee is an expected participant.
    """
    return await exam_session_crud.get_all(query={
            "exam.expected_examinees.id": user_info.id
        }, limit=1000
    )

@exam_router.get(
    "/admin/get_exam/{exam_id}", response_model=Exam,
    dependencies=[Depends(AuthenticationChecker(role=["admin"]))]
)
async def get_exam_for_admin(exam_id: str):
    """
    Returns a single Exam object for an admin.
    """
    exam = await exam_crud.get(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

# await axios.post(`/${examId}/submit`, formattedAnswers); -> 이것도 처리하는 거 필요