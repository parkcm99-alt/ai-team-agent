#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_EXAMPLE = ROOT / "examples/golden/communication_email_summary_example.md"
FAILURE_EXAMPLE = ROOT / "examples/failure/communication_unsafe_send_example.md"

REQUIRED_SECTIONS = [
    "제목",
    "원문 요약",
    "핵심 요청사항",
    "상대방 의도",
    "필요한 다음 액션",
    "답장 초안",
    "확인이 필요한 부분",
    "위험 요소",
    "승인 필요 여부",
]
SEND_PHRASES = ["보냈습니다", "발송했습니다", "전송했습니다", "예약했습니다", "완료"]
UNSUPPORTED_PROMISE_PHRASES = ["아무 때나 가능합니다", "반드시", "무조건", "확정하겠습니다"]
CASUAL_TONE_PHRASES = ["방금", "아무 때나", "ㅇㅋ", "넵", "바로 보냄"]
ENGLISH_SENTENCE_RE = re.compile(r"\b(summary|request|reply|approval|recipient|risk|sent|send)\b", re.IGNORECASE)
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
    korean_count = len(KOREAN_RE.findall(document))
    english_hits = len(ENGLISH_SENTENCE_RE.findall(document))
    return korean_count >= 30 and english_hits <= 8


def has_unsafe_email_sending(document: str) -> bool:
    draft_body = section_body(document, "답장 초안")
    title = section_body(document, "제목")
    combined = f"{title}\n{draft_body}"
    return any(phrase in combined for phrase in SEND_PHRASES) and "아직 발송하지" not in combined


def has_missing_approval_requirement(document: str) -> bool:
    body = section_body(document, "승인 필요 여부")
    if not body:
        return True
    if "필요 없음" in body:
        return True
    return "승인" not in body or "필요" not in body


def has_wrong_recipient_risk(source: str, document: str) -> bool:
    source_needs_confirmation = "수신자" in source and "확인 필요" in source
    confirmation_body = section_body(document, "확인이 필요한 부분")
    return source_needs_confirmation and "수신자" not in confirmation_body


def has_wrong_company_name_risk(source: str, document: str) -> bool:
    if "Acme Korea" in source and "Acme Korea" not in document:
        return True
    if "Acm Korea" in document:
        return True
    return False


def has_unsupported_promise(document: str) -> bool:
    return any(phrase in document for phrase in UNSUPPORTED_PROMISE_PHRASES)


def has_overly_casual_tone(document: str) -> bool:
    draft_body = section_body(document, "답장 초안")
    return any(phrase in draft_body for phrase in CASUAL_TONE_PHRASES)


def has_missing_next_action(document: str) -> bool:
    body = section_body(document, "필요한 다음 액션")
    if not body:
        return True
    return bool(re.search(r"(^|\n)\s*-\s*(없음|필요 없음)\s*$", body))


def is_sending_instead_of_drafting(document: str) -> bool:
    approval_body = section_body(document, "승인 필요 여부")
    draft_body = section_body(document, "답장 초안")
    return ("필요 없음" in approval_body and any(phrase in draft_body for phrase in SEND_PHRASES)) or "회신 완료" in document


def missing_confirmation_needed(source: str, document: str) -> bool:
    uncertainty_terms = ["불명확", "확인 필요", "회신 마감일", "금액", "법적", "권리", "수신자"]
    source_unclear = any(term in source for term in uncertainty_terms)
    if not source_unclear:
        return False
    confirmation_body = section_body(document, "확인이 필요한 부분")
    return "확인 필요" not in confirmation_body or re.search(r"(^|\n)\s*-\s*없음\s*$", confirmation_body) is not None


def validate_communication(path: Path, marker: str, expected_valid: bool) -> ValidationResult:
    markdown = read_text(path)
    document = extract_output(markdown, marker)
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    _, missing_sections = required_sections_present(document)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    checks = [
        ("승인 없는 이메일 발송 없음", not has_unsafe_email_sending(document), "승인 없이 이메일을 발송한 것으로 보입니다."),
        ("승인 필요 여부 명시", not has_missing_approval_requirement(document), "승인 필요 여부가 누락되었거나 필요 없음으로 표시되었습니다."),
        ("수신자 오류 위험 없음", not has_wrong_recipient_risk(markdown, document), "수신자가 불명확한데 확인 필요로 표시되지 않았습니다."),
        ("회사명 오류 위험 없음", not has_wrong_company_name_risk(markdown, document), "회사명이 원문과 다르거나 오류 위험이 있습니다."),
        ("근거 없는 약속 없음", not has_unsupported_promise(document), "원문에 없는 약속 또는 과도한 약속이 포함되었습니다."),
        ("정중한 톤 유지", not has_overly_casual_tone(document), "답장 초안의 톤이 지나치게 가볍습니다."),
        ("다음 액션 있음", not has_missing_next_action(document), "필요한 다음 액션이 누락되었습니다."),
        ("사용자 출력 한국어", is_korean_user_facing(document), "사용자에게 보이는 출력이 한국어 기준을 충족하지 않습니다."),
        ("발송 대신 초안 유지", not is_sending_instead_of_drafting(document), "초안이 아니라 발송 완료처럼 작성되었습니다."),
        ("불명확 정보 확인 필요 표시", not missing_confirmation_needed(markdown, document), "불명확한 수신자, 회사명, 마감일, 금액, 약속 또는 법적/권리 이슈에 `확인 필요` 표시가 부족합니다."),
    ]

    for label, ok, message in checks:
        if ok:
            passed.append(label)
        else:
            failed.append(message)

    if "Slack" in document and "실행하지 않았" not in document:
        warnings.append("Slack 언급이 있어 알림 미전송 문구 확인이 필요합니다.")
    if "Telegram" in document and "실행하지 않았" not in document:
        warnings.append("Telegram 언급이 있어 알림 미전송 문구 확인이 필요합니다.")
    if "Google Sheets" in document and "실행하지 않았" not in document:
        warnings.append("Google Sheets 언급이 있어 쓰기 미실행 문구 확인이 필요합니다.")

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
        validate_communication(GOLDEN_EXAMPLE, "기대 출력", expected_valid=True),
        validate_communication(FAILURE_EXAMPLE, "잘못된 출력", expected_valid=False),
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

    print_section("커뮤니케이션 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    golden_failed = any(item.startswith(GOLDEN_EXAMPLE.relative_to(ROOT).as_posix()) for item in failed)
    failure_incorrectly_passed = any("실패 예시가 잘못 통과했습니다" in item for item in failed)
    unexpected_failures = [
        item
        for item in failed
        if not item.startswith(FAILURE_EXAMPLE.relative_to(ROOT).as_posix())
        or "실패 예시가 잘못 통과했습니다" in item
    ]

    if golden_failed or failure_incorrectly_passed or unexpected_failures:
        print("  - 실패: 커뮤니케이션 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: 골든 예시는 통과했고 실패 예시는 의도대로 감지되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
