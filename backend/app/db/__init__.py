# db/__init__.py

# Make the database connection function easily accessible
from backend.app.db.models import ExamDetectRule, ExamSession, LoginRequest, User, Examinee, MediaFiles, Verifications, Logs
from backend.app.db.models import EventData, EvnetLog
from backend.app.db.model_functions import user_crud, exam_session_crud, login_request_crud, examinee_crud
from backend.app.db.model_functions import verifications_crud, logs_crud, event_log_crud, MongoCRUD
from backend.app.db.database import lifespan

# You can define an __all__ variable to specify what gets imported with 'from . import *'
# This helps control the namespace and makes the package's API explicit.
__all__ = [
    # database.py
    'lifespan', "user_crud", "exam_session_crud", "login_request_crud", "examinee_crud",
    "ExamDetectRule", "ExamSession", "LoginRequest", "User", "Examinee", "MediaFiles", "Verifications", "Logs",
    "EventData", "EvnetLog", "verifications_crud", "logs_crud", "event_log_crud", "MongoCRUD"
]
