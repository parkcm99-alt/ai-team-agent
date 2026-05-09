#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DOC = ROOT / "examples/golden/document_meeting_note_example.md"
FAILURE_DOC = ROOT / "examples/failure/document_missing_action_items_example.md"

REQUIRED_SECTIONS = [
    "제목",
    "요약",
    "주요 논의 내용",
    "결정 사항",
    "액션아이템",
    "담당자",
    "마감일",
    "리스크",
    "다음 제안",
    "확인이 필요한 부분",
]
OVERCONFIDENT_PHRASES = [
    "바로 진행하면 됩니다",
    "무조건",
    "반드시 성공",
    "확실합니다",
    "리스크는 없습니다",
]
ENGLISH_SENTENCE_RE = re.compile(r"\b(the|summary|action|decision|risk|next|owner|deadline)\b", re.IGNORECASE)
KOREAN_RE = re.compile(r"[가-힣]")


@dataclass
class ValidationResult:
    name: str
    passed: list[str]
    failed: list[str]
    warnings: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_output(markdown: str, marker: str) -> str:
    marker_heading = f"## {marker}"
    marker_index = markdown.find(marker_heading)
    if marker_index == -1:
        return markdown
    output_start = markdown.find("\n", marker_index)
    if output_start == -1:
        return ""
    rest = markdown[output_start + 1 :]
    next_heading = re.search(r"\n## [^\n]+", rest)
    if not next_heading:
        return rest.strip()
    return rest[: next_heading.start()].strip()


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


def is_korean_user_facing(document: str) -> bool:
    # Korean examples may include product names and English service names, but should contain substantial Korean text.
    korean_count = len(KOREAN_RE.findall(document))
    english_policy_hits = len(ENGLISH_SENTENCE_RE.findall(document))
    return korean_count >= 30 and english_policy_hits <= 6


def has_missing_action_items(document: str) -> bool:
    body = section_body(document, "액션아이템")
    if not body:
        return True
    if re.search(r"(^|\n)\s*[-|]\s*없음", body):
        return True
    return "확인 필요" not in body and "|" not in body and len(body.strip()) < 10


def has_missing_decisions(document: str) -> bool:
    body = section_body(document, "결정 사항")
    if not body:
        return True
    return bool(re.search(r"(^|\n)\s*[-|]\s*(없음|확인 필요)\s*$", body))


def has_wrong_company_name_risk(source: str, document: str) -> bool:
    if "Acme Korea" in source and "Acme Korea" not in document:
        return True
    if "Acm Korea" in document:
        return True
    return False


def has_wrong_date_risk(source: str, document: str) -> bool:
    source_dates = set(re.findall(r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일", source))
    doc_dates = set(re.findall(r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일", document))
    if source_dates and not source_dates.issubset(doc_dates):
        return True
    if "2026년 5월 8일" in document:
        return True
    return False


def has_unsupported_assumptions(document: str) -> bool:
    risky_phrases = ["확정되었습니다", "검증되었습니다", "완료되었습니다", "문제 없습니다"]
    return any(phrase in document for phrase in risky_phrases)


def has_overconfident_recommendation(document: str) -> bool:
    body = section_body(document, "다음 제안")
    return any(phrase in body for phrase in OVERCONFIDENT_PHRASES)


def missing_confirmation_needed(source: str, document: str) -> bool:
    uncertainty_terms = ["불명확", "확인되지", "후속 작업", "숫자", "마감일", "담당자"]
    source_unclear = any(term in source for term in uncertainty_terms)
    if not source_unclear:
        return False
    confirmation_body = section_body(document, "확인이 필요한 부분")
    combined = f"{document}\n{confirmation_body}"
    return "확인 필요" not in combined or re.search(r"(^|\n)\s*-\s*없음\s*$", confirmation_body) is not None


def validate_document(path: Path, marker: str, expected_valid: bool) -> ValidationResult:
    markdown = read_text(path)
    document = extract_output(markdown, marker)
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    present_sections, missing_sections = required_sections_present(document)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    checks = [
        ("액션아이템 누락 없음", not has_missing_action_items(document), "액션아이템이 누락되었거나 `없음`으로 표시되었습니다."),
        ("결정 사항 누락 없음", not has_missing_decisions(document), "결정 사항이 누락되었거나 불명확합니다."),
        ("회사명 오류 위험 없음", not has_wrong_company_name_risk(markdown, document), "회사명이 원문과 다르거나 오류 위험이 있습니다."),
        ("날짜 오류 위험 없음", not has_wrong_date_risk(markdown, document), "날짜가 원문과 다르거나 누락되었습니다."),
        ("근거 없는 가정 없음", not has_unsupported_assumptions(document), "근거 없는 확정 표현이 있습니다."),
        ("사용자 출력 한국어", is_korean_user_facing(document), "사용자에게 보이는 출력이 한국어 기준을 충족하지 않습니다."),
        ("과신 추천 없음", not has_overconfident_recommendation(document), "다음 제안에 과신 표현이 있습니다."),
        ("불명확 정보 확인 필요 표시", not missing_confirmation_needed(markdown, document), "불명확한 담당자, 마감일, 회사명 또는 숫자에 `확인 필요` 표시가 부족합니다."),
    ]

    for label, ok, message in checks:
        if ok:
            passed.append(label)
        else:
            failed.append(message)

    if "이메일 발송" in document and "실행하지 않았" not in document:
        warnings.append("이메일 발송 언급이 있어 외부 실행 금지 문구 확인이 필요합니다.")
    if "Google Sheets 쓰기" in document and "실행하지 않았" not in document:
        warnings.append("Google Sheets 쓰기 언급이 있어 외부 실행 금지 문구 확인이 필요합니다.")
    if "Slack/Telegram 알림" in document and "실행하지 않았" not in document:
        warnings.append("Slack/Telegram 알림 언급이 있어 외부 실행 금지 문구 확인이 필요합니다.")

    if expected_valid and failed:
        failed.insert(0, "골든 예시가 검증에 실패했습니다.")
    if not expected_valid and not failed:
        failed.append("실패 예시가 잘못 통과했습니다.")
    elif not expected_valid and failed:
        passed.append("실패 예시를 의도대로 감지했습니다.")

    return ValidationResult(path.relative_to(ROOT).as_posix(), passed, failed, warnings)


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if items:
        for item in items:
            print(f"  - {item}")
    else:
        print("  - 없음")


def main() -> int:
    results = [
        validate_document(GOLDEN_DOC, "기대 출력", expected_valid=True),
        validate_document(FAILURE_DOC, "잘못된 출력", expected_valid=False),
    ]

    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    report: list[str] = []

    for result in results:
        report.append(f"{result.name}: 통과 {len(result.passed)}개, 실패 {len(result.failed)}개, 경고 {len(result.warnings)}개")
        passed.extend(f"{result.name}: {item}" for item in result.passed)
        failed.extend(f"{result.name}: {item}" for item in result.failed)
        warnings.extend(f"{result.name}: {item}" for item in result.warnings)

    print_section("문서 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    golden_failed = any(item.startswith(GOLDEN_DOC.relative_to(ROOT).as_posix()) for item in failed)
    failure_incorrectly_passed = any("실패 예시가 잘못 통과했습니다" in item for item in failed)
    unexpected_failures = [
        item
        for item in failed
        if not item.startswith(FAILURE_DOC.relative_to(ROOT).as_posix())
        or "실패 예시가 잘못 통과했습니다" in item
    ]

    if golden_failed or failure_incorrectly_passed or unexpected_failures:
        print("  - 실패: 문서 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: 골든 예시는 통과했고 실패 예시는 의도대로 감지되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
