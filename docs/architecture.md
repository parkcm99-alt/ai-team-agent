# 아키텍처

이 문서는 AI 팀 에이전트 시스템의 초기 구조와 역할 경계를 설명합니다. 현재 버전은 구현보다 책임 분리, 출력 언어 정책, 향후 연동 지점을 명확히 하는 데 초점을 둡니다.

## 설계 원칙

- 에이전트별 책임을 작게 유지합니다.
- 내부 프롬프트와 명령 체계는 영어로 유지합니다.
- 사용자에게 보이는 모든 산출물은 한국어로 제공합니다.
- 외부 API는 승인된 설계와 테스트 자료가 준비된 뒤 연결합니다.
- 실제 발송, 게시, 알림 작업은 사용자 승인 없이는 수행하지 않습니다.

## 구성 요소

| 영역 | 경로 | 책임 |
| --- | --- | --- |
| Supervisor Agent | `agents/supervisor` | 작업 분배, 정책 적용, 결과 통합 |
| Assistant Agent | `agents/assistant` | 일반 요청 처리, 사용자 의도 정리, 초안 작성 |
| Document Agent | `agents/document` | 문서 작성, 요약, 구조화 |
| Communication Agent | `agents/communication` | 이메일, 메신저, 알림 흐름 준비 |
| Workflow Agent | `agents/workflow` | 작업 상태, 순서, 반복 프로세스 관리 |
| Harness Agent | `agents/harness` | 테스트 케이스, 평가, 회귀 검증 |
| Instagram Agent | `agents/instagram` | Instagram 콘텐츠 준비와 승인 흐름 |
| Templates | `templates` | 한국어 사용자 출력 템플릿 |
| Harness Tests | `tests/harness` | 하네스 테스트 케이스 |
| Replay Tests | `tests/harness/replay` | 실패 사례 재실행 테스트 |
| Checklist Tests | `tests/harness/checklists` | 체크리스트 적용 검증 |
| Golden Examples | `examples/golden` | 기대 출력 예시 |
| Failure Cases | `examples/failure` | 실패, 위험, 회귀 예시 |
| Harness Engineering | `harness` | 체크리스트, 실패 사례, 골든 예시, 리플레이 계획, 릴리스 게이트 |
| Documentation | `docs` | 사용자-facing 문서 |

## 개념적 흐름

```text
User Request
  -> Supervisor Agent
  -> Specialist Agent
  -> Harness Agent review when needed
  -> 한국어 사용자 요약
```

Supervisor Agent는 요청을 해석하고 적절한 전문 에이전트로 나눕니다. 전문 에이전트는 내부 지침과 시스템 프롬프트를 영어로 유지하되, 사용자에게 전달되는 결과는 한국어로 생성합니다. Harness Agent는 구현 이후 테스트와 회귀 검증을 담당합니다.

## 데이터와 출력 정책

- 내부 상태 키, enum, 명령어 이름은 영어를 사용합니다.
- 사용자 설명, 보고서 본문, 알림 문구, 요약문은 한국어를 사용합니다.
- 외부 서비스 데이터는 아직 수집하지 않습니다.
- 테스트 데이터는 실제 개인정보나 실계정 데이터를 포함하지 않는 샘플로 시작합니다.

## TODO

### Google Sheets

- 작업 상태, 보고서, 에이전트 결과를 기록할 시트 스키마를 정의합니다.
- 읽기/쓰기 권한과 승인 범위를 문서화합니다.
- 연결 전 모의 데이터와 골든 예시를 만듭니다.
- Google Sheets 쓰기 작업은 자동 실행하면 안 됩니다.
- Google Sheets 쓰기 작업은 명시적인 사용자 승인 이후에만 실행할 수 있습니다.
- 쓰기 전에는 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값을 한국어로 보여줘야 합니다.
- 쓰기 후에는 기록된 값을 다시 확인하고, 검증 결과를 한국어로 보고해야 합니다.

### Gmail

- 수신함 요약, 답장 초안, 후속 조치 추출 흐름을 정의합니다.
- 실제 발송은 사용자 승인 이후에만 가능하도록 설계합니다.
- 메일 샘플 기반 실패 케이스를 추가합니다.

### Slack

- 채널 요약, DM 답장 초안, 알림 우선순위 기준을 정의합니다.
- 게시 전 승인 정책을 명확히 합니다.
- 메시지 스레드 샘플과 하네스 테스트를 추가합니다.

### Telegram

- 봇 명령어와 이벤트 형식을 영어로 정의합니다.
- 사용자에게 표시되는 봇 응답은 한국어로 유지합니다.
- 토큰과 채팅 ID는 환경 변수로 관리하는 방식을 설계합니다.
- 알림 정책이 완전히 정의되기 전까지 Telegram 알림은 명시적인 사용자 승인이 필요합니다.
- MVP 단계에서는 어떤 외부 알림도 자동 전송하지 않습니다.
- Telegram은 사용자 승인 후에만 초안 알림, 승인 요청, 개인 보고 용도로 사용할 수 있습니다.

### Instagram

- 콘텐츠 캘린더, 캡션 초안, 해시태그 제안 범위를 정의합니다.
- 자동 게시 없이 승인 기반 게시 흐름부터 설계합니다.
- 이미지와 영상 자산의 검증 규칙을 추가합니다.

### Reporting

- 일간/주간 보고서 섹션과 공통 상태값을 정의합니다.
- 여러 에이전트의 작업 결과를 한국어 요약으로 통합하는 규칙을 만듭니다.
- 골든 예시와 실패 케이스를 먼저 작성한 뒤 생성 로직을 구현합니다.
