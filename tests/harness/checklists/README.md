# 하네스 체크리스트 테스트

이 디렉터리는 체크리스트가 실제 평가와 릴리스 게이트에 맞게 적용되는지 확인하는 테스트 자료를 보관합니다.

## 목적

- 문서 출력, 커뮤니케이션 초안, 이메일 초안, Google Sheets 쓰기 승인 요청, Slack/Telegram 알림, Instagram 게시, Supervisor 라우팅, Notification 초안 검증 항목을 확인합니다.
- 승인 게이트가 빠진 출력이 `ready_for_approval`로 잘못 분류되지 않도록 막습니다.
- 사용자에게 보이는 설명이 한국어인지 확인합니다.
- 내부 시스템 프롬프트와 스키마 지시가 영어인지 확인합니다.
- 알려진 실패 사례와 유사한 출력이 차단 또는 초안 상태로 낮춰지는지 확인합니다.
- 골든 예시와 비교해 안전한 출력 패턴이 유지되는지 확인합니다.

## 기본 규칙

- 체크리스트 이름과 내부 키는 영어를 사용할 수 있습니다.
- 사용자에게 보이는 검토 결과와 설명은 한국어로 작성합니다.
- 이메일 발송, Google Sheets 쓰기, Slack/Telegram 알림, Instagram 게시 테스트는 실제 외부 작업을 실행하지 않습니다.
- 사용자 승인이 필요한 항목은 초안, 미리보기, 승인 요청 상태로만 검증합니다.
- Google Sheets 쓰기 검증은 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값, 사후 검증 계획을 확인합니다.
- Sheets Write Approval 검증은 실제 쓰기를 수행하지 않고 승인 요청서만 생성하는지 확인합니다.
- Slack/Telegram 검증은 MVP 단계에서 자동 전송이 없는지 확인합니다.
- Notification 검증은 Slack/Telegram 메시지를 실제 발송하지 않고 초안으로만 유지하는지 확인합니다.
- Instagram 검증은 권리 체크리스트와 명시적 사용자 승인이 있는지 확인합니다.

## 릴리스 전 검증 데이터셋

- `examples/failure/sample_failure_cases.jsonl`: 체크리스트가 잡아내야 하는 실패 사례입니다.
- `examples/golden/sample_golden_examples.jsonl`: 체크리스트가 통과시켜야 하는 안전한 예시입니다.

## 문서 검증 실행

문서 에이전트의 Markdown 예시를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/document_validation_runner.py
```

러너는 골든 문서 예시가 통과하는지, 실패 문서 예시가 의도대로 감지되는지 확인합니다.

## 커뮤니케이션 검증 실행

커뮤니케이션 에이전트의 Markdown 예시를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/communication_validation_runner.py
```

러너는 골든 커뮤니케이션 예시가 통과하는지, 실패 커뮤니케이션 예시가 의도대로 감지되는지 확인합니다.

## 커뮤니케이션 워크플로 검증 실행

커뮤니케이션 에이전트의 워크플로 출력 예시 전체를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/communication_workflow_runner.py
```

러너는 `examples/communication_outputs` 아래의 모든 Markdown 출력이 커뮤니케이션 에이전트 형식과 승인 게이트 기준을 만족하는지 확인합니다.

## Sheets Reader 검증 실행

Sheets Reader Agent의 로컬 CSV 읽기 전용 리포트를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/sheets_reader_validation_runner.py
```

러너는 `examples/sheets_outputs/sample_play_count_report.md`가 필수 한국어 섹션, 쓰기 미수행 문구, 누락값, 중복 의심값, 숫자 형식 오류를 올바르게 포함하는지 확인합니다.

## Sheets Write Approval 검증 실행

Sheets Write Approval Agent의 로컬 승인 요청서를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/sheets_write/sheets_write_approval_runner.py
python3 tests/harness/sheets_write_approval_validation_runner.py
```

러너는 골든 승인 요청 예시가 통과하는지, 승인 없는 실제 쓰기 예시가 실패로 감지되는지, 생성된 승인 요청서에 대상 스프레드시트, 탭, 행, 열, 원본 값, 제안 값, 승인 필요 여부, 쓰기 미수행, Google Sheets API 미연결, 사후 검증 계획이 포함되는지 확인합니다.

## Assistant Report 검증 실행

Assistant Report Agent의 로컬 상태 보고서를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 tests/harness/assistant_report_validation_runner.py
```

러너는 `reports/daily_status_report.md`가 필수 한국어 섹션, 외부 실행 미수행 문구, 남은 리스크, 다음 추천 작업, 승인 필요 항목을 포함하는지 확인합니다.

## Supervisor 라우팅 검증 실행

Supervisor Agent의 샘플 요청 라우팅 결과를 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/supervisor/supervisor_router.py
python3 tests/harness/supervisor_validation_runner.py
```

러너는 안전한 요청이 올바른 에이전트로 라우팅되는지, 위험한 외부 실행 요청이 승인 없이 통과하지 않는지, 사용자 표시 결정이 한국어인지 확인합니다.

## Notification 초안 검증 실행

Notification Draft Agent의 Slack/Telegram 초안을 검증하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/notification/notification_draft_runner.py
python3 tests/harness/notification_validation_runner.py
```

러너는 골든 초안이 통과하는지, 위험 발송 예시가 실패로 감지되는지, 생성된 Slack/Telegram 초안에 `승인 필요 여부: 필요`과 `발송 여부: 발송하지 않음`이 포함되어 있는지 확인합니다.

## 관련 문서

- `tests/harness/checklists/assistant_report_validation.md`
- `tests/harness/checklists/document_validation.md`
- `tests/harness/checklists/communication_validation.md`
- `tests/harness/checklists/sheets_reader_validation.md`
- `tests/harness/checklists/sheets_write_approval_validation.md`
- `tests/harness/checklists/supervisor_validation.md`
- `tests/harness/checklists/notification_validation.md`
- `harness/checklists/document_output_validation.md`
- `harness/checklists/email_draft_validation.md`
- `harness/checklists/google_sheets_write_validation.md`
- `harness/checklists/slack_telegram_notification_validation.md`
- `harness/checklists/instagram_publishing_validation.md`
