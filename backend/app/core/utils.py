from datetime import datetime, timedelta, UTC
import jwt, os
from typing import List, Literal
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from backend.app.db import user_crud, User

load_dotenv()
JWT_SECRET: str = os.getenv("JWT_SECRET")


def create_jwt(user_id: str, role: str, expires_delta: timedelta) -> tuple[str, datetime]:
    """JWT를 생성하고 만료 시간을 반환합니다."""
    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token, expire


class UserInfo(BaseModel):

    user_id: str
    user_role: Literal["examinee", "admin", "supervisor"]


class AuthenticationChecker:
    """
    __call__ 메서드의 반환 값이 필요할 땐, uid: str = Depends(AuthenticationChecker(role=["admin", "examinee"])) 같이 사용 됩니다..
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

        try:
            payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])

            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                raise HTTPException(status_code=401, detail="Token has expired")

            user_id: str = payload.get("sub")
            user_role: str = payload.get("role")

            if user_role not in self.allowed_roles:
                raise HTTPException(status_code=403, detail="Permission denied")
            user : User | None = await user_crud.get_by({"user_id" : user_id, "role" : user_role})
            if not user:
                raise HTTPException(status_code=403, detail="not exist")
            return UserInfo(user_id=user_id, user_role=user_role)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

