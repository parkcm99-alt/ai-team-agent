# Document Agent

Document Agent는 문서 작성, 요약, 구조화, 보고서 초안 생성을 담당합니다.

## 현재 상태

- 기본 시스템 프롬프트와 로컬 규칙 기반 MVP 러너가 준비되어 있습니다.
- 외부 LLM API, 이메일 발송, Google Sheets 쓰기, Slack/Telegram 알림은 연결하지 않았습니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행하면 `examples/document_inputs`의 Markdown 입력을 읽고 `examples/document_outputs`에 한국어 구조화 요약을 생성합니다.

```bash
python3 agents/document/document_agent_runner.py
```

생성 후 문서 워크플로 검증을 실행합니다.

```bash
python3 tests/harness/document_workflow_runner.py
```

## 다음 작업

- 문서 템플릿 목록을 정의합니다.
- 보고서와 요약문의 한국어 스타일 기준을 정합니다.
- 골든 예시와 실패 케이스를 추가합니다.
