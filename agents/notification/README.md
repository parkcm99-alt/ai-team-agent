# Notification Draft Agent

Notification Draft Agent는 Slack과 Telegram에 보낼 수 있는 메시지의 **초안만** 작성하는 로컬 MVP입니다.

## 현재 상태

- Slack 상태 요약 초안을 생성합니다.
- Telegram 긴급 알림 초안을 생성합니다.
- 승인 요청 초안과 일일 상태 보고 초안을 작성합니다.
- Slack/Telegram API는 연결하지 않았습니다.
- 실제 알림 발송은 수행하지 않습니다.

## 안전 정책

- Slack 메시지를 보내지 않습니다.
- Telegram 메시지를 보내지 않습니다.
- 외부 API를 연결하지 않습니다.
- 환경 변수, 토큰, 인증 정보를 추가하지 않습니다.
- 모든 초안은 `승인 필요 여부: 필요`로 표시합니다.
- 모든 초안은 `발송 여부: 발송하지 않음`으로 표시합니다.
- 수신자, 채널, 긴급도, 승인 담당자, 마감일, 외부 실행 여부가 불명확하면 `확인 필요`로 표시합니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/notification/notification_draft_runner.py
```

입력 파일:

```text
examples/notification_inputs/sample_status_report_raw.md
```

출력 파일:

```text
examples/notification_outputs/sample_slack_status_draft.md
examples/notification_outputs/sample_telegram_alert_draft.md
```

검증 명령어:

```bash
python3 tests/harness/notification_validation_runner.py
```

## 출력 형식

- 제목
- 채널 유형
- 메시지 목적
- 초안 본문
- 승인 필요 여부
- 발송 여부
- 확인이 필요한 부분
- 위험 요소
