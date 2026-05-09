# Sheets Reader Agent

Sheets Reader Agent는 로컬 CSV 샘플 파일을 읽고 한국어 검토 리포트를 생성하는 읽기 전용 에이전트입니다.

## 현재 범위

- 로컬 CSV 파일만 분석합니다.
- Google Sheets API에 연결하지 않습니다.
- Google 인증 정보를 사용하지 않습니다.
- 스프레드시트 쓰기, 수정, 삭제, 추가, 업데이트를 수행하지 않습니다.
- 실제 스프레드시트를 생성하거나 변경하지 않습니다.

## 입력 파일

- `examples/sheets_inputs/sample_play_count_sheet.csv`

## 출력 파일

- `examples/sheets_outputs/sample_play_count_report.md`

## 로컬 MVP 러너 실행

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/sheets/sheets_reader_runner.py
```

생성된 리포트는 다음 명령어로 검증합니다.

```bash
python3 tests/harness/sheets_reader_validation_runner.py
```

## 리포트 형식

- 제목
- 데이터 요약
- 컬럼 목록
- 총 행 수
- 누락값
- 중복 의심값
- 숫자 형식 오류
- 확인이 필요한 행
- 다음 제안
- 쓰기 작업 여부: 수행하지 않음

## 안전 원칙

- 사용자에게 보이는 출력은 한국어로 작성합니다.
- 값이 불명확하면 `확인 필요`로 표시합니다.
- 쓰기 작업은 수행하지 않았다고 명시합니다.
