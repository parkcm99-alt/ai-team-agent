# Email Draft Agent

Email Draft Agent는 로컬 샘플 이메일만 읽어 한국어 이메일 요약, 답장 초안, 승인 요청서를 생성하는 MVP입니다.

## 현재 범위

- `examples/email_inputs` 아래의 Markdown 이메일 샘플만 읽습니다.
- `examples/email_outputs` 아래에 한국어 Markdown 결과를 생성합니다.
- Gmail API는 연결하지 않습니다.
- 실제 이메일을 발송하지 않습니다.
- Gmail API를 통해 실제 Gmail 초안을 만들지 않습니다.
- 외부 API, 인증 정보, 환경 변수는 사용하지 않습니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/email/email_draft_runner.py
```

생성된 결과를 검증하려면 다음 명령어를 실행합니다.

```bash
python3 tests/harness/email_draft_validation_runner.py
```

## 승인 정책

- 모든 이메일 결과는 검토 가능한 초안입니다.
- 실제 발송 전 명시적인 사용자 승인이 필요합니다.
- 수신자, 회사명, 마감일, 요청 작업, 법적/권리 이슈, 가격, 수량, 약속이 불명확하면 `확인 필요`로 표시합니다.
- `발송 여부: 발송하지 않음`, `승인 필요 여부: 필요`, `Gmail API 연결 여부: 연결하지 않음`을 명시해야 합니다.
