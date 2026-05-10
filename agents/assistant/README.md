# Assistant Agent

Assistant Agent는 일반적인 사용자 요청을 정리하고, 간단한 초안과 실행 가능한 다음 단계를 준비하는 역할을 담당합니다.

## 현재 상태

- 기본 시스템 프롬프트와 로컬 상태 보고서 러너가 준비되어 있습니다.
- 외부 연동은 없습니다.
- 이메일, Slack/Telegram 알림, Google Sheets 쓰기, Instagram 게시를 수행하지 않습니다.

## 로컬 MVP 러너 실행

프로젝트 루트에서 다음 명령어를 실행하면 로컬 git 상태, 최근 커밋, 하네스 점검 결과, Supervisor 라우팅 결과를 바탕으로 한국어 상태 보고서를 생성합니다.

```bash
python3 agents/assistant/assistant_report_runner.py
```

생성된 보고서는 다음 파일에 저장됩니다.

```text
reports/daily_status_report.md
```

보고서 검증은 다음 명령어로 실행합니다.

```bash
python3 tests/harness/assistant_report_validation_runner.py
```

## 보고서 형식

- 제목
- 오늘의 전체 상태
- 완료된 작업
- 에이전트별 상태
- 하네스 점검 결과
- Supervisor 라우팅 결과
- 최근 커밋 요약
- 남은 리스크
- 다음 추천 작업
- 승인 필요 항목
- 외부 실행 여부

## 다음 작업

- 요청 분류 기준을 정의합니다.
- 한국어 응답 형식의 골든 예시를 추가합니다.
- Supervisor 라우팅 결과를 웹 대시보드에 더 자동으로 반영하는 방식을 검토합니다.
