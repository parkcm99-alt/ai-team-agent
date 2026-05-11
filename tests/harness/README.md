# 하네스 테스트 케이스

에이전트 동작을 검증할 하네스 테스트 케이스를 보관하는 디렉터리입니다.

## 구조

- `replay`: 릴리스 전 실패 사례 재실행 테스트를 보관합니다.
- `checklists`: 체크리스트 적용 여부를 검증하는 테스트를 보관합니다.

## 현재 상태

- 테스트 케이스 형식은 아직 정의하지 않았습니다.
- 외부 API를 호출하는 테스트는 추가하지 않습니다.

## 다음 작업

- 입력, 기대 출력, 금지 출력 형식을 정의합니다.
- 한국어 사용자 출력 정책 검증 케이스를 추가합니다.
- Google Sheets, Gmail, Slack, Telegram, Instagram, reporting, notification, sheets_write, email_draft, workflow_instagram별 샘플 케이스를 준비합니다.

## 통합 점검 실행

하네스 정책, 리플레이 데이터셋, 문서 검증, 문서 워크플로, 커뮤니케이션 검증, 커뮤니케이션 워크플로, Email Draft 검증, Sheets Reader 검증, Sheets Write Approval 검증, Workflow Instagram 검증, Assistant Report 검증, Supervisor 라우팅 검증, Notification 초안 검증, Python 문법 검사를 한 번에 확인하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/run_all.py
```

개별 정책 체커만 실행하려면 다음 명령어를 사용합니다.

```bash
python3 tests/harness/policy_checker.py
```

통합 점검은 결과를 한국어로 출력하며, 하위 점검 중 하나라도 실패하면 0이 아닌 종료 코드를 반환합니다.

Supervisor 라우팅 검증만 개별 실행하려면 다음 명령어를 사용합니다.

```bash
python3 agents/supervisor/supervisor_router.py
python3 tests/harness/supervisor_validation_runner.py
```

Notification 초안 검증만 개별 실행하려면 다음 명령어를 사용합니다.

```bash
python3 agents/notification/notification_draft_runner.py
python3 tests/harness/notification_validation_runner.py
```

Email Draft 검증만 개별 실행하려면 다음 명령어를 사용합니다.

```bash
python3 agents/email/email_draft_runner.py
python3 tests/harness/email_draft_validation_runner.py
```

Sheets Write Approval 검증만 개별 실행하려면 다음 명령어를 사용합니다.

```bash
python3 agents/sheets_write/sheets_write_approval_runner.py
python3 tests/harness/sheets_write_approval_validation_runner.py
```

Workflow Instagram 검증만 개별 실행하려면 다음 명령어를 사용합니다.

```bash
python3 agents/workflow/workflow_runner.py
python3 tests/harness/workflow_instagram_validation_runner.py
```
