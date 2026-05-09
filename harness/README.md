# 하네스 엔지니어링 레이어

이 디렉터리는 에이전트 출력이 릴리스되기 전에 검증해야 하는 체크리스트, 실패 사례, 골든 예시, 리플레이 계획, 릴리스 게이트 기준을 보관합니다.

## 구조

```text
harness
├── checklists
├── failure_cases
├── golden_examples
├── replay_tests
└── release_gate.md
```

## 포함 항목

- `replay_tests`: 릴리스 전에 실패 사례를 재실행하는 절차를 정의합니다.
- `checklists`: 출력 유형별 검증 항목을 정의합니다.
- `failure_cases`: 반복되면 안 되는 실패 사례를 보관합니다.
- `golden_examples`: 기대 품질을 보여주는 좋은 예시를 보관합니다.
- `release_gate.md`: `blocked`, `draft_only`, `ready_for_approval` 판정 기준을 정의합니다.
- `approval_gates`: 이메일 발송, Google Sheets 쓰기, Slack/Telegram 알림, Instagram 게시의 승인 조건을 문서화합니다.

## 원칙

- 사용자에게 보이는 설명, 요약, 알림, 보고서는 한국어여야 합니다.
- 내부 키, 스키마 이름, 상태값은 영어를 사용할 수 있습니다.
- 외부 API 쓰기, 발송, 게시, 알림은 기본적으로 차단합니다.
- 사용자 승인 전에는 이메일, Google Sheets 쓰기, Slack/Telegram 알림, Instagram 게시를 실행하지 않습니다.
- 실패 사례는 릴리스 전 반드시 재실행하고, 동일 유형의 회귀가 없는지 확인합니다.
