#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_FILE = ROOT / "reports/daily_status_report.md"
REQUIRED_SECTIONS = [
    "제목",
    "오늘의 전체 상태",
    "완료된 작업",
    "에이전트별 상태",
    "하네스 점검 결과",
    "Supervisor 라우팅 결과",
    "최근 커밋 요약",
    "남은 리스크",
    "다음 추천 작업",
    "승인 필요 항목",
    "외부 실행 여부",
]
KOREAN_RE = re.compile(r"[가-힣]")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    return len(KOREAN_RE.findall(document)) >= 120


def has_not_performed(body: str, label: str) -> bool:
    pattern = rf"{re.escape(label)}\s*:\s*수행하지 않음"
    return re.search(pattern, body) is not None


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

    if not REPORT_FILE.is_file():
        failed.append(f"보고서 파일이 없습니다: {REPORT_FILE.relative_to(ROOT)}")
        print_section("Assistant Report 검증 결과", [])
        print_section("통과 항목", passed)
        print_section("실패 항목", failed)
        print_section("경고 항목", warnings)
        print("- 최종 판단")
        print("  - 실패: 필수 보고서 파일이 없습니다.")
        return 1

    report = read_text(REPORT_FILE)
    _, missing_sections = required_sections_present(report)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    if is_korean_report(report):
        passed.append("보고서가 한국어 기준을 충족합니다.")
    else:
        failed.append("보고서의 한국어 내용이 부족합니다.")

    external_body = section_body(report, "외부 실행 여부")
    external_checks = [
        ("이메일 발송", has_not_performed(external_body, "이메일 발송")),
        ("Slack/Telegram 알림", has_not_performed(external_body, "Slack/Telegram 알림")),
        ("Google Sheets 쓰기 작업", has_not_performed(external_body, "Google Sheets 쓰기 작업")),
        ("Instagram 게시", has_not_performed(external_body, "Instagram 게시")),
    ]
    for label, ok in external_checks:
        if ok:
            passed.append(f"{label} 미수행이 명시되어 있습니다.")
        else:
            failed.append(f"{label} 미수행 문구가 부족합니다.")

    banned_phrases = ["발송했습니다", "알림을 보냈습니다", "쓰기 완료", "게시했습니다", "외부 API 호출: 수행함"]
    if any(phrase in report for phrase in banned_phrases):
        failed.append("외부 실행을 수행한 것으로 보이는 문구가 있습니다.")
    else:
        passed.append("외부 실행 수행 문구가 없습니다.")

    supervisor_body = section_body(report, "Supervisor 라우팅 결과")
    supervisor_terms = [
        "총 요청 수",
        "차단된 요청 수",
        "승인 필요 요청 수",
        "라우팅 대상 에이전트 목록",
        "위험 작업 차단 요약",
        "확인이 필요한 요청 요약",
        "외부 실행 여부: 수행하지 않음",
    ]
    missing_supervisor_terms = [term for term in supervisor_terms if term not in supervisor_body]
    if missing_supervisor_terms:
        failed.append(f"Supervisor 라우팅 결과 내용이 부족합니다: {', '.join(missing_supervisor_terms)}")
    else:
        passed.append("Supervisor 라우팅 결과가 보고서에 포함되어 있습니다.")

    risks_body = section_body(report, "남은 리스크")
    if "리스크" in risks_body or "연동" in risks_body or "승인" in risks_body:
        passed.append("남은 리스크가 포함되어 있습니다.")
    else:
        failed.append("남은 리스크 내용이 부족합니다.")

    next_body = section_body(report, "다음 추천 작업")
    if "제안" in next_body or "추천" in next_body or "확정" in next_body:
        passed.append("다음 추천 작업이 포함되어 있습니다.")
    else:
        failed.append("다음 추천 작업 내용이 부족합니다.")

    approval_body = section_body(report, "승인 필요 항목")
    approval_terms = ["이메일", "Slack", "Telegram", "Google Sheets", "Instagram", "승인"]
    if all(term in approval_body for term in approval_terms):
        passed.append("승인 필요 항목이 포함되어 있습니다.")
    else:
        failed.append("승인 필요 항목이 부족합니다.")

    report_items = [
        f"{REPORT_FILE.relative_to(ROOT)}: 통과 {len(passed)}개, 실패 {len(failed)}개, 경고 {len(warnings)}개"
    ]
    print_section("Assistant Report 검증 결과", report_items)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: Assistant Report 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: Assistant Report가 상태 보고서 검증 기준을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
