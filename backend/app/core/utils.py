from datetime import datetime, timedelta
import jwt, os
from typing import List, Literal

from dotenv import load_dotenv
from fastapi import Request, HTTPException

load_dotenv()
JWT_SECRET: str = os.getenv("JWT_SECRET")


def create_jwt(user_id: str, role: str, expires_delta: timedelta) -> tuple[str, datetime]:
    """JWT를 생성하고 만료 시간을 반환합니다."""
    expire = datetime.now() + expires_delta
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token, expire


class AuthenticationChecker:
    """
    __call__ 메서드의 반환 값이 필요할 땐, uid: str = Depends(AuthenticationChecker(role=["admin", "examinee"])) 같이 사용 됩니다..
    만약 필요하지 않다면 @router.post("/url", dependencies=[Depends(AuthenticationChecker(role=["admin"]))]) 와 같이 사용 됩니다.
    """

    allowed_roles: List[Literal["examinee", "admin", "supervisor"]]

    def __init__(self, role: List[Literal["examinee", "admin", "supervisor"]]):
        self.allowed_roles = role
        return

    def __call__(self, request: Request):
        jwt_token = request.cookies.get("jwt_token")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="Not authenticated, token not found")

        try:
            payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
            user_id: str = payload.get("user_id")
            user_role: str = payload.get("role")

            if user_role not in self.allowed_roles:
                raise HTTPException(status_code=403, detail="Permission denied")

            return user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
