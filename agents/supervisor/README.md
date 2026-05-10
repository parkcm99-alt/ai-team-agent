# Supervisor Agent

Supervisor Agent는 사용자 요청을 해석하고, 적절한 전문 에이전트로 작업을 나누며, 최종 한국어 결과를 통합하는 역할을 담당합니다.

## 현재 상태

- 로컬 규칙 기반 MVP 라우터가 준비되어 있습니다.
- 외부 API 연결은 없습니다.
- 이메일, Slack, Telegram, Google Sheets, Instagram, Vercel 설정 변경은 실행하지 않습니다.

## 라우팅 대상

- `document`: 회의록, 문서 요약, 액션아이템 추출, 후속 초안 준비
- `communication`: 이메일/비즈니스 메시지 요약, 답장 초안, 승인 요청 초안
- `sheets_reader`: 로컬 CSV 샘플 분석 전용
- `assistant_report`: 로컬 상태 보고서 생성
- `harness`: 정책 점검, 리플레이, 검증, 승인 게이트 확인
- `web_dashboard`: 정적 웹 대시보드 문구와 표시 항목
- `blocked`: 승인 누락, 위험 작업, 불명확하거나 지원하지 않는 요청

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/supervisor/supervisor_router.py
```

입력 샘플은 `examples/supervisor_inputs/sample_user_requests.jsonl`에서 읽고, 라우팅 결과는 `examples/supervisor_outputs/sample_routing_decisions.jsonl`에 저장합니다.

## 출력 형식

구조화된 JSONL 스키마 키는 영어로 유지합니다. 사용자에게 보이는 결정 내용은 한국어로 작성하며 다음 항목을 포함합니다.

- 요청 요약
- 선택된 에이전트
- 판단 이유
- 위험도
- 승인 필요 여부
- 차단 여부
- 다음 실행 제안
- 확인이 필요한 부분

## 승인 게이트

- 승인 없는 이메일 발송 요청은 차단합니다.
- 승인 없는 Slack/Telegram 알림 요청은 차단합니다.
- 승인 없는 Google Sheets 쓰기, 수정, 삭제, 추가, 업데이트 요청은 차단합니다.
- 대상 시트, 탭, 행/열, 원본 값, 제안 값, 사후 검증 계획이 없는 Google Sheets 쓰기 제안은 차단합니다.
- 권리 확인과 명시적 승인이 없는 Instagram 게시 요청은 차단합니다.
- 명시적 승인 없는 외부 API 작업은 차단합니다.
- 불명확하거나 지원하지 않는 요청은 `blocked`로 라우팅하고 확인이 필요한 부분을 제시합니다.

## 다음 작업

- 실제 에이전트 실행 오케스트레이션은 아직 연결하지 않습니다.
- 라우팅 결과를 대시보드와 보고서에 반영하는 방식을 검토합니다.
- 승인 완료 이후에도 외부 실행 전 하네스 검증을 먼저 거치도록 확장합니다.
