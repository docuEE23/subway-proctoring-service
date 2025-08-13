"""
## 시험 동안 발생한 이벤트 로그를 모아 리포트를 제작 합니다.
### 리포트 제작 요청

url : GET /reports/generate/{exam_id}?user_id={user_id}

backend/app/core 에 있는 AuthenticationChecker 를 사용해서 jwt의 유효성을 판단하세요. 반환 값은 필요 없습니다.

ExamSession 컬렉션에서 exam_id 값이 존재 하는지 확인 합니다. 존재하지 않는다면 에러를 내세요.
exam_id 가 존재하지만 그 ExamSession 컬렉션에 있는 session_status 필드의 값이 'completed', 'archived' 이 아니라면 에러를 내세요.

이제 url query 에 user_id 값이 있는지 확인하세요. 없다면 EvnetLog 컬렉션에 exam_id 를 가진 모든 로그를 모아 보고서를 생성해야 합니다.
user_id 값이 있다면 동일한 exam_id, user_id 를 가진 EvnetLog 만 보고서로 만드시면 됩니다.



시험이 끝나고
"""