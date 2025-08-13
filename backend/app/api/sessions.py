"""

## 2. 시험 세션 (Sessions) - `api/sessions.py`

### 2.1. 세션 생성 (관리자) (UC-101)
- **Endpoint**: `POST /create_sessions
- **목표**: 관리자가 새로운 시험 세션을 생성합니다.

#### **세부 구현 절차:**
1.  **요청 수신 및 권한 검증**:
    *   `Authorization` 헤더에서 JWT를 추출하고 유효성을 검증합니다. 이 JWT 토큰에는 user_id 와 role 에
    *   토큰의 `role`이 'admin'인지 확인합니다. 'admin'이 아니면 `403 Forbidden` 에러와 `FORBIDDEN_ROLE` 코드를 반환합니다.
2.  **요청 본문 유효성 검사**:
    *   세션 설정에 필요한 정보(e.g., `title`, `description`, `rules`)가 포함되어 있는지 확인합니다.
3.  **세션 데이터 생성**:
    *   세션 ID (UUID)를 생성합니다.
    *   6자리 숫자 또는 영문 조합의 참여 코드(joinCode)를 생성합니다.
    *   이 코드가 현재 활성화된 다른 세션의 코드와 중복되지 않는지 확인하고, 중복 시 다시 생성합니다.
    *   세션 상태를 `draft`로 설정합니다.
4.  **데이터베이스 저장**:
    *   생성된 세션 정보를 `sessions` 컬렉션에 저장합니다.
5.  **응답 반환**:
    *   `201 Created` 상태 코드와 함께 생성된 세션의 정보(session_id, exam_id, )를 반환합니다.
    *   Logs 컬렉션에 `SESSION_CREATE` 감사 로그를 기록합니다.

### 2.2. 응시자 세션 참여 (UC-205)
- **Endpoint**: `POST /sessions/join-examinee`
- **목표**: 응시자가 참여 코드를 사용하여 특정 시험 세션에 입장합니다.

#### **세부 구현 절차:**
1.  **요청 수신 및 본문 검사**:
    *   요청 본문에 `code` (참여 코드)와 `displayName` (응시자 이름)이 있는지 확인합니다. 누락 시 `422` 에러를 반환합니다.
2.  **세션 조회**:
    *   `sessions` 컬렉션에서 전달받은 `code`와 일치하고, 상태가 `Open` 또는 `Running`인 세션을 조회합니다.
    *   세션이 없거나, 참여 코드가 만료되었거나, 최대 사용 횟수를 초과한 경우 `404 Not Found` 에러와 `SESSION_NOT_FOUND` 또는 `CODE_EXPIRED` 코드를 반환합니다.
3.  **응시자 정보 등록**:
    *   `enrollments` 컬렉션에 새로운 응시자 정보를 등록합니다. 이 때, `session_id`, `displayName`, `status` ('waiting') 등의 정보를 포함합니다.
4.  **응시자용 JWT 발급**:
    *   해당 세션에만 접근 가능한 임시 JWT를 발급하거나, 기존 로그인 로직을 활용하여 응시자 정보를 포함한 토큰을 발급합니다.
5.  **응답 반환**:
    *   `200 OK` 상태 코드와 함께 참여하게 될 `sessionId`를 반환합니다.
    *   `SESSION_JOIN` 감사 로그를 기록합니다.

### 2.3. 세션 제어 (감독관) (UC-602)
- **Endpoint**: `POST /sessions/{id}/controls`
- **목표**: 감독관이 시험을 시작, 일시정지, 재개, 종료합니다.

#### **세부 구현 절차:**
1.  **요청 수신 및 권한 검증**:
    *   JWT를 검증하고 `role`이 'supervisor' 또는 'admin'인지 확인합니다.
    *   `X-Session-Id` 헤더가 요청된 `{id}`와 일치하는지 확인합니다.
2.  **세션 상태 전이(State Transition) 검증**:
    *   요청 본문의 `action` (`start`, `pause`, `resume`, `stop`)에 따라 유효한 상태 변경인지 확인합니다. (e.g., `Paused` 상태에서 `pause` 요청 불가)
    *   `Draft` → `Open` → `Running` → `Paused` → `Ended` 순서의 상태 전이를 강제합니다. 역행은 금지됩니다.
    *   유효하지 않은 상태 변경 요청 시, `409 Conflict` 에러와 `INVALID_STATE` 코드를 반환합니다.
3.  **데이터베이스 업데이트**:
    *   `sessions` 컬렉션에서 해당 세션의 `status`를 업데이트합니다.
4.  **실시간 이벤트 전파**:
    *   WebSocket (`/ws/room/{sessionId}`)을 통해 해당 세션의 모든 참여자(응시자, 감독관)에게 `control:apply` 이벤트를 브로드캐스트하여 상태 변경을 알립니다.
5.  **응답 반환**:
    *   `200 OK`와 함께 변경된 세션 상태를 반환합니다.
    *   `EXAM_START`, `EXAM_PAUSE` 등 `EXAM_*` 감사 로그를 기록합니다.

"""