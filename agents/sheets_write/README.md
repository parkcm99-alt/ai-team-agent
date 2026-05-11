# Sheets Write Approval Agent

Sheets Write Approval Agent는 Google Sheets 쓰기 요청을 실제로 실행하지 않고, 먼저 검토 가능한 승인 요청서로 바꾸는 로컬 MVP입니다.

## 현재 상태

- 로컬 JSONL 샘플만 읽습니다.
- Google Sheets API에 연결하지 않습니다.
- Google 인증 정보를 사용하지 않습니다.
- 실제 스프레드시트 쓰기, 수정, 삭제, 추가, 업데이트를 수행하지 않습니다.
- 모든 쓰기 제안은 `승인 필요 여부: 필요` 상태로 표시합니다.
- 위험하거나 정보가 부족한 요청은 `blocked` 또는 `approval_required`로 분류합니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/sheets_write/sheets_write_approval_runner.py
```

입력 파일:

```text
examples/sheets_write_inputs/sample_write_requests.jsonl
```

출력 파일:

```text
examples/sheets_write_outputs/sample_write_approval_report.md
```

검증 명령어:

```bash
python3 tests/harness/sheets_write_approval_validation_runner.py
```

## 승인 요청서 필수 항목

- 제목
- 요청 요약
- 승인 필요 여부
- 실제 쓰기 수행 여부
- 대상 스프레드시트
- 대상 탭
- 대상 행
- 대상 열
- 원본 값
- 제안 값
- 변경 사유
- 위험 요소
- 확인이 필요한 부분
- 사후 검증 계획
- 최종 상태

## 고정 안전 문구

- 승인 필요 여부: 필요
- 실제 쓰기 수행 여부: 수행하지 않음
- Google Sheets API 연결 여부: 연결하지 않음

## 다음 작업

- 실제 Google Sheets 쓰기 연결은 아직 하지 않습니다.
- 향후 연결 전에는 대상 스프레드시트, 탭, 행, 열, 원본 값, 제안 값, 승인 요구, 사후 검증 계획을 먼저 보여주는 승인 게이트를 유지해야 합니다.
