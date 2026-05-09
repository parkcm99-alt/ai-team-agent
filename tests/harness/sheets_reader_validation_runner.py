#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "examples/sheets_inputs/sample_play_count_sheet.csv"
REPORT_FILE = ROOT / "examples/sheets_outputs/sample_play_count_report.md"
REQUIRED_SECTIONS = [
    "제목",
    "데이터 요약",
    "컬럼 목록",
    "총 행 수",
    "누락값",
    "중복 의심값",
    "숫자 형식 오류",
    "확인이 필요한 행",
    "다음 제안",
    "쓰기 작업 여부: 수행하지 않음",
]
KOREAN_RE = re.compile(r"[가-힣]")
NUMERIC_COLUMNS = {"play_count"}
KEY_COLUMNS = ["date", "track_id", "platform"]
UNCLEAR_MARKER = "확인 필요"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return list(reader.fieldnames or []), rows


def section_body(document: str, section: str) -> str:
    pattern = re.compile(rf"^### {re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(document)
    if not match:
        return ""
    body_start = match.end()
    next_match = re.search(r"^### .+$", document[body_start:], re.MULTILINE)
    if not next_match:
        return document[body_start:].strip()
    return document[body_start : body_start + next_match.start()].strip()


def required_sections_present(document: str) -> tuple[list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        if re.search(rf"^### {re.escape(section)}\s*$", document, re.MULTILINE):
            present.append(section)
        else:
            missing.append(section)
    return present, missing


def is_korean_report(document: str) -> bool:
    return len(KOREAN_RE.findall(document)) >= 80


def is_valid_number(value: str) -> bool:
    normalized = value.replace(",", "").strip()
    return bool(re.fullmatch(r"\d+(\.\d+)?", normalized))


def detect_missing_values(columns: list[str], rows: list[dict[str, str]]) -> list[str]:
    found: list[str] = []
    for index, row in enumerate(rows, start=2):
        for column in columns:
            if row.get(column, "").strip() == "":
                found.append(f"{index}행 `{column}`")
    return found


def detect_duplicates(rows: list[dict[str, str]]) -> list[str]:
    found: list[str] = []
    seen: dict[tuple[str, ...], int] = {}
    for index, row in enumerate(rows, start=2):
        key = tuple(row.get(column, "").strip() for column in KEY_COLUMNS)
        if not all(key):
            continue
        if key in seen:
            found.append(f"{seen[key]}행과 {index}행")
        else:
            seen[key] = index
    return found


def detect_numeric_issues(rows: list[dict[str, str]]) -> list[str]:
    found: list[str] = []
    for index, row in enumerate(rows, start=2):
        for column in NUMERIC_COLUMNS:
            value = row.get(column, "").strip()
            if value and UNCLEAR_MARKER not in value and not is_valid_number(value):
                found.append(f"{index}행 `{column}`")
    return found


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def main() -> int:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    if not INPUT_FILE.is_file():
        failed.append(f"입력 CSV 파일이 없습니다: {INPUT_FILE.relative_to(ROOT)}")
    if not REPORT_FILE.is_file():
        failed.append(f"리포트 파일이 없습니다: {REPORT_FILE.relative_to(ROOT)}")

    if failed:
        print_section("Sheets Reader 검증 결과", [])
        print_section("통과 항목", passed)
        print_section("실패 항목", failed)
        print_section("경고 항목", warnings)
        print("- 최종 판단")
        print("  - 실패: 필수 파일이 없습니다.")
        return 1

    columns, rows = read_csv_rows(INPUT_FILE)
    report = read_text(REPORT_FILE)

    _, missing_sections = required_sections_present(report)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    if is_korean_report(report):
        passed.append("리포트가 한국어 기준을 충족합니다.")
    else:
        failed.append("리포트의 한국어 내용이 부족합니다.")

    write_body = section_body(report, "쓰기 작업 여부: 수행하지 않음")
    if "수행하지 않았습니다" in write_body and "Google Sheets API에 연결하지 않았습니다" in write_body:
        passed.append("쓰기 작업과 Google Sheets API 연결 미수행이 명시되어 있습니다.")
    else:
        failed.append("쓰기 작업 미수행 또는 Google Sheets API 미연결 문구가 부족합니다.")

    banned_phrases = ["수행했습니다", "업데이트했습니다", "삭제했습니다", "추가했습니다", "append", "update"]
    if any(phrase in write_body for phrase in banned_phrases):
        failed.append("쓰기 작업을 수행한 것으로 오해될 수 있는 문구가 있습니다.")
    else:
        passed.append("쓰기, 수정, 삭제, 추가, 업데이트 수행 문구가 없습니다.")

    missing_values = detect_missing_values(columns, rows)
    missing_body = section_body(report, "누락값")
    if missing_values and all(item in missing_body for item in missing_values):
        passed.append("CSV의 누락값이 리포트에 표시되어 있습니다.")
    elif missing_values:
        failed.append("CSV에 누락값이 있지만 리포트 표시가 부족합니다.")
    else:
        passed.append("CSV에 누락값이 없습니다.")

    duplicates = detect_duplicates(rows)
    duplicate_body = section_body(report, "중복 의심값")
    if duplicates and all(item in duplicate_body for item in duplicates):
        passed.append("CSV의 중복 의심값이 리포트에 표시되어 있습니다.")
    elif duplicates:
        failed.append("CSV에 중복 의심값이 있지만 리포트 표시가 부족합니다.")
    else:
        passed.append("CSV에 중복 의심값이 없습니다.")

    numeric_issues = detect_numeric_issues(rows)
    numeric_body = section_body(report, "숫자 형식 오류")
    if numeric_issues and all(item in numeric_body for item in numeric_issues):
        passed.append("CSV의 숫자 형식 오류가 리포트에 표시되어 있습니다.")
    elif numeric_issues:
        failed.append("CSV에 숫자 형식 오류가 있지만 리포트 표시가 부족합니다.")
    else:
        passed.append("CSV에 숫자 형식 오류가 없습니다.")

    confirmation_body = section_body(report, "확인이 필요한 행")
    if UNCLEAR_MARKER in confirmation_body:
        passed.append("불명확한 값이 `확인 필요`로 표시되어 있습니다.")
    else:
        failed.append("불명확한 값에 `확인 필요` 표시가 부족합니다.")

    report_items = [
        f"{REPORT_FILE.relative_to(ROOT)}: 통과 {len(passed)}개, 실패 {len(failed)}개, 경고 {len(warnings)}개"
    ]
    print_section("Sheets Reader 검증 결과", report_items)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: Sheets Reader 리포트 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: Sheets Reader 리포트가 읽기 전용 검증 기준을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
