# db/__init__.py

# Make the database connection function easily accessible
from backend.app.db.models import ExamDetectRule, ExamSession, LoginRequest, User, Examinee, MediaFiles, Verifications, Logs
from backend.app.db.models import EventData, EventLog, Exam, Schedule, ExamContent, ExamQuestion, LogContent
from backend.app.db.models import ExamQuestionTitle, ExamQuestionBody, ExamQuestionSelection, FinalReport
from backend.app.db.database import lifespan
from backend.app.db.model_functions import user_crud, exam_session_crud, login_request_crud, examinee_crud
from backend.app.db.model_functions import verifications_crud, logs_crud, event_log_crud, MongoCRUD
from backend.app.db.model_functions import exam_crud

# You can define an __all__ variable to specify what gets imported with 'from . import *'
# This helps control the namespace and makes the package's API explicit.
__all__ = [
    # database.py
    'lifespan', "user_crud", "exam_session_crud", "login_request_crud", "examinee_crud",
    "ExamDetectRule", "ExamSession", "LoginRequest", "User", "Examinee", "MediaFiles", "Verifications", "Logs",
    "EventData", "EventLog", "verifications_crud", "logs_crud", "event_log_crud", "MongoCRUD",
    "ExamQuestionTitle", "ExamQuestionBody", "ExamQuestionSelection", "FinalReport",
    "Exam", "Schedule", "ExamContent", "ExamQuestion", "exam_crud", "LogContent"
]
