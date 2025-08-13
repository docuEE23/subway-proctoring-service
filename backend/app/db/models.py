from datetime import datetime
from beanie import Document, Link
from typing import Optional , Literal
from pydantic import BaseModel, Field


class User(Document):
    """
    사용자(응시자, 감독관, 관리자)의 기본 정보를 저장합니다.
    """
    user_id: str
    name: str = Field(description="사용자 이름")
    role: Literal['examinee', 'supervisor', 'admin'] = Field(description="사용자 역할 ")
    pwd: str = Field(description="암호화된 비번")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")

    class Settings:
        name = "users"
        validate_on_save = True
        indexes : list = [
            "user_id", "name", "role"
        ]

class ExamDetectRule(BaseModel):
    """
    부정 행위를 탐지할 방법 선택
    """
    detect_gaze_off_screen: bool
    detect_window_switch: bool
    detect_prohibited_items: bool
    detect_multiple_faces: bool
    detect_audio_noise: bool


class ExamSession(Document):
    """
    생성된 시험에 대한 정보.
    """
    session_id: str = Field(description="세션 고유 ID")
    exam_title: str = Field(description="시험 제목")
    exam_id: str = Field(description="연결된 시험의 ID")
    proctor_id: str = Field(description="담당 감독관의 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="세션 생성 일시")
    expected_examinee: list[Link['User']]
    detect_rule: ExamDetectRule
    session_status: Literal['draft', 'ready', 'in_progress', 'paused', 'completed', 'archived']

    class Settings:
        name = "exam_sessions"
        validate_on_save = True
        indexes : list = [
            "session_id", "exam_id", "proctor_id"
        ]



class LoginRequest(Document):
    """
    로그인 요청 추적 용도. 10 분에 최대 5 번 로그인 요청이 가능하다.
    로그인 요청이 올 때마다 request_count 가 증가한다.
    last_request_time 과 현재 datetime 을 비교해서 10 분이 지났다면 1 로 초기화 한다.
    """
    request_id: str
    last_request_time: datetime
    request_count: int

class Examinee(Document):
    """
    세션에 참여한 응시자에 대한 정보
    """
    session_id: str = Field(description="참여한 시험 세션 ID")
    examinee: Link["User"]
    exam_id: str
    join_time: datetime = Field(default_factory=datetime.now, description="응시자 참여 시간")
    status: Literal["connected", "disconnected", "active", "inactive"]
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name="examinee"
        validate_on_save = True
        indexes : list = [
            "session_id", "exam_id", "status"
        ]


class MediaFiles(BaseModel):
    media_type: Literal['face_snapshot', 'id_card_front', 'desk_view']
    media_url: str

class Verifications(Document):

    exam_id: str
    examinee_id: Link["Examinee"] = Field(description="로그를 생성한 id")
    status: Literal["pending", "approved", "rejected"]
    media_files: list[MediaFiles]
    proctor_id: Optional[str] = None
    proctor_decision: Optional[Literal["approved", "rejected"]] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name="verifications"
        validate_on_save = True
        indexes : list = [
            "proctor_id", "exam_id", "status"
        ]


class LogContent(BaseModel):
    content: str
    user_ids: list[str]

class Logs(Document):
    """
    Represents a log entry in the database.
    """
    user_id: Link["User"] = Field(description="로그를 생성한 id")
    generated_at: datetime = Field(default_factory=datetime.now, description="로그 생성 일시")
    url_path: str = Field(description="The URL path of the request that generated the log.", min_length=1)
    log_type: str = Field(description="The type of log (e.g., VERIFY_REJECT, EXAM_START).", min_length=1)
    content: Optional[LogContent] = None

    class Settings:
        name = "logs"
        validate_on_save = True
        indexes : list = [
            "user_id", "log_type"
        ]

class EventData(BaseModel):
    message: str
    details: Optional[dict] = None

class EvnetLog(Document):
    """
    A log of all detected cheating events (by AI) and significant actions (by proctors). This is the source for the final report.
    """
    user_id: Link["User"]
    exam_id: str
    generated_at: datetime = Field(default_factory=datetime.now, description="The exact time the event occurred.")
    event_type: Literal['gaze_off_screen', 'window_switch', 'prohibited_item_detected', 'proctor_snapshot', 'manual_flag']
    severity: Literal['low', 'medium', 'high', 'critical']
    content: EventData = Field(description="A detailed description of the event.")
    is_dismissed : bool = Field(description="`true` if a proctor reviewed and dismissed the event.")
    screenshot_url: str = Field(description="URL to the evidence snapshot stored in the cloud.")

    class Settings:
        name = "event_logs"
        validate_on_save = True
        indexes : list = [
            "user_id", "severity", "event_type", "is_dismissed"
        ]


class FinalReport(Document):
    exam_id: str
    target_user_id: str = Field(description="보고서 대상의 user_id")
    created_datetime: datetime = Field(default_factory=datetime.now, description="보고서 생성 일시")
    report_url: str = Field(description="생성된 보고서가 위치한 경로")

class ExamQuestionSelection(BaseModel):
    selection_id: str = Field(description="시험 문항에 있는 선택지 아이디", min_length=5)
    selection_index: int = Field(description="선택지 인덱스 위치", gt=0)
    selection_content: str = Field(description="선택지 내용", min_length=1)

class ExamQuestionBody(BaseModel):
    question_id: str = Field(description="시험 문항 아이디", min_length=5)
    body_base64: str = Field(description="시험 문항에 있는 '보기' 이미지를 base64 로 저장한 값.", min_length=10)

class ExamQuestionTitle(BaseModel):
    question_id: str = Field(description="시험 문항 아이디", min_length=5)
    title_content: str = Field(description="시험 문항의 제목", min_length=5)

class ExamQuestion(BaseModel):
    question_id: str = Field(description="시험 문항 아이디", min_length=5)
    question_index: int = Field(description="시험 문항 인덱스", gt=0)
    title: ExamQuestionTitle
    bodies: list[ExamQuestionBody]
    selections: list[ExamQuestionSelection]

class ExamContent(BaseModel):
    exam_content_id: str
    schedule_id: str
    exam_id: str
    questions: list[ExamQuestion]

class Schedule(BaseModel):
    schedule_id: str
    exam_id: str
    schedule_index: int
    start_datetime: datetime
    end_datetime: datetime
    content_id: str

class Exam(Document):

    exam_title: str = Field(description="시험 제목")
    exam_id: str = Field(description="연결된 시험의 ID")
    proctor_id: str = Field(description="담당 감독관의 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="시험 정보 생성 일시")
    exam_start_datetime: datetime
    exam_end_datetime: datetime
    schedules: list[Schedule]
    contents: list[ExamContent]
    expected_examinee_ids: list[str]