# Communication Agent

Communication Agent는 이메일, 비즈니스 메시지, 파트너 커뮤니케이션을 한국어로 요약하고 답장 초안을 준비하는 에이전트입니다.

## 현재 상태

- 기본 시스템 프롬프트와 MVP 템플릿이 준비되어 있습니다.
- Gmail, Slack, Telegram API 연결은 없습니다.
- 실제 발송이나 게시 기능은 없습니다.
- 이메일 발송, Slack/Telegram 알림, Google Sheets 쓰기는 수행하지 않습니다.
- 사용자 검토 가능한 초안과 구조화 요약만 생성합니다.

## 출력 형식

- 제목
- 원문 요약
- 핵심 요청사항
- 상대방 의도
- 필요한 다음 액션
- 답장 초안
- 확인이 필요한 부분
- 위험 요소
- 승인 필요 여부

## 실행 원칙

- 사용자에게 보이는 모든 출력은 한국어로 작성합니다.
- 수신자, 회사명, 마감일, 금액, 약속, 법적/권리 이슈가 불명확하면 `확인 필요`로 표시합니다.
- 답장 초안은 정중한 한국어로 작성합니다.
- 외부 발송이나 알림 전송 전 반드시 사용자 검토가 가능해야 합니다.

## 로컬 MVP 러너 실행

커뮤니케이션 입력 예시를 구조화된 한국어 요약과 답장 초안으로 변환하려면 프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/communication/communication_agent_runner.py
```

러너는 `examples/communication_inputs`의 Markdown 입력을 읽고 `examples/communication_outputs`에 결과를 생성합니다. 외부 LLM API, 이메일 발송, Slack/Telegram 알림, Google Sheets 쓰기는 실행하지 않습니다.

생성된 출력은 다음 명령어로 검증합니다.

```bash
python3 tests/harness/communication_workflow_runner.py
```

## 다음 작업

- 채널별 읽기/쓰기 권한 범위를 정의합니다.
- 사용자 승인 흐름을 설계합니다.
- 커뮤니케이션 샘플과 실패 케이스를 추가합니다.
