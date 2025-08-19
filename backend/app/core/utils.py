from datetime import datetime, timedelta, UTC
import jwt, os
from typing import List, Literal
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from backend.app.db import user_crud, User
import csv, uuid
from io import StringIO
from pydantic import BaseModel, Field

load_dotenv()
JWT_SECRET: str = os.getenv("JWT_SECRET")
ALGORITHM: str = os.getenv("ALGORITHM")


class Payload(BaseModel):
    sub: str = Field(description="user_id", min_length=2)
    role: str = Field(description="user_role", min_length=2)
    exp: datetime = Field(description="expire datetime")

def create_jwt(user_id: str, role: str, expires_delta: timedelta) -> tuple[str, datetime]:
    """JWT를 생성하고 만료 시간을 반환합니다."""
    expire = datetime.now(UTC) + expires_delta
    payload = Payload(sub=user_id, role=role, exp=expire)
    token = jwt.encode(payload.model_dump(), JWT_SECRET, algorithm=ALGORITHM)
    return token, expire


async def decode_jwt_token(jwt_token: str) -> Payload:
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(status_code=401, detail="Token has expired")
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        return Payload(sub=user_id, role=user_role, exp=payload["exp"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



class AuthenticationChecker:
    """
    __call__ 메서드의 반환 값이 필요할 땐, user_info: User = Depends(AuthenticationChecker(role=["admin", "examinee"])) 같이 사용 됩니다..
    만약 필요하지 않다면 @router.post("/url", dependencies=[Depends(AuthenticationChecker(role=["admin"]))]) 와 같이 사용 됩니다.
    """

    allowed_roles: List[Literal["examinee", "admin", "supervisor"]]

    def __init__(self, role: List[Literal["examinee", "admin", "supervisor"]]):
        self.allowed_roles = role
        return

    async def __call__(self, request: Request):
        jwt_token = request.cookies.get("jwt_token")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="Not authenticated, token not found")

        payload = await decode_jwt_token(jwt_token)
        if payload.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        user : User | None = await user_crud.get_by({"id" : payload.sub, "role" : payload.role})
        if not user:
            raise HTTPException(status_code=403, detail="not exist")
        return user

async def create_examinees_from_csv(csv_content: str) -> list[User]:
    """
    CSV 파일 내용을 읽어 User 객체 리스트를 생성합니다.
    CSV 파일에는 'email'과 'name' 열이 포함되어야 합니다.
    """
    users = []
    csv_file = StringIO(csv_content)
    reader = csv.DictReader(csv_file)

    for row in reader:
        if 'email' in row and 'name' in row:
            user = User(
                email=row['email'],
                name=row['name'],
                role="examinee",
                pwd=str(uuid.uuid4())
            )
            users.append(user)

    return users
