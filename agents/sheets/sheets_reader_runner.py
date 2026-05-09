#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "examples/sheets_inputs/sample_play_count_sheet.csv"
OUTPUT_FILE = ROOT / "examples/sheets_outputs/sample_play_count_report.md"
NUMERIC_COLUMNS = {"play_count"}
KEY_COLUMNS = ["date", "track_id", "platform"]
UNCLEAR_MARKER = "확인 필요"


@dataclass
class SheetAnalysis:
    columns: list[str]
    rows: list[dict[str, str]]
    missing_values: list[str]
    duplicate_values: list[str]
    numeric_issues: list[str]
    confirmation_rows: list[str]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return list(reader.fieldnames or []), rows


def row_number(index: int) -> int:
    return index + 2


def is_missing(value: str) -> bool:
    return value.strip() == ""


def is_unclear(value: str) -> bool:
    return UNCLEAR_MARKER in value


def is_valid_number(value: str) -> bool:
    normalized = value.replace(",", "").strip()
    return bool(re.fullmatch(r"\d+(\.\d+)?", normalized))


def analyze_sheet(columns: list[str], rows: list[dict[str, str]]) -> SheetAnalysis:
    missing_values: list[str] = []
    duplicate_values: list[str] = []
    numeric_issues: list[str] = []
    confirmation_rows: list[str] = []
    seen_keys: dict[tuple[str, ...], int] = {}

    for index, row in enumerate(rows):
        row_no = row_number(index)
        row_needs_confirmation: list[str] = []

        for column in columns:
            value = row.get(column, "")
            if is_missing(value):
                missing_values.append(f"{row_no}행 `{column}` 값 누락")
                row_needs_confirmation.append(f"{column}: {UNCLEAR_MARKER}")
            elif is_unclear(value):
                row_needs_confirmation.append(f"{column}: {UNCLEAR_MARKER}")

        for column in NUMERIC_COLUMNS:
            value = row.get(column, "")
            if value and not is_unclear(value) and not is_valid_number(value):
                numeric_issues.append(f"{row_no}행 `{column}` 값 `{value}` 숫자 형식 오류")
                row_needs_confirmation.append(f"{column}: {UNCLEAR_MARKER}")

        key = tuple(row.get(column, "") for column in KEY_COLUMNS)
        if all(key):
            if key in seen_keys:
                first_row = seen_keys[key]
                duplicate_values.append(
                    f"{first_row}행과 {row_no}행의 기준값 중복 의심: {dict(zip(KEY_COLUMNS, key))}"
                )
                row_needs_confirmation.append(f"중복 여부: {UNCLEAR_MARKER}")
            else:
                seen_keys[key] = row_no

        if row_needs_confirmation:
            title = row.get("title") or UNCLEAR_MARKER
            confirmation_rows.append(f"{row_no}행 `{title}`: {', '.join(sorted(set(row_needs_confirmation)))}")

    return SheetAnalysis(
        columns=columns,
        rows=rows,
        missing_values=missing_values,
        duplicate_values=duplicate_values,
        numeric_issues=numeric_issues,
        confirmation_rows=confirmation_rows,
    )


def line_items(items: list[str]) -> str:
    if not items:
        return "- 없음"
    return "\n".join(f"- {item}" for item in items)


def render_report(analysis: SheetAnalysis) -> str:
    columns = ", ".join(analysis.columns) if analysis.columns else UNCLEAR_MARKER
    total_rows = len(analysis.rows)
    issue_count = len(analysis.missing_values) + len(analysis.duplicate_values) + len(analysis.numeric_issues)
    next_steps = [
        "누락값이 있는 행은 원본 출처를 확인한 뒤 수동으로 검토합니다.",
        "중복 의심 행은 같은 날짜, 트랙 ID, 플랫폼 기준으로 실제 중복인지 확인합니다.",
        "숫자 형식 오류는 쉼표, 문자 혼입, 단위 표기를 확인한 뒤 정리합니다.",
        "쓰기 작업이 필요하면 별도 승인 게이트를 먼저 통과해야 합니다.",
    ]

    if issue_count == 0:
        next_steps = ["현재 샘플에서는 즉시 확인할 위험 항목이 없습니다.", "그래도 실제 시트 쓰기 전에는 별도 승인 게이트가 필요합니다."]

    return f"""# Sheets Reader Agent Report

### 제목

재생 수 샘플 CSV 읽기 전용 검토 리포트

### 데이터 요약

로컬 CSV 샘플 `examples/sheets_inputs/sample_play_count_sheet.csv`를 읽기 전용으로 분석했습니다. 총 {total_rows}개 데이터 행과 {len(analysis.columns)}개 컬럼을 확인했습니다. 누락값, 중복 의심값, 숫자 형식 오류를 점검했으며 쓰기 작업은 수행하지 않았습니다.

### 컬럼 목록

- {columns}

### 총 행 수

- {total_rows}행

### 누락값

{line_items(analysis.missing_values)}

### 중복 의심값

{line_items(analysis.duplicate_values)}

### 숫자 형식 오류

{line_items(analysis.numeric_issues)}

### 확인이 필요한 행

{line_items(analysis.confirmation_rows)}

### 다음 제안

{line_items(next_steps)}

### 쓰기 작업 여부: 수행하지 않음

- Google Sheets API에 연결하지 않았습니다.
- Google 인증 정보를 사용하지 않았습니다.
- 스프레드시트 쓰기, 수정, 삭제, 추가, 업데이트를 수행하지 않았습니다.
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if not INPUT_FILE.is_file():
        print("- Sheets Reader 실행 결과")
        print(f"  - 실패: 입력 파일이 없습니다: {INPUT_FILE.relative_to(ROOT)}")
        return 1

    columns, rows = read_csv(INPUT_FILE)
    analysis = analyze_sheet(columns, rows)
    report = render_report(analysis)
    write_text(OUTPUT_FILE, report)

    print("- Sheets Reader 실행 결과")
    print(f"  - 처리한 샘플 파일: {INPUT_FILE.relative_to(ROOT)}")
    print(f"  - 생성된 리포트: {OUTPUT_FILE.relative_to(ROOT)}")
    print("- 최종 판단")
    print("  - 통과: 로컬 CSV 읽기 전용 분석을 완료했습니다. 외부 API 연결과 쓰기 작업은 수행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
